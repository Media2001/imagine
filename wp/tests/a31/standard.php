<?php

declare(strict_types=1);

// Installed sources inspected before subject bootstrap; no guessed installed hash.
$site = $argv[1] ?? '';
$woo = $site . '/wp-content/plugins/woocommerce';
$paths = [
    'order' => $woo . '/includes/abstracts/abstract-wc-order.php',
    'functions' => $woo . '/includes/wc-order-functions.php',
    'customer' => $woo . '/includes/class-wc-order.php',
    'classic' => $woo . '/includes/data-stores/abstract-wc-order-data-store-cpt.php',
    'hpos' => $woo . '/src/Internal/DataStores/Orders/OrdersTableDataStore.php',
    'refund' => $woo . '/includes/class-wc-order-refund.php',
    'statuses' => $woo . '/src/Enums/OrderStatus.php',
    'internal_statuses' => $woo . '/src/Enums/OrderInternalStatus.php',
];
$sources = [];
$hashes = [];
foreach ($paths as $key => $path) {
    $sources[$key] = file_get_contents($path);
    $hashes[$key] = hash('sha256', $sources[$key]);
}
$checks = [
    'native_order_get_parent' => str_contains($sources['order'], 'function get_parent_id('),
    'native_order_get_date' => str_contains($sources['order'], 'function get_date_created('),
    'native_order_get_customer' => str_contains($sources['customer'], 'function get_customer_id('),
    'native_closed_statuses' => str_contains($sources['functions'], 'function wc_get_order_statuses(')
        && str_contains($sources['functions'], 'OrderInternalStatus::REFUNDED')
        && str_contains($sources['internal_statuses'], "public const REFUNDED = 'wc-refunded';"),
    'native_classic_reader' => str_contains($sources['classic'], 'function read('),
    'native_hpos_reader' => str_contains($sources['hpos'], 'wc_orders_meta'),
    'native_refund_type' => str_contains($sources['refund'], 'shop_order_refund'),
];
$statusMap = ['PENDING' => 'pending', 'PROCESSING' => 'processing', 'ON_HOLD' => 'on-hold',
    'COMPLETED' => 'completed', 'CANCELLED' => 'cancelled', 'REFUNDED' => 'refunded', 'FAILED' => 'failed'];
foreach ($statusMap as $constant => $value) {
    $checks['native_status_' . $value] = str_contains($sources['functions'], 'OrderInternalStatus::' . $constant)
        && str_contains($sources['internal_statuses'], "public const {$constant} = 'wc-{$value}';")
        && str_contains($sources['statuses'], "public const {$constant} = '{$value}';");
}
$checks['native_status_checkout_draft'] = str_contains(
    $sources['statuses'],
    "public const CHECKOUT_DRAFT = 'checkout-draft';"
);
$found = ['native_wcs_subscription_getter' => false, 'native_wcs_uncached_related_reader' => false,
    'native_wcs_default_types' => false, 'native_wcs_parent_field' => false];
$wcs = $site . '/wp-content/plugins/woocommerce-subscriptions';
foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($wcs, FilesystemIterator::SKIP_DOTS)) as $file) {
    if (!$file->isFile() || $file->getExtension() !== 'php') {
        continue;
    }
    $source = file_get_contents($file->getPathname());
    $rules = [
        'native_wcs_subscription_getter' => str_contains($source, 'function wcs_get_subscription('),
        'native_wcs_uncached_related_reader' => str_contains($source, 'class WCS_Related_Order_Store_CPT extends')
            && str_contains($source, 'function get_related_subscription_ids(')
            && str_contains($source, '$order->get_meta(') && str_contains($source, "'_subscription_%s'"),
        'native_wcs_default_types' => str_contains($source, 'abstract class WCS_Related_Order_Store')
            && str_contains($source, "'renewal'") && str_contains($source, "'resubscribe'")
            && str_contains($source, "'switch'"),
        'native_wcs_parent_field' => str_contains($source, 'class WC_Subscription')
            && str_contains($source, 'get_parent_id('),
    ];
    foreach ($rules as $key => $ok) {
        if ($ok && !$found[$key]) {
            $hashes[$key] = hash('sha256', $source);
            $found[$key] = true;
        }
    }
}
$checks += $found;
$report = ['source_sha256' => $hashes, 'checks' => array_map(static fn (string $key, bool $ok): array => [
    'check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'], array_keys($checks), array_values($checks)),
    'exit_code' => (int) in_array(false, $checks, true)];
file_put_contents('/report/' . basename($site) . '-standard.json', json_encode($report, JSON_PRETTY_PRINT) . "\n");
exit($report['exit_code']);
