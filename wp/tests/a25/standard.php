<?php

declare(strict_types=1);

$paths = ['comment' => '/opt/wordpress/wordpress/wp-includes/class-wp-comment.php',
    'order' => '/opt/woocommerce/woocommerce/includes/class-wc-order.php',
    'abstract_order' => '/opt/woocommerce/woocommerce/includes/abstracts/abstract-wc-order.php',
    'storage' => '/opt/woocommerce/woocommerce/src/Utilities/OrderUtil.php',
    'hooks' => '/opt/wordpress/wordpress/wp-includes/class-wp-hook.php',
    'scheduler' => '/opt/woocommerce/woocommerce/packages/action-scheduler/functions.php'];
$hashes = [];
$sources = [];
foreach ($paths as $key => $path) {
    $sources[$key] = file_get_contents($path);
    $hashes[$key] = hash('sha256', $sources[$key]);
}
$rules = ['native_wp_comment' => str_contains($sources['comment'], 'class WP_Comment'),
    'native_customer_getter' => str_contains($sources['order'], 'function get_customer_id('),
    'native_order_date_getter' => str_contains($sources['abstract_order'], 'function get_date_created('),
    'native_authoritative_store' => str_contains($sources['storage'], 'function custom_orders_table_usage_is_enabled('),
    'native_preinitialised_hooks' => str_contains($sources['hooks'], 'function build_preinitialized_hooks(')];
foreach (
    ['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
    'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook
) {
    $rules['native_filter:' . $hook] = str_contains($sources['scheduler'], "apply_filters( '" . $hook . "', null,");
}
$report = ['source_sha256' => $hashes, 'checks' => array_map(static fn(string $key, bool $ok): array => [
    'check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'], array_keys($rules), array_values($rules)),
    'exit_code' => (int) in_array(false, $rules, true)];
file_put_contents('/report/standard.json', json_encode($report, JSON_PRETTY_PRINT) . "\n");
exit($report['exit_code']);
