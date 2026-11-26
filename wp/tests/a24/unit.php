<?php

declare(strict_types=1);

// Disposable pure bank, no WordPress or database bootstrap.
$checks = [];
function a24_check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
$file = '/subject/a24/Analysis.php';
if (is_file($file)) {
    require $file;
}
a24_check('analysis_available', class_exists(\Imagine\ShippingAddresses\Analysis::class));
if (class_exists(\Imagine\ShippingAddresses\Analysis::class)) {
    $row = ['shipping' => ['country' => 'BE', 'first_name' => 'Fictif', 'last_name' => 'Exemple',
        'address_1' => 'A24_STREET_PRIVATE_CANARY', 'city' => 'Ville fictive', 'postcode' => '1000'],
        'billing' => [], 'customer' => null,
        'required' => ['shipping_first_name', 'shipping_last_name', 'shipping_country',
            'shipping_address_1', 'shipping_city', 'shipping_postcode']];
    $d = \Imagine\ShippingAddresses\Analysis::analyse([$row], ['BE']);
    a24_check('complete_shipping_not_missing', $d['overall']['subscriptions'] === 1
        && $d['overall']['shipping_empty'] === 0 && $d['overall']['missing_any'] === 0);
    a24_check('no_account_is_not_a_difference', $d['overall']['different_from_account'] === 0
        && $d['overall']['account_unavailable'] === 1);
    a24_check('small_country_is_pooled', count($d['countries']) === 1
        && $d['countries'][0]['country'] === 'autres pays'
        && $d['countries'][0]['counts'] === $d['overall']);
    a24_check('private_address_never_in_analysis', !str_contains(json_encode($d), 'CANARY'));
    $rows = array_fill(0, 5, $row);
    $rows[0]['shipping'] = [];
    $rows[0]['billing'] = ['address_1' => 'Fictif'];
    $rows[0]['customer'] = [];
    $rows[1]['shipping']['postcode'] = '';
    $rows[1]['customer'] = $rows[1]['shipping'];
    $rows[2]['shipping']['country'] = '';
    $rows[2]['customer'] = $rows[2]['shipping'];
    $rows[2]['customer']['address_1'] = 'a24_street_private_canary';
    $rows[3]['shipping']['country'] = 'A24_COUNTRY_PRIVATE_CANARY';
    $rows[3]['customer'] = $rows[3]['shipping'];
    $rows[3]['customer']['address_1'] .= ' ';
    $d = \Imagine\ShippingAddresses\Analysis::analyse($rows, ['BE']);
    $o = $d['overall'];
    a24_check('empty_shipping_and_billing_present_exact', $o['shipping_empty'] === 1 && $o['empty_with_billing'] === 1);
    a24_check('native_missing_counts_exact', $o['missing_any'] === 3 && $o['missing_required']['shipping_postcode'] === 2
        && $o['missing_required']['shipping_country'] === 2 && $o['missing_required']['shipping_company'] === 0);
    a24_check('absent_and_unknown_countries_separate', $o['country_absent'] === 2 && $o['country_unknown'] === 1);
    a24_check('literal_case_and_space_comparison', $o['different_from_account'] === 2);
    a24_check('unknown_country_not_leaked', !str_contains(json_encode($d), 'CANARY'));
    $n = \Imagine\ShippingAddresses\Analysis::analyse($rows, ['BE'], true);
    a24_check('neutralisation_unknown_never_false_zero', $n['overall']['shipping_empty'] === 'inconnu après neutralisation'
        && $n['overall']['missing_required']['shipping_postcode'] === 'inconnu après neutralisation'
        && $n['overall']['different_from_account'] === 'inconnu après neutralisation');
    a24_check('neutralisation_preserves_country_and_totals', $n['overall']['subscriptions'] === 5
        && $n['overall']['country_absent'] === 2 && $n['overall']['country_unknown'] === 1
        && $n['overall']['missing_required']['shipping_country'] === 2
        && $n['overall']['account_unavailable'] === 1);
    $empty = \Imagine\ShippingAddresses\Analysis::analyse([], ['BE']);
    a24_check('empty_population_has_closed_zero_counts', $empty['overall']['subscriptions'] === 0
        && $empty['countries'] === [] && count($empty['overall']['missing_required']) === 10);
    $five = \Imagine\ShippingAddresses\Analysis::analyse(array_fill(0, 5, $row), ['BE']);
    $four = \Imagine\ShippingAddresses\Analysis::analyse(array_fill(0, 4, $row), ['BE']);
    a24_check('threshold_five_exact', $five['countries'][0]['country'] === 'BE'
        && $four['countries'][0]['country'] === 'autres pays');
    $optional = $row;
    $optional['shipping']['postcode'] = '';
    $optional['required'] = array_values(array_diff($optional['required'], ['shipping_postcode']));
    $optional['shipping']['phone'] = '0';
    $optional['required'][] = 'shipping_phone';
    $o = \Imagine\ShippingAddresses\Analysis::analyse([$optional], ['BE'])['overall'];
    a24_check('native_optional_and_zero_string_respected', $o['missing_any'] === 0
        && $o['missing_required']['shipping_postcode'] === 0 && $o['missing_required']['shipping_phone'] === 0);
    $spaces = $row;
    $spaces['shipping'] = array_fill_keys(\Imagine\ShippingAddresses\Analysis::FIELDS, '  ');
    $spaces['billing'] = [];
    $o = \Imagine\ShippingAddresses\Analysis::analyse([$spaces], ['BE'])['overall'];
    a24_check('space_only_is_empty_not_unknown_country', $o['shipping_empty'] === 1
        && $o['empty_with_billing'] === 0 && $o['country_absent'] === 1 && $o['country_unknown'] === 0);
    $bad = $row;
    $bad['required'][] = 'shipping_A24_FIELD_PRIVATE_CANARY';
    try {
        \Imagine\ShippingAddresses\Analysis::analyse([$bad], ['BE']);
        a24_check('free_native_field_refused', false);
    } catch (RuntimeException $error) {
        a24_check('free_native_field_refused', $error->getMessage() === 'A24_NATIVE_FIELDS_UNSUPPORTED');
    }
}
$result = ['suite' => 'A24-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (getenv('A24_PURE_PROBE') !== '1') {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
}
echo 'A24_PURE_' . ($result['exit_code'] === 0 ? 'OK' : 'FAIL') . ' ' . count($checks) . "\n";
exit($result['exit_code']);
