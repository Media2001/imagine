<?php
/** Second C20 probe: installed native calls, exact transactional rollback, no gateway. */
declare(strict_types=1);
namespace Imagine\Demo\C20Second;

use Imagine\Site\{MonCompte, Paywall, EnvoiNatif};
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Echeancier\{Planificateur, ReglagesAdministration};

define('IMAGINE_C20_READ_ONLY', true);
ob_start();
require __DIR__ . '/c20-native.php';
ob_end_clean();
$f = \Imagine\Demo\C20\guard();
global $tables;
$tables = \Imagine\Demo\C20\tables();
$checks = [];
$effects = [];
add_filter('pre_http_request', static function () use (&$effects) { $effects[] = 'http'; return new \WP_Error('c20_offline'); }, PHP_INT_MAX);
add_filter('pre_wp_mail', static function () use (&$effects) { $effects[] = 'mail'; return false; }, PHP_INT_MAX);

function transaction(callable $callback): array
{
    global $wpdb, $tables;
    $before = \Imagine\Demo\C20\fingerprint($tables);
    $wpdb->query('START TRANSACTION');
    $guard = static function (string $sql): string {
        if (preg_match('/^\s*(COMMIT|START\s+TRANSACTION|BEGIN|ROLLBACK|CREATE|ALTER|DROP|TRUNCATE|RENAME|LOCK\s+TABLE|UNLOCK\s+TABLE|SET\s+autocommit)\b/i', $sql)) {
            throw new \RuntimeException('Transaction termination refused.');
        }
        return $sql;
    };
    add_filter('query', $guard, PHP_INT_MAX);
    try {
        $data = $callback();
    } finally {
        remove_filter('query', $guard, PHP_INT_MAX);
        $wpdb->query('ROLLBACK');
        wp_cache_flush();
        Paywall::invalidate();
    }
    $after = \Imagine\Demo\C20\fingerprint($tables);
    if ($before !== $after) {
        throw new \RuntimeException('C20 rollback drift: STOP');
    }
    return ['result' => $data, 'rollback_exact_all_tables' => true];
}

