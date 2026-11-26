<?php

declare(strict_types=1);

use Imagine\SubscriptionPrices\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$path = dirname(__DIR__, 2) . '/outils/bascule/a20/Analysis.php';
if (!is_file($path)) {
    $path = '/subject/a20/Analysis.php';
}
$check('pure_analysis_available', is_file($path));
if (is_file($path)) {
    require_once $path;
    $empty = Analysis::analyse([], 'EUR');
    $check('empty_counts_explicit', $empty['live_subscriptions'] === 0 && $empty['products'] === []
        && $empty['countries'] === [] && $empty['zero_recurring_total'] === 0);
    $base = ['status' => 'active', 'period' => 'year', 'interval' => 1, 'total' => '100.00',
        'currency' => 'EUR', 'country' => 'BE', 'products' => [['product' => 11, 'variation' => 0]],
        'line_count' => 1, 'fees' => false, 'shipping' => false];
    $rows = array_fill(0, 5, $base);
    $rows[] = array_replace($base, ['status' => 'pending', 'period' => 'month', 'total' => '9.00',
        'country' => 'FR', 'shipping' => true, 'fees' => true]);
    $rows[] = array_replace($base, ['status' => 'cancelled', 'total' => '1234567.89']);
    $data = Analysis::analyse($rows, 'EUR');
    $p = $data['products'][0] ?? [];
    $check('live_status_scope', $data['live_subscriptions'] === 6);
    $check('product_states_distinct_subscriptions', ($p['product'] ?? null) === 11
        && ($p['variation'] ?? null) === 0 && ($p['states'] ?? null) === ['active' => 5, 'pending' => 1, 'on-hold' => 0, 'pending-cancel' => 0]);
    $check('actual_subscription_schedule', ($p['schedules'] ?? null) === [
        ['interval' => 1, 'period' => 'month', 'count' => 1], ['interval' => 1, 'period' => 'year', 'count' => 5]]
        && ($p['non_annual'] ?? null) === 1);
    $check('threshold_five_visible_one_suppressed', ($p['amounts'] ?? null) === [
        ['currency' => 'EUR', 'amount' => '100.00', 'count' => 5]] && ($p['other_amounts'] ?? null) === 1);
    $check('country_threshold_and_shipping', $data['countries'] === [['country' => 'BE', 'count' => 5, 'with_shipping' => 0]]
        && $data['other_countries'] === ['count' => 1, 'with_shipping' => 1]);
    $check('fee_and_shipping_presence', $data['with_fee_line'] === 1 && $data['with_shipping_line'] === 1
        && $data['multiple_product_lines'] === 0);
    $check('rare_and_closed_values_absent', !str_contains(json_encode($data), '9.00')
        && !str_contains(json_encode($data), '1234567.89'));
    $edgeRows = array_fill(0, 5, array_replace($base, ['country' => 'A20_NAME_CANARY', 'total' => '000.0000',
        'status' => 'pending-cancel', 'currency' => 'USD', 'interval' => 12, 'period' => 'month',
        'line_count' => 3, 'products' => [['product' => 11, 'variation' => 12],
            ['product' => 11, 'variation' => 12], ['product' => 20, 'variation' => 0]]]));
    $edge = Analysis::analyse($edgeRows, 'EUR');
    $check('unknown_country_never_leaks_even_five', $edge['countries'] === []
        && $edge['unknown_country'] === ['count' => 5, 'with_shipping' => 0]
        && !str_contains(json_encode($edge), 'CANARY'));
    $check('duplicate_lines_deduplicated_per_product', count($edge['products']) === 2
        && $edge['products'][0]['count'] === 5 && $edge['multiple_product_lines'] === 5);
    $check('variation_and_twelve_months_are_explicit', $edge['products'][0]['variation'] === 12
        && $edge['products'][0]['non_annual'] === 0 && $edge['products'][0]['states']['pending-cancel'] === 5);
    $check('zero_normalized_without_float_and_foreign_currency', $edge['zero_recurring_total'] === 5
        && $edge['foreign_currency'] === 5 && $edge['products'][0]['amounts'] === [
            ['currency' => 'USD', 'amount' => '0.00', 'count' => 5]]);
    $check('every_count_has_definition', isset($data['definitions'])
        && count(array_diff(array_keys($data), array_merge(array_keys($data['definitions']), ['definitions']))) === 0);
    $boundary = Analysis::analyse(array_fill(0, 4, $base), 'EUR');
    $check('four_suppressed_threshold', $boundary['countries'] === []
        && $boundary['other_countries']['count'] === 4 && $boundary['products'][0]['amounts'] === []
        && $boundary['products'][0]['other_amounts'] === 4);
    $mixed = Analysis::analyse(array_merge(array_fill(0, 3, $base), array_fill(0, 3,
        array_replace($base, ['currency' => 'USD']))), 'EUR');
    $check('same_amount_different_currency_not_pooled', $mixed['products'][0]['amounts'] === []
        && $mixed['products'][0]['other_amounts'] === 6);
    foreach (['period' => 'A20_PRIVATE_CANARY', 'currency' => 'A20_PRIVATE_CANARY',
        'interval' => 0, 'total' => '1e3', 'products' => [['product' => 'A20_PRIVATE_CANARY', 'variation' => 0]]] as $key => $bad) {
        $refused = false;
        try {
            Analysis::analyse([array_replace($base, [$key => $bad])], 'EUR');
        } catch (RuntimeException $e) {
            $refused = $e->getMessage() === 'A20_DATA_UNSUPPORTED';
        }
        $check('closed_invalid_data:' . $key, $refused);
    }
    $none = Analysis::analyse([array_replace($base, ['products' => [], 'line_count' => 0,
        'status' => 'on-hold', 'total' => '-0.00', 'country' => ''])], 'EUR');
    $check('no_line_and_missing_country_not_invented', $none['without_product_line'] === 1
        && $none['products'] === [] && $none['unknown_country']['count'] === 1
        && $none['zero_recurring_total'] === 1);
    $check('deterministic_input_order', Analysis::analyse(array_reverse($rows), 'EUR') === $data);
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') !== __FILE__) {
    return $checks;
}
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
exit($result['exit_code']);
