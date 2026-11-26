<?php

declare(strict_types=1);

// Disposable pure bank, no WordPress or database bootstrap.
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$file = '/subject/a24/Analysis.php';
if (is_file($file)) {
    require $file;
}
$check('analysis_available', class_exists(\Imagine\ShippingAddresses\Analysis::class));
if (class_exists(\Imagine\ShippingAddresses\Analysis::class)) {
    $row = ['shipping' => ['country' => 'BE', 'first_name' => 'Fictif', 'last_name' => 'Exemple',
        'address_1' => 'A24_STREET_PRIVATE_CANARY', 'city' => 'Ville fictive', 'postcode' => '1000'],
        'billing' => [], 'customer' => null,
        'required' => ['shipping_first_name', 'shipping_last_name', 'shipping_country',
            'shipping_address_1', 'shipping_city', 'shipping_postcode']];
    $d = \Imagine\ShippingAddresses\Analysis::analyse([$row], ['BE']);
    $check('complete_shipping_not_missing', $d['overall']['subscriptions'] === 1
        && $d['overall']['shipping_empty'] === 0 && $d['overall']['missing_any'] === 0);
    $check('no_account_is_not_a_difference', $d['overall']['different_from_account'] === 0
        && $d['overall']['account_unavailable'] === 1);
    $check('small_country_is_pooled', count($d['countries']) === 1
        && $d['countries'][0]['country'] === 'autres pays'
        && $d['countries'][0]['counts'] === $d['overall']);
    $check('private_address_never_in_analysis', !str_contains(json_encode($d), 'CANARY'));
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
    $check('empty_shipping_and_billing_present_exact', $o['shipping_empty'] === 1 && $o['empty_with_billing'] === 1);
    $check('native_missing_counts_exact', $o['missing_any'] === 3 && $o['missing_required']['shipping_postcode'] === 2
        && $o['missing_required']['shipping_country'] === 2 && $o['missing_required']['shipping_company'] === 0);
    $check('absent_and_unknown_countries_separate', $o['country_absent'] === 2 && $o['country_unknown'] === 1);
    $check('case_and_space_only_rows_are_not_different', $o['different_from_account'] === 0);
    $comparison = $row;
    $comparison['customer'] = $comparison['shipping'];
    foreach (
        [
        'case_only_ignored' => ['Rue ÉCOLE', 'rue école', 0],
        'space_only_ignored' => ["  Rue\t Exemple \n", 'RueExemple', 0],
        'unicode_space_only_ignored' => ["Rue\u{00A0}Exemple\u{202F}", 'RueExemple', 0],
        'actual_street_difference_counted' => ['Rue Exemple', 'Rue Autre', 1],
        'actual_postcode_difference_counted' => ['1000', '1001', 1],
        'accent_not_removed' => ['École', 'Ecole', 1],
        'punctuation_not_removed' => ['Rue-Exemple', 'RueExemple', 1],
        'zero_not_empty' => ['0', '', 1],
        ] as $name => [$shipping, $account, $expected]
    ) {
        $field = $name === 'actual_postcode_difference_counted' ? 'postcode' : 'address_1';
        $case = $comparison;
        $case['shipping'][$field] = $shipping;
        $case['customer'][$field] = $account;
        $snapshot = $case;
        $counts = \Imagine\ShippingAddresses\Analysis::analyse([$case], ['BE']);
        $check($name, $counts['overall']['different_from_account'] === $expected
            && $counts['countries'][0]['counts']['different_from_account'] === $expected
            && $case === $snapshot);
    }
    $raw = $comparison;
    $raw['shipping']['country'] = ' be ';
    $raw['customer']['country'] = 'BE';
    $raw['shipping']['address_1'] = "\u{00A0}";
    $raw['customer']['address_1'] = '';
    $rawCounts = \Imagine\ShippingAddresses\Analysis::analyse([$raw], ['BE'])['overall'];
    $check(
        'comparison_does_not_normalise_raw_completeness_or_country',
        $rawCounts['different_from_account'] === 0 && $rawCounts['country_unknown'] === 1
        && $rawCounts['missing_required']['shipping_address_1'] === 0
    );
    $rawEmpty = $row;
    $rawEmpty['shipping'] = array_fill_keys(\Imagine\ShippingAddresses\Analysis::FIELDS, "\u{00A0}");
    $rawEmpty['customer'] = [];
    $rawEmptyCounts = \Imagine\ShippingAddresses\Analysis::analyse([$rawEmpty], ['BE'])['overall'];
    $check(
        'unicode_comparison_does_not_change_raw_shipping_empty',
        $rawEmptyCounts['shipping_empty'] === 0 && $rawEmptyCounts['missing_any'] === 0
        && $rawEmptyCounts['different_from_account'] === 0
    );
    $check('unknown_country_not_leaked', !str_contains(json_encode($d), 'CANARY'));
    $n = \Imagine\ShippingAddresses\Analysis::analyse($rows, ['BE'], true);
    $check('neutralisation_unknown_never_false_zero', $n['overall']['shipping_empty'] === 'inconnu après neutralisation'
        && $n['overall']['missing_required']['shipping_postcode'] === 'inconnu après neutralisation'
        && $n['overall']['different_from_account'] === 'inconnu après neutralisation');
    $check('neutralisation_preserves_country_and_totals', $n['overall']['subscriptions'] === 5
        && $n['overall']['country_absent'] === 2 && $n['overall']['country_unknown'] === 1
        && $n['overall']['missing_required']['shipping_country'] === 2
        && $n['overall']['account_unavailable'] === 1);
    $empty = \Imagine\ShippingAddresses\Analysis::analyse([], ['BE']);
    $check('empty_population_has_closed_zero_counts', $empty['overall']['subscriptions'] === 0
        && $empty['countries'] === [] && count($empty['overall']['missing_required']) === 10);
    $five = \Imagine\ShippingAddresses\Analysis::analyse(array_fill(0, 5, $row), ['BE']);
    $four = \Imagine\ShippingAddresses\Analysis::analyse(array_fill(0, 4, $row), ['BE']);
    $check('threshold_five_exact', $five['countries'][0]['country'] === 'BE'
        && $four['countries'][0]['country'] === 'autres pays');
    $optional = $row;
    $optional['shipping']['postcode'] = '';
    $optional['required'] = array_values(array_diff($optional['required'], ['shipping_postcode']));
    $optional['shipping']['phone'] = '0';
    $optional['required'][] = 'shipping_phone';
    $o = \Imagine\ShippingAddresses\Analysis::analyse([$optional], ['BE'])['overall'];
    $check('native_optional_and_zero_string_respected', $o['missing_any'] === 0
        && $o['missing_required']['shipping_postcode'] === 0 && $o['missing_required']['shipping_phone'] === 0);
    $spaces = $row;
    $spaces['shipping'] = array_fill_keys(\Imagine\ShippingAddresses\Analysis::FIELDS, '  ');
    $spaces['billing'] = [];
    $o = \Imagine\ShippingAddresses\Analysis::analyse([$spaces], ['BE'])['overall'];
    $check('space_only_is_empty_not_unknown_country', $o['shipping_empty'] === 1
        && $o['empty_with_billing'] === 0 && $o['country_absent'] === 1 && $o['country_unknown'] === 0);
    $bad = $row;
    $bad['required'][] = 'shipping_A24_FIELD_PRIVATE_CANARY';
    try {
        \Imagine\ShippingAddresses\Analysis::analyse([$bad], ['BE']);
        $check('free_native_field_refused', false);
    } catch (RuntimeException $error) {
        $check('free_native_field_refused', $error->getMessage() === 'A24_NATIVE_FIELDS_UNSUPPORTED');
    }
}
$result = ['suite' => 'A24-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (getenv('A24_PURE_PROBE') !== '1') {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
}
echo 'A24_PURE_' . ($result['exit_code'] === 0 ? 'OK' : 'FAIL') . ' ' . count($checks) . "\n";
exit($result['exit_code']);
