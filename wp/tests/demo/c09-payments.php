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
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures, 'proof' => $proof]);
if ($failures) { \WP_CLI::halt(1); }
