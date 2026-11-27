<?php

declare(strict_types=1);

// Observateur temporaire B07, sans bloquer ni changer le gardien existant.
$GLOBALS['b07_antislash_observation'] = ['mail' => 0, 'http' => 0, 'transport_mail' => 0, 'transport_http' => 0];
add_filter('pre_wp_mail', static function ($value) {
    $GLOBALS['b07_antislash_observation']['mail']++;
    return $value;
}, -9999);
add_filter('pre_http_request', static function ($value) {
    $GLOBALS['b07_antislash_observation']['http']++;
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
