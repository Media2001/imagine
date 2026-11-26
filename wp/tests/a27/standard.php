<?php

declare(strict_types=1);

// Parent gate: installed source only, before subject bootstrap; no provider API.
$site = $argv[1] ?? '';
$woo = $site . '/wp-content/plugins/woocommerce';
$paths = [
    'tokens' => $woo . '/includes/class-wc-payment-tokens.php',
    'token_store' => $woo . '/includes/data-stores/class-wc-payment-token-data-store.php',
    'cc' => $woo . '/includes/payment-tokens/class-wc-payment-token-cc.php',
    'order' => $woo . '/includes/abstracts/abstract-wc-order.php',
    'hpos' => $woo . '/src/Internal/DataStores/Orders/OrdersTableDataStore.php',
];
$sources = [];
$hashes = [];
foreach ($paths as $key => $path) {
    $sources[$key] = file_get_contents($path);
    $hashes[$key] = hash('sha256', $sources[$key]);
}
$checks = [
    'native_token_table' => str_contains($sources['token_store'], 'woocommerce_payment_tokens'),
    'native_tokenmeta_table' => str_contains($sources['token_store'], 'woocommerce_payment_tokenmeta'),
    'native_single_token_read_not_customer_pagination' => str_contains($sources['tokens'], 'function get(')
        && str_contains($sources['token_store'], 'function get_token_by_id('),
    'native_order_token_link' => str_contains($sources['order'], 'function get_payment_tokens('),
    'native_cc_expiry' => str_contains($sources['cc'], 'function get_expiry_year(')
        && str_contains($sources['cc'], 'function get_expiry_month('),
    'native_hpos_metadata' => str_contains($sources['hpos'], 'wc_orders_meta'),
];
$wcs = $site . '/wp-content/plugins/woocommerce-subscriptions';
$found = ['native_wcs_manual_flag' => false, 'native_wcs_payment_meta_schema' => false,
    'native_wcs_renewal_dispatch' => false, 'native_paypal_reference_key' => false];
foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($wcs, FilesystemIterator::SKIP_DOTS)) as $file) {
    if (!$file->isFile() || $file->getExtension() !== 'php') {
        continue;
    }
    $source = file_get_contents($file->getPathname());
    $rules = [
        'native_wcs_manual_flag' => str_contains($source, 'function get_requires_manual_renewal('),
        'native_wcs_payment_meta_schema' => str_contains($source, 'woocommerce_subscription_payment_meta'),
        'native_wcs_renewal_dispatch' => str_contains($source, 'woocommerce_scheduled_subscription_payment_'),
        'native_paypal_reference_key' => str_contains($source, '_paypal_subscription_id'),
    ];
    foreach ($rules as $key => $ok) {
        if ($ok && !$found[$key]) {
            $hashes[$key] = hash('sha256', $source);
            $found[$key] = true;
        }
    }
}
$checks += $found;
$report = ['source_sha256' => $hashes, 'checks' => array_map(static fn(string $key, bool $ok): array => [
    'check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'], array_keys($checks), array_values($checks)),
    'exit_code' => (int) in_array(false, $checks, true)];
file_put_contents('/report/' . basename($site) . '-standard.json', json_encode($report, JSON_PRETTY_PRINT) . "\n");
exit($report['exit_code']);
