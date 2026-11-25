<?php
/** Complément C09 : lecture persistée indépendante du catalogue, jamais de paiement réel. */
declare(strict_types=1);
namespace Imagine\Demo\C09PaymentsTests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new \RuntimeException('Cible C09 refusée.');
}
$f = get_option('imagine_c09_fixture');
$checks = []; $proof = [];
foreach (['A-CARTE', 'A-PAYPAL', 'A-ETRANGER', 'A-SANSMAIL', 'A-ECHEANCE', 'A-NONRENOUV', 'A-SEPA4', 'A-PAPIER'] as $key) {
    $o = wc_get_order($f['orders'][$key]);
    $checks[$key . ':initial_paye'] = $o->is_paid() && (bool) $o->get_date_paid();
    $checks[$key . ':initial_fictif'] = $o->get_meta('imagine_demo_fictif') === '1'
        && $o->get_payment_method_title() === 'Paiement fictif de démonstration';
    $checks[$key . ':aucune_transaction'] = !$o->get_payment_method() && !$o->get_transaction_id() && $o->get_payment_tokens() === [];
    $proof[$key]['initial'] = ['id' => $o->get_id(), 'status' => $o->get_status(), 'paid' => $o->get_date_paid()?->getTimestamp(), 'total' => $o->get_total()];
}
foreach ($f['subscriptions'] as $key => $id) {
    $s = wcs_get_subscription($id);
    $checks[$key . ':manuel_sans_jeton'] = $s->is_manual() && !$s->get_payment_method() && !$s->get_transaction_id() && $s->get_payment_tokens() === [];
}
$o = wc_get_order($f['orders']['A-VIR']);
$checks['A-VIR:non_paye'] = !$o->get_date_paid() && !$o->is_paid() && $o->has_status('on-hold');
$checks['hors_ligne'] = apply_filters('pre_wp_mail', null, []) === false
    && is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    && WC()->payment_gateways()->get_available_payment_gateways() === [];
foreach (['A-SEPA4' => 'processing', 'A-GRACE' => 'failed', 'A-SUSP' => 'failed'] as $key => $expected) {
    $s = wcs_get_subscription($f['subscriptions'][$key]);
    $orders = array_map('wc_get_order', array_values($s->get_related_orders('ids', 'renewal')));
    $checks[$key . ':renouvellement_unique'] = count($orders) === 1;
    $o = count($orders) === 1 ? reset($orders) : null;
    $checks[$key . ':renouvellement_natif'] = $o && $o->has_status($expected)
        && (int) $o->get_meta('_subscription_renewal') === $s->get_id()
        && (int) $o->get_customer_id() === (int) $s->get_customer_id();
    $checks[$key . ':renouvellement_fictif'] = $o && $o->get_meta('imagine_demo_fictif') === '1'
        && $o->get_payment_method_title() === 'Paiement fictif de démonstration'
        && !$o->get_payment_method() && !$o->get_transaction_id() && $o->get_payment_tokens() === [];
    if ($key === 'A-SEPA4') {
        $checks[$key . ':deux_payees_sur_quatre'] = $s->get_payment_count() === 2
            && $o && (bool) $o->get_date_paid() && $s->get_time('next_payment') > time()
            && $s->get_billing_period() === 'month' && (int) $s->get_billing_interval() === 3;
    } else {
        $checks[$key . ':rejet_date_grace'] = $o && !$o->get_date_paid()
            && $o->get_date_created()->getTimestamp() === strtotime($s->get_meta('_imagine_acces_grace_debut') . ' UTC');
    }
    $proof[$key]['renewals'] = array_map(static fn ($o) => ['id' => $o->get_id(), 'status' => $o->get_status(),
        'created' => $o->get_date_created()->getTimestamp(), 'paid' => $o->get_date_paid()?->getTimestamp(), 'total' => $o->get_total()], $orders);
}
foreach ($f['subscriptions'] as $key => $id) {
    $s = wcs_get_subscription($id);
    $checks[$key . ':marque_fictive_abonnement'] = $s->get_meta('imagine_demo_fictif') === '1'
        && $s->get_payment_method_title() === 'Paiement fictif de démonstration';
    foreach ($s->get_items() as $item) {
        $checks[$key . ':marque_ligne_abonnement'] = $item->get_meta('imagine_demo_fictif') === '1';
    }
}
foreach ($f['users'] as $key => $id) {
    $checks[$key . ':marque_compte'] = get_user_meta($id, 'imagine_demo_fictif', true) === '1';
}
foreach ($f['memberships'] as $key => $id) {
    $checks[$key . ':marque_adhesion'] = get_post_meta($id, 'imagine_demo_fictif', true) === '1';
}
foreach ([$f['plan'], $f['product'], ...array_values($f['tariffs'])] as $id) {
    $checks['catalogue_' . $id . ':marque'] = get_post_meta($id, 'imagine_demo_fictif', true) === '1';
}
foreach (['A-VIR', 'A-GRACE', 'A-SUSP', 'A-EXPIRE'] as $key) {
    $o = wc_get_order($f['orders'][$key]);
    $checks[$key . ':initial_non_paye_conserve'] = !$o->get_date_paid() && !$o->is_paid();
}
foreach (['P-OFFERT', 'P-GEST', 'P-BENEF'] as $key) {
    $checks[$key . ':aucun_lien_ou_droit_invente'] = !isset($f['subscriptions'][$key]) && !isset($f['memberships'][$key]);
}
foreach ([...array_values($f['orders']), ...array_values($f['renewals'])] as $id) {
    $o = wc_get_order($id);
    $ok = $o->get_meta('imagine_demo_fictif') === '1'
        && $o->get_payment_method_title() === 'Paiement fictif de démonstration';
    foreach (['line_item', 'shipping', 'fee'] as $type) {
        foreach ($o->get_items($type) as $item) { $ok = $ok && $item->get_meta('imagine_demo_fictif') === '1'; }
    }
    $checks['commande_' . $id . ':marques'] = $ok;
}
$postal = \Imagine\Site\EnvoiNatif::apercu('DEMO-2027-T1');
$checks['A-SANSMAIL:inclusion_postale'] = in_array((string) $f['subscriptions']['A-SANSMAIL'], array_column($postal['liste']->lignes, 'abonnement_id'), true);
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures, 'proof' => $proof]);
if ($failures) { \WP_CLI::halt(1); }
