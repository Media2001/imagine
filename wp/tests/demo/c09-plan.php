<?php
/** Altération de plan C09, remise native et décision réelle, nettoyage garanti. */
declare(strict_types=1);
namespace Imagine\Demo\C09PlanTests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new \RuntimeException('Cible refusée.'); }
$f = get_option('imagine_c09_fixture');
$id = $f['memberships']['A-CARTE'];
if (get_post_meta($id, '_imagine_c09_fixture', true) !== 'A-CARTE') { throw new \RuntimeException('Objet étranger.'); }
$temp = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_status' => 'publish',
    'post_title' => 'C09 — plan temporaire de reset, FICTIF', 'meta_input' => ['_imagine_c09_fixture' => 'reset-plan', '_access_method' => 'manual-only']], true);
if (is_wp_error($temp)) { throw new \RuntimeException('Plan temporaire impossible.'); }
$checks = [];
try {
    wc_memberships_create_user_membership(['user_membership_id' => $id, 'user_id' => $f['users']['A-CARTE'], 'plan_id' => $temp]);
    $checks['plan_altere_reellement'] = wc_memberships_get_user_membership($id)->get_plan_id() === $temp;
    ob_start(); require WP_CONTENT_DIR . '/imagine-demo-build/c09-seed.php'; ob_end_clean();
    $checks['plan_restaure_api_native'] = wc_memberships_get_user_membership($id)->get_plan_id() === $f['plan'];
    wp_set_current_user($f['users']['A-CARTE']);
    $d = \Imagine\Site\Paywall::decision(get_post(get_option('imagine_c08_fixture')['article']));
    $checks['decision_apres_reset'] = $d['complet'] && $d['motif'] === 'abonnement_actif';
} finally {
    wc_memberships_create_user_membership(['user_membership_id' => $id, 'user_id' => $f['users']['A-CARTE'], 'plan_id' => $f['plan']]);
    ob_start(); require WP_CONTENT_DIR . '/imagine-demo-build/c09-seed.php'; ob_end_clean();
    if (get_post_meta($temp, '_imagine_c09_fixture', true) === 'reset-plan') { wp_delete_post($temp, true); }
    wp_set_current_user(0);
}
$checks['nettoyage_temporaire_relu'] = get_post($temp) === null && wc_memberships_get_user_membership($id)->get_plan_id() === $f['plan'];
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures]);
if ($failures) { \WP_CLI::halt(1); }
