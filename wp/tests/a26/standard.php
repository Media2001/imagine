<?php

declare(strict_types=1);

$paths = ['html' => '/opt/wordpress/wordpress/wp-includes/html-api/class-wp-html-tag-processor.php',
    'parser' => '/opt/wordpress/wordpress/wp-includes/class-wp-block-parser.php',
    'shortcodes' => '/opt/wordpress/wordpress/wp-includes/shortcodes.php',
    'plugins' => '/opt/wordpress/wordpress/wp-admin/includes/plugin.php',
    'options' => '/opt/wordpress/wordpress/wp-includes/option.php',
    'storage' => '/opt/woocommerce/woocommerce/src/Utilities/OrderUtil.php',
    'hooks' => '/opt/wordpress/wordpress/wp-includes/class-wp-hook.php',
    'scheduler' => '/opt/woocommerce/woocommerce/packages/action-scheduler/functions.php'];
$hashes = [];
$sources = [];
foreach ($paths as $key => $path) {
    $sources[$key] = file_get_contents($path);
    $hashes[$key] = hash('sha256', $sources[$key]);
}
$rules = ['native_html_tag_processor' => str_contains($sources['html'], 'class WP_HTML_Tag_Processor')
        && str_contains($sources['html'], 'function next_token(')
        && str_contains($sources['html'], 'function get_attribute('),
    'native_default_block_parser' => str_contains($sources['parser'], 'class WP_Block_Parser'),
    'native_shortcode_regex' => str_contains($sources['shortcodes'], 'function get_shortcode_regex('),
    'native_shortcode_attributes' => str_contains($sources['shortcodes'], 'function shortcode_parse_atts('),
    'native_active_plugins_option' => str_contains($sources['plugins'], "get_option( 'active_plugins'"),
    'native_option_storage' => str_contains($sources['options'], 'function get_option('),
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