$carte = transaction(static function () use ($f, &$checks): array {
    $before = \Imagine\Demo\C20\state('A-CARTE', $f);
    $s = wcs_get_subscription($before['id']);
    wp_set_current_user($s->get_customer_id());
    $allowed = $s->can_be_updated_to('pending-cancel') && current_user_can('cancel_subscription', $s->get_id());
    if (!$allowed) {
        throw new \RuntimeException('Existing fixture cannot cancel natively.');
    }
    $s->update_status('pending-cancel', 'C20 offline second probe');
    $after = \Imagine\Demo\C20\state('A-CARTE', $f);
    $checks['pending_cancel_native_membership_pending'] = $after['membership_status'] === 'pending';
    $checks['pending_cancel_access_unchanged'] = $after['access_C06'] === $before['access_C06'];
    $checks['pending_cancel_shipping_unchanged'] = $after['shipping_C13'] === $before['shipping_C13'];
    $checks['B02_numbers_unchanged'] = array_intersect_key($after['account_B02'], array_flip(['premier','dernier','restants','echeances'])) === array_intersect_key($before['account_B02'], array_flip(['premier','dernier','restants','echeances']));
    $s = wcs_get_subscription($s->get_id());
    $resume = $s->can_be_updated_to('active');
    $details = ['can_resume' => $resume, 'products_unavailable' => $s->contains_unavailable_product(), 'manual' => $s->is_manual(), 'payment_method' => $s->get_payment_method(), 'end' => $s->get_date('end')];
    if ($resume) {
        $s->update_status('active', 'C20 standard resumption');
        $details['resumed'] = \Imagine\Demo\C20\state('A-CARTE', $f);
    }
    // Same pending membership without native subscription must remain closed.
    delete_post_meta($f['memberships']['A-CARTE'], '_subscription_id');
    Paywall::invalidate();
    $checks['pending_unlinked_stays_closed'] = !Paywall::decision(get_post(get_option('imagine_c08_fixture')['article']))['complet'];
    return ['before' => $before, 'after' => $after, 'resumption' => $details];
});
$four = transaction(static function () use ($f): array {
    $before = \Imagine\Demo\C20\state('A-SEPA4', $f);
    $s = wcs_get_subscription($before['id']);
    $engine = new Moteur(EnvoiNatif::calendrier());
    $year = $engine->ouvrir(new \DateTimeImmutable($s->get_date('start'), new \DateTimeZone('UTC')));
    foreach (\Imagine\Site\EnvoiRelations::renouvellements($s) as $row) {
        $year = $engine->renouveler($year, new \DateTimeImmutable($row['debut'], new \DateTimeZone('UTC')));
    }
    $planner = new Planificateur($engine);
    $margin = (new ReglagesAdministration())->lire()->margeJours;
    $current = $planner->planifier($year, $margin);
    $last = $engine->dernier($year);
    if (!$last) {
        throw new \RuntimeException('C05 current block incomplete.');
    }
    // For a successor C05 uses the calendar launches, never this seed as a payment date.
    // Reuse an existing editorial instant; no manual end-date arithmetic.
    $successor = $engine->renouveler($year, $last->sortie);
    $next = $planner->planifier($successor, $margin);
    $end = $next[0]->date->setTimezone(new \DateTimeZone('UTC'))->format('Y-m-d H:i:s');
    $s->update_dates(['end' => $end], 'gmt');
    $s->save();
    $after = \Imagine\Demo\C20\state('A-SEPA4', $f);
    $remaining = [];
    foreach ($current as $v) {
        if ($v->date->getTimestamp() > time()) {
            $remaining[] = $v->date->setTimezone(new \DateTimeZone('UTC'))->format('Y-m-d H:i:s');
        }
    }
    $payments = array_values(array_filter($after['actions'], static fn ($a) => $a['hook'] === 'woocommerce_scheduled_subscription_payment'));
    $pendingDates = array_column($payments, 'scheduled_date_gmt');
    $nativeChecks = [
        'active_retained' => $after['status'] === 'active',
        'end_exact_C05_successor_launch' => $after['end'] === $end,
        'next_payment_unchanged' => $after['next_payment'] === $before['next_payment'],
        'C05_remaining_positions_scheduled' => $remaining !== [] && array_diff($remaining, $pendingDates) === [],
        'no_payment_at_or_after_end' => count(array_filter($pendingDates, static fn ($date) => $date >= $end)) === 0,
        'expiration_native_scheduled' => count(array_filter($after['actions'], static fn ($a) => $a['hook'] === 'woocommerce_scheduled_subscription_expiration' && $a['scheduled_date_gmt'] === $end)) === 1,
        'access_unchanged' => $after['access_C06'] === $before['access_C06'],
        'shipping_unchanged' => $after['shipping_C13'] === $before['shipping_C13'],
        'B02_instalments_unchanged' => $after['account_B02']['echeances'] === $before['account_B02']['echeances'],
    ];
    return ['before' => $before, 'after' => $after, 'C05_block_end' => $end, 'C05_remaining' => $remaining, 'native_pending_payment_dates' => $pendingDates, 'checks' => $nativeChecks, 'supported' => !in_array(false, $nativeChecks, true)];
});
wp_set_current_user($f['users']['A-VIR']);
Paywall::invalidate();
$checks['A_VIR_first_payment_closed'] = !Paywall::decision(get_post(get_option('imagine_c08_fixture')['article']))['complet'];
$checks['rollback_exact_carte'] = $carte['rollback_exact_all_tables'];
$checks['rollback_exact_four'] = $four['rollback_exact_all_tables'];
$checks['no_mail_http_attempt'] = $effects === [];
wp_set_current_user(0);
echo wp_json_encode(['checks'=>$checks,'failures'=>array_keys(array_filter($checks, static fn ($v)=>!$v)), 'carte'=>$carte, 'four'=>$four, 'effects'=>$effects]);
