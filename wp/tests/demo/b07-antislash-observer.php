<?php

declare(strict_types=1);

// Observateur temporaire B07, sans bloquer ni changer le gardien existant.
$GLOBALS['b07_antislash_observation'] = ['mail' => 0, 'http' => 0, 'http_agenda' => 0,
    'http_infrastructure' => 0, 'http_autre' => 0, 'transport_mail' => 0, 'transport_http' => 0];
add_filter('pre_wp_mail', static function ($value) {
    $GLOBALS['b07_antislash_observation']['mail']++;
    return $value;
}, -9999);
add_filter('pre_http_request', static function ($value) {
    $GLOBALS['b07_antislash_observation']['http']++;
    $stack = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS);
    $files = array_map(static fn ($frame) => basename($frame['file'] ?? ''), $stack);
    $functions = array_column($stack, 'function');
    $licence = in_array('licensing.php', $files, true)
        && in_array('Novamira\\Pro\\license_api_get', $functions, true);
    $queue = in_array('wp-async-request.php', $files, true)
        && in_array('ActionScheduler_AsyncRequest_QueueRunner.php', $files, true);
    $subject = in_array('Agenda.php', $files, true) || in_array('AgendaConfidentialite.php', $files, true);
    $key = $licence || $queue ? 'http_infrastructure' : ($subject ? 'http_agenda' : 'http_autre');
    $GLOBALS['b07_antislash_observation'][$key]++;
    return $value;
}, -9999);
add_action('phpmailer_init', static function (): void {
    $GLOBALS['b07_antislash_observation']['transport_mail']++;
});
add_action('http_api_debug', static function (): void {
    $GLOBALS['b07_antislash_observation']['transport_http']++;
});
register_shutdown_function(static function (): void {
    file_put_contents(WP_CONTENT_DIR . '/imagine-demo-build/b07-antislash-observations.jsonl',
        json_encode($GLOBALS['b07_antislash_observation']) . "\n", FILE_APPEND | LOCK_EX);
});
