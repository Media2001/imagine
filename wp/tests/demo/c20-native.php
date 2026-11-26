<?php
/** C20: native acceptance probe; every database write is rolled back. No adapter override. */
declare(strict_types=1);
namespace Imagine\Demo\C20;

use Imagine\Site\{MonCompte, Paywall, EnvoiNatif};

function guard(): array
{
    if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
        || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || home_url() !== 'http://192.168.129.32:8085'
        || apply_filters('pre_wp_mail', null, []) !== false
        || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
        || WC()->payment_gateways()->get_available_payment_gateways() !== []
        || wp_using_ext_object_cache()) {
        throw new \RuntimeException('C20 refuses target or external side effects/cache.');
    }
    return get_option('imagine_c09_fixture');
}

function tables(): array
{
    global $wpdb;
    $out = [];
    foreach ($wpdb->get_results('SHOW TABLE STATUS', ARRAY_A) as $row) {
        if (str_starts_with($row['Name'], $wpdb->prefix)) {
            if ($row['Engine'] !== 'InnoDB' || !preg_match('/^[a-zA-Z0-9_]+$/D', $row['Name'])) {
                throw new \RuntimeException('C20 requires transactional tables.');
            }
            $out[] = $row['Name'];
        }
    }
    sort($out);
    return $out;
}

function fingerprint(array $tables): array
{
    global $wpdb;
    $out = [];
    foreach ($tables as $table) {
        $rows = $wpdb->get_results("SELECT * FROM `$table`", ARRAY_A);
        $serialized = array_map('serialize', $rows);
        sort($serialized);
        $out[$table] = ['count' => count($rows), 'sha256' => hash('sha256', serialize($serialized))];
    }
    return $out;
}

function state(string $who, array $fixture): array
{
    global $wpdb;
    $id = (int) $fixture['subscriptions'][$who];
    clean_post_cache($id);
    wp_cache_delete($id, 'posts');
    $s = wcs_get_subscription($id);
    wp_set_current_user((int) $fixture['users'][$who]);
    Paywall::invalidate();
    $data = MonCompte::donnees();
    $m = wc_memberships_get_user_membership($fixture['memberships'][$who]);
    $actions = $wpdb->get_results($wpdb->prepare("SELECT action_id,hook,status,scheduled_date_gmt,args FROM {$wpdb->prefix}actionscheduler_actions WHERE args=%s AND status IN ('pending','in-progress') ORDER BY action_id", wp_json_encode(['subscription_id' => $id])), ARRAY_A);
    $view = EnvoiNatif::calculer('DEMO-2027-T1', EnvoiNatif::releves(), new \DateTimeImmutable('now', new \DateTimeZone('UTC')));
    return ['id' => $id, 'status' => $s->get_status(), 'end' => $s->get_date('end', 'gmt'),
        'next_payment' => $s->get_date('next_payment', 'gmt'), 'manual' => $s->get_requires_manual_renewal(),
        'membership_status' => $m->get_status(), 'membership_end' => $m->get_end_date('mysql', false),
        'access_C06' => Paywall::decision(get_post(get_option('imagine_c08_fixture')['article'])),
        'account_B02' => $data['abonnements'][0], 'shipping_C13' => $view, 'actions' => $actions];
}

