<?php
declare(strict_types=1);
// Executed only on the newly generated, network-none fixture.
if (!str_contains(ABSPATH, '/imagine-test-a01-ai1wm-')) {
    throw new RuntimeException('SYNTHETIC_PATH_REQUIRED');
}
if (($args[0] ?? '') === 'grow') {
    for ($i = 0; $i < 1500; $i++) {
        wp_insert_post(['post_title' => 'FICTION GENERATED ' . $i, 'post_status' => 'publish',
            'post_content' => str_repeat('FICTION SANS DONNEE PERSONNELLE. ', 3400)]);
    }
    echo "FIXTURE_GROWN\n";
    return;
}
add_filter('ai1wm_completed_timeout', static fn() => 0);
add_filter('ai1wm_max_file_size', static fn() => PHP_INT_MAX);
$params = ['options' => [], 'archive' => ($args[0] ?? 'small') . '.wpress'];
$steps = [];
// The free UI's registered export pipeline, unchanged vendor callbacks.
// wp ai1wm export itself is a paid-extension stub; no license override is used.
foreach (ai1wm_get_filters('ai1wm_export') as $priority => $hooks) {
    $params['priority'] = $priority;
    foreach ($hooks as $hook) {
        $attempts = 0;
        do {
            $params = call_user_func($hook['function'], $params);
            if (++$attempts > 10000) {
                throw new RuntimeException('FIXTURE_EXPORT_TIMEOUT');
            }
        } while (isset($params['completed']) && !$params['completed']);
        $steps[] = $hook['function'];
    }
}
$path = ai1wm_backup_path($params);
file_put_contents('/report/export-' . ($args[0] ?? 'small') . '.json', json_encode([
    'plugin_version' => AI1WM_VERSION, 'path' => $path, 'bytes' => filesize($path),
    'steps' => $steps, 'wordpress' => $GLOBALS['wp_version'], 'php' => PHP_VERSION,
]));
echo "FIXTURE_EXPORTED\n";
