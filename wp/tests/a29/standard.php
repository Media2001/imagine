<?php

declare(strict_types=1);

use Imagine\ScheduledTasks\Analysis;

// Parent-only installed-source gate. No WordPress bootstrap or provider call.
require '/subject/a29/Analysis.php';

$site = $argv[1] ?? '';
$woo = $site . '/wp-content/plugins/woocommerce';
$files = [
    'wp_cron' => $site . '/wp-includes/cron.php',
    'as_store' => $woo . '/packages/action-scheduler/classes/data-stores/ActionScheduler_DBStore.php',
    'as_schema' => $woo . '/packages/action-scheduler/classes/schema/ActionScheduler_StoreSchema.php',
    'as_functions' => $woo . '/packages/action-scheduler/functions.php',
    'email' => $woo . '/includes/class-wc-background-emailer.php',
    'background' => $woo . '/includes/abstracts/class-wc-background-process.php',
];
$sources = [];
$hashes = [];
foreach ($files as $key => $file) {
    if (!is_file($file) || is_link($file)) {
        throw new RuntimeException('A29_STANDARD_SOURCE_MISSING');
    }
    $sources[$key] = file_get_contents($file);
    $hashes[$key] = hash('sha256', $sources[$key]);
}
$checks = [
    'native_cron_option_version' => str_contains($sources['wp_cron'], 'function _get_cron_array(')
        && str_contains($sources['wp_cron'], "'cron'") && str_contains($sources['wp_cron'], "'version'"),
    'native_as_gmt_status_hook_columns' => str_contains($sources['as_schema'], 'scheduled_date_gmt')
        && str_contains($sources['as_schema'], 'hook') && str_contains($sources['as_schema'], 'status'),
    'native_as_db_store' => str_contains($sources['as_store'], 'ActionScheduler_DBStore')
        && str_contains($sources['as_store'], 'function mark_failure('),
    'native_email_queue_hook_composition' => str_contains($sources['email'], "'wc_emailer'")
        && str_contains($sources['email'], 'get_current_blog_id()')
        && str_contains($sources['background'], "'_cron'"),
];
foreach (['enqueue_async_action', 'schedule_single_action', 'schedule_recurring_action', 'schedule_cron_action'] as $api) {
    $checks['native_pre_as_' . $api] = str_contains($sources['as_functions'], "'pre_as_" . $api . "'");
}
$roots = [$site . '/wp-includes', $site . '/wp-admin', $woo,
    $site . '/wp-content/plugins/woocommerce-subscriptions'];
$found = array_fill_keys(array_keys(Analysis::HOOKS), false);
$index = 0;
foreach ($roots as $root) {
    if (!is_dir($root) || is_link($root)) {
        throw new RuntimeException('A29_STANDARD_SOURCE_MISSING');
    }
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS)) as $file) {
        if (!$file->isFile() || $file->isLink() || $file->getExtension() !== 'php') {
            continue;
        }
        $source = file_get_contents($file->getPathname());
        foreach ($found as $hook => $ok) {
            if (!$ok && str_contains($source, $hook)) {
                $found[$hook] = true;
                $hashes['hook_source_' . array_search($hook, array_keys($found), true)] = hash('sha256', $source);
            }
        }
    }
}
// Legacy queue identifier is composed by the native background process.
$found['wp_1_wc_emailer_cron'] = $checks['native_email_queue_hook_composition'];
foreach ($found as $ok) {
    $checks['installed_closed_hook_' . $index++] = $ok;
}
$report = ['qualification' => 'installed_source_lexical_gate_and_sha256', 'source_sha256' => $hashes,
    'checks' => array_map(static fn(string $key, bool $ok): array => [
        'check' => $key, 'status' => $ok ? 'PASS' : 'FAIL',
    ], array_keys($checks), array_values($checks)), 'exit_code' => (int) in_array(false, $checks, true)];
file_put_contents('/report/' . basename($site) . '-standard.json', json_encode($report, JSON_PRETTY_PRINT) . "\n");
exit($report['exit_code']);