global $wpdb;
$f = guard();
$tables = tables();
if (defined('IMAGINE_C20_READ_ONLY') && IMAGINE_C20_READ_ONLY) {
    $out = ['fingerprints' => fingerprint($tables), 'profiles' => []];
    foreach (['A-CARTE', 'A-SEPA4', 'A-VIR', 'A-PAPIER'] as $who) {
        $out['profiles'][$who] = state($who, $f);
    }
    echo wp_json_encode($out);
    return;
}
$before = fingerprint($tables);
$out = ['scope' => 'imagine-test-demo', 'mode' => 'real-native-write-readback-then-rollback', 'cases' => []];
$acceptance = [];
$effects = [];
$http = static function () use (&$effects) { $effects[] = 'http-blocked'; return new \WP_Error('c20_offline'); };
$mail = static function () use (&$effects) { $effects[] = 'mail-blocked'; return false; };
add_filter('pre_http_request', $http, PHP_INT_MAX);
add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
try {
    foreach (['A-CARTE', 'A-SEPA4'] as $who) {
        $wpdb->query('START TRANSACTION');
        $forbidCommit = static function (string $sql): string {
            if (preg_match('/^\s*(COMMIT|START\s+TRANSACTION|BEGIN|ROLLBACK|CREATE|ALTER|DROP|TRUNCATE|RENAME|LOCK\s+TABLE|UNLOCK\s+TABLE|SET\s+autocommit)\b/i', $sql)) {
                throw new \RuntimeException('Implicit or explicit transaction termination refused.');
            }
            return $sql;
        };
        add_filter('query', $forbidCommit, PHP_INT_MAX);
        try {
            $initial = state($who, $f);
            $s = wcs_get_subscription($initial['id']);
            $term = $s->calculate_date('end_of_prepaid_term');
            $s->update_status('pending-cancel', 'C20 fictitious native acceptance probe');
            $cancelled = state($who, $f);
            $s = wcs_get_subscription($initial['id']);
            $canReactivate = $s->can_be_updated_to('active');
            $resumeError = null;
            if ($canReactivate) {
                try {
                    $s->update_status('active', 'C20 native resumption probe');
                } catch (\Throwable $error) {
                    $resumeError = $error->getMessage();
                }
            }
            $resumed = state($who, $f);
            $out['cases'][$who] = ['initial' => $initial, 'native_prepaid_term' => $term,
                'after_pending_cancel' => $cancelled, 'can_resume_before_end' => $canReactivate,
                'after_active' => $resumed];
            $acceptance[$who . ':current_access_unchanged'] = $initial['access_C06'] === $cancelled['access_C06'];
            $acceptance[$who . ':shipping_list_unchanged'] = $initial['shipping_C13'] === $cancelled['shipping_C13'];
            $acceptance[$who . ':numbers_same_B02'] = $initial['account_B02']['premier'] === $cancelled['account_B02']['premier']
                && $initial['account_B02']['dernier'] === $cancelled['account_B02']['dernier']
                && $initial['account_B02']['restants'] === $cancelled['account_B02']['restants'];
            $acceptance[$who . ':native_resumption_dates'] = $resumed['end'] === $initial['end']
                && $resumed['next_payment'] === $initial['next_payment'] && $resumed['status'] === 'active' && $canReactivate;
            if ($who === 'A-SEPA4') {
                $acceptance['A-SEPA4:remaining_instalments_retained'] = $cancelled['next_payment'] === $initial['next_payment'];
                $acceptance['A-SEPA4:remaining_instalment_states_same_B02'] = $cancelled['account_B02']['echeances'] === $initial['account_B02']['echeances'];
            }
        } finally {
            remove_filter('query', $forbidCommit, PHP_INT_MAX);
            $wpdb->query('ROLLBACK');
            wp_cache_flush();
        }
        $after = fingerprint($tables);
        $out['rollback'][$who] = ['before' => $before, 'after' => $after, 'identical' => $before === $after];
        if ($before !== $after) {
            throw new \RuntimeException('Native rollback drift: stop immediately.');
        }
    }
} finally {
    remove_filter('pre_http_request', $http, PHP_INT_MAX);
    remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
    wp_set_current_user(0);
}
$out['acceptance'] = $acceptance;
$out['effects_blocked'] = $effects;
$out['failures'] = array_keys(array_filter($acceptance, static fn (bool $ok): bool => !$ok));
$out['acceptance_total'] = count($acceptance);
$out['acceptance_passed'] = count($acceptance) - count($out['failures']);
$out['verdict'] = $out['failures'] ? 'BLOCKED_NATIVE_NO_WORKAROUND' : 'NATIVE_CANDIDATE_ONLY';
echo wp_json_encode($out);
