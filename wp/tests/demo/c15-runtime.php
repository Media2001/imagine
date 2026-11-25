<?php
/** C15 native read-only acceptance, no additional fixtures. */
declare(strict_types=1);
namespace Imagine\Demo\C15Tests;
use Imagine\Site\EcheancesNatives;
use Imagine\Site\EcheancesAdmin;
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') { throw new \RuntimeException('Wrong target'); }
$c = ['raccord_present' => class_exists(EcheancesNatives::class) && class_exists(EcheancesAdmin::class)];
if ($c['raccord_present']) {
    $f = get_option('imagine_c09_fixture');
    foreach (['E-ABO' => true, 'E-ADMIN' => true, 'E-REDAC' => false, 'A-CARTE' => false] as $key => $allowed) {
        wp_set_current_user($f['users'][$key]);
        $c['capacite_' . $key] = EcheancesAdmin::autorise() === $allowed;
    }
    wp_set_current_user($f['users']['E-ABO']);
    $c['referent_cap_dediee_sans_manage_options'] = current_user_can('imagine_gerer_echeances') && !current_user_can('manage_options') && !current_user_can('manage_woocommerce');
    $views = [];
    foreach (['echeances', 'attente', 'virements', 'mandats', 'echecs'] as $view) { $views[$view] = EcheancesNatives::lire($view, 30); }
    $c['A_ECHEANCE_dans_echeances'] = in_array($f['subscriptions']['A-ECHEANCE'], array_column($views['echeances'], 'id'), true);
    $c['A_VIR_seul_virement'] = array_column($views['virements'], 'id') === [$f['orders']['A-VIR']];
    $c['A_VIR_attente'] = in_array($f['orders']['A-VIR'], array_column($views['attente'], 'id'), true);
    $c['A_CARTE_payee_hors_attente'] = !in_array($f['orders']['A-CARTE'], array_column($views['attente'], 'id'), true);
    $failed = array_column($views['echecs'], 'id'); sort($failed); $expected = [$f['renewals']['A-GRACE'], $f['renewals']['A-SUSP']]; sort($expected);
    $c['echecs_GRACE_SUSP_seulement'] = $failed === $expected;
    $c['A_PAPIER_seul_mandat'] = array_column($views['mandats'], 'id') === [$f['subscriptions']['A-PAPIER']];
    $paper = $views['mandats'][0] ?? [];
    $c['mandat_identifiant_fictif_natif'] = ($paper['reference'] ?? '') === 'A-PAPIER';
    $c['mandat_montant_date_natifs'] = ($paper['montant'] ?? null) === wcs_get_subscription($f['subscriptions']['A-PAPIER'])->get_total()
        && ($paper['echeance'] ?? null) === wcs_get_subscription($f['subscriptions']['A-PAPIER'])->get_time('next_payment');
    $c['pas_IBAN_dans_projection'] = !preg_match('/iban/i', wp_json_encode($views));
    $source = wc_get_order($f['orders']['A-VIR']);
    $clone = clone $source;
    $clone->set_customer_id($f['users']['A-CARTE']);
    $c['marqueur_fictif_mauvais_proprietaire_ferme'] = EcheancesNatives::methode($clone) === '';
    $clone = clone $source; $clone->set_id(2147483647);
    $c['marqueur_fictif_mauvais_id_ferme'] = EcheancesNatives::methode($clone) === '';
    $clone = clone $source; $clone->update_meta_data('imagine_demo_fictif', '0');
    $c['marqueur_sans_fictif_ferme'] = EcheancesNatives::methode($clone) === '';
    $clone = clone $source; $clone->set_payment_method('stripe');
    $c['methode_native_prioritaire_pas_de_bacs_invente'] = EcheancesNatives::methode($clone) === 'stripe';
    $c['garde_hors_ligne'] = apply_filters('pre_wp_mail', null, []) === false && is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
        && WC()->payment_gateways()->get_available_payment_gateways() === [];
    wp_set_current_user(0);
    $c['anonyme_ferme'] = !EcheancesAdmin::autorise();
}
echo wp_json_encode($c);
