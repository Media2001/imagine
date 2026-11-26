<?php

declare(strict_types=1);

// Loaded by the fixture oracle, never by the inventory.
$native = [];
foreach (['BE', 'FR', 'US', 'AE', '', 'ZZ'] as $country) {
    $required = [];
    foreach (WC()->countries->get_address_fields($country, 'shipping_') as $key => $definition) {
        if (!empty($definition['required'])) {
            $required[] = $key;
        }
    }
    sort($required, SORT_STRING);
    $native[$country === '' ? 'country_absent' : $country] = $required;
}
$base = ['shipping_address_1', 'shipping_city', 'shipping_country', 'shipping_first_name', 'shipping_last_name', 'shipping_postcode'];
$us = array_merge($base, ['shipping_state']);
sort($us, SORT_STRING);
$ae = array_values(array_diff($base, ['shipping_postcode']));
$closed = json_decode(file_get_contents('/subject/a24/country_codes.json'), true, 16, JSON_THROW_ON_ERROR);
$actual = array_keys(WC()->countries->get_countries());
sort($actual, SORT_STRING);
$checks = [
    'native_BE_fields' => $native['BE'] === $base,
    'native_FR_fields' => $native['FR'] === $base,
    'native_US_state_required' => $native['US'] === $us,
    'native_AE_postcode_not_required' => $native['AE'] === $ae,
    'native_missing_country_fallback' => $native['country_absent'] === $base,
    'native_unknown_country_defaults' => $native['ZZ'] === $us,
    'closed_country_codes_equal_native' => $actual === $closed,
];
$source = [];
foreach ([
    'includes/class-wc-countries.php', 'i18n/countries.php', 'includes/class-wc-order.php',
    'includes/class-wc-customer.php', 'includes/data-stores/class-wc-customer-data-store.php',
    'includes/data-stores/class-wc-order-data-store-cpt.php',
    'src/Internal/DataStores/Orders/OrdersTableDataStore.php',
    'packages/action-scheduler/functions.php',
] as $file) {
    $source['woocommerce/' . $file] = hash_file('sha256', WC_ABSPATH . $file);
}
foreach (['includes/core/wcs-functions.php', 'includes/core/class-wc-subscription.php'] as $file) {
    $source['woocommerce-subscriptions/' . $file] = hash_file('sha256', WP_PLUGIN_DIR . '/woocommerce-subscriptions/' . $file);
}
$source['staging/lib.php'] = hash_file('sha256', '/subject/staging/lib.php');
$source['staging/pdo-store.php'] = hash_file('sha256', '/subject/staging/pdo-store.php');
$report = ['php' => PHP_VERSION, 'wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION,
    'subscriptions' => WC_Subscriptions::$version, 'native_required_fields' => $native,
    'native_country_count' => count($actual), 'source_sha256' => $source,
    'checks' => array_map(static fn(string $name, bool $ok): array => ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'],
        array_keys($checks), array_values($checks)),
    'exit_code' => (int) in_array(false, $checks, true)];
$file = '/report/' . (get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic') . '-standard.json';
file_put_contents($file, json_encode($report, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
if ($report['exit_code'] !== 0) {
    throw new RuntimeException('A24_STANDARD_FAILED');
}
