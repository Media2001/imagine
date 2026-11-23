<?php
/** Corrections C09 : attentes indépendantes du catalogue, objets relus. */
declare(strict_types=1);
namespace Imagine\Demo\C09CorrectionTests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new \RuntimeException('Cible refusée.'); }
$f = get_option('imagine_c09_fixture');
$rows = array_column(json_decode(file_get_contents(WP_CONTENT_DIR . '/imagine-demo-build/c09-profils.json'), true), null, 'code');
$checks = [];
$grid = [];
foreach (['normal' => 120, 'solidaire' => 60, 'soutien' => 240] as $tarif => $annual) {
    foreach ([1, 4] as $times) {
        $key = $tarif . '-' . $times;
        $p = wc_get_product($f['tariffs'][$key] ?? 0);
        $checks[$key . ':produit_subscription_fictif_prive'] = $p instanceof \WC_Product_Subscription
            && $p->get_status() === 'private' && $p->get_catalog_visibility() === 'hidden'
            && str_contains($p->get_name(), 'FICTIF') && $p->get_meta('_imagine_c09_fixture') === 'shared';
        $checks[$key . ':prix_fictif_et_periodicite'] = $p && (float) $p->get_price() === (float) ($annual / $times)
            && (float) $p->get_meta('_subscription_price') === (float) ($annual / $times)
            && $p->get_meta('_subscription_period') === ($times === 1 ? 'year' : 'month')
            && (int) $p->get_meta('_subscription_period_interval') === ($times === 1 ? 1 : 3)
            && (int) $p->get_meta('_subscription_length') === ($times === 1 ? 1 : 12);
        $grid[$key] = $p ? ['id' => $p->get_id(), 'price' => $p->get_price(), 'period' => $p->get_meta('_subscription_period'),
            'interval' => $p->get_meta('_subscription_period_interval'), 'length' => $p->get_meta('_subscription_length')] : null;
    }
}
$checks['six_combinaisons_uniques'] = count($f['tariffs'] ?? []) === 6 && count(array_unique($f['tariffs'] ?? [])) === 6;
foreach (['A-CARTE' => 'normal-1', 'A-SEPA4' => 'normal-4', 'A-PAYPAL' => 'normal-1', 'A-PAPIER' => 'normal-4'] as $code => $key) {
    $pid = $f['tariffs'][$key] ?? 0;
    $order = wc_get_order($f['orders'][$code]);
    $sub = wcs_get_subscription($f['subscriptions'][$code]);
    $oi = array_values($order->get_items()); $si = array_values($sub->get_items());
    $m = wc_memberships_get_user_membership($f['memberships'][$code]);
    $checks[$code . ':raccord_tarif_natif'] = $pid && $oi[0]->get_product_id() === $pid && $si[0]->get_product_id() === $pid
        && $m->get_product_id() === $pid;
    $checks[$code . ':montants_fictifs_sans_paiement'] = $pid && (float) $order->get_total() === (float) wc_get_product($pid)->get_price()
        && (float) $sub->get_total() === (float) wc_get_product($pid)->get_price()
        && !$order->get_date_paid() && !$sub->get_date_paid() && $sub->is_manual() && $sub->get_payment_method() === '';
}
wp_set_current_user($f['users']['E-REDAC']);
$calendarCap = apply_filters('option_page_capability_options', 'manage_options');
$checks['E-REDAC:capacite_reelle_calendrier_absente'] = !current_user_can($calendarCap) && current_user_can('edit_posts');
$checks['E-REDAC:partiel_strict'] = $rows['E-REDAC']['etat'] === 'partiel' && str_contains($rows['E-REDAC']['limite'], 'calendrier');
$checks['V-INSCRIT:partiel_strict'] = $rows['V-INSCRIT']['etat'] === 'partiel';
wp_set_current_user($f['users']['E-ABO']);
$role = get_role('imagine_referent_abonnements');
$expectedCaps = array_fill_keys(['read', 'edit_shop_orders', 'edit_others_shop_orders', 'read_private_shop_orders',
    'edit_private_shop_orders', 'edit_published_shop_orders', 'publish_shop_orders',
    'imagine_creer_compte_client', 'imagine_gerer_echeances', 'imagine_traiter_justificatifs',
    'imagine_exporter_liste_envoi', 'imagine_extraire_abonnes'], true);
$checks['E-ABO:matrice_limitee_exacte'] = $role && count(array_diff_assoc($role->capabilities, $expectedCaps)) === 0
    && count(array_diff_assoc($expectedCaps, $role->capabilities)) === 0;
$checks['E-ABO:nom_role_et_attribution'] = (wp_roles()->role_names['imagine_referent_abonnements'] ?? '') === 'Référent abonnements'
    && wp_get_current_user()->roles === ['imagine_referent_abonnements'];
foreach (['edit_posts', 'edit_pages', 'publish_posts', 'upload_files', 'manage_options', 'manage_woocommerce',
    'edit_products', 'edit_users', 'create_users', 'delete_users', 'promote_users', 'delete_shop_orders'] as $denied) {
    $checks['E-ABO:interdit:' . $denied] = !current_user_can($denied);
}
$d = \Imagine\Site\Paywall::decision(get_post(get_option('imagine_c08_fixture')['article']));
$checks['E-ABO:lecture_equipe'] = $d['complet'] && $d['motif'] === 'equipe';
wp_set_current_user($f['users']['A-VIR']);
$d = \Imagine\Site\Paywall::decision(get_post(get_option('imagine_c08_fixture')['article']));
$checks['A-VIR:arbitrage_virement_non_valide'] = !$d['complet'] && $d['motif'] === 'virement_non_valide';
$calendar = get_option('imagine_demo_calendrier');
$checks['calendrier_15_parutions_complet'] = count($calendar) === 15
    && count(array_filter($calendar, static fn ($r) => !empty($r['sortie']) && !empty($r['cloture']))) === 15;
wp_set_current_user(0);
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures, 'tariffs' => $grid,
    'calendar_capability' => $calendarCap, 'role_capabilities' => $role ? $role->capabilities : null], JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
