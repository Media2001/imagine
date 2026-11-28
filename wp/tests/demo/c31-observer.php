<?php
// Sonde temporaire C31 pour formulaires natifs, aucune livraison fonctionnelle.
if (defined('WP_CLI') && WP_CLI) { return; }
add_action('init', static function (): void {
    if (get_option('imagine_demo_site') !== 'imagine-test-demo') { return; }
    $observed = ['http' => [], 'mail' => []];
    add_filter('pre_http_request', static function ($pre) use (&$observed) { $observed['http'][] = ['blocked', 'trace' => array_column(debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 14), 'function')];return new WP_Error('imagine_c31_probe', 'FICTIF'); }, PHP_INT_MAX);
    add_filter('pre_wp_mail', static function ($pre) use (&$observed) { $observed['mail'][] = 'blocked';return false; }, PHP_INT_MAX);
    if (isset($_GET['imagine_c31_witness'])) { wp_remote_get('https://example.invalid/');wp_mail('fictif@example.org', 'FICTIF', 'FICTIF'); }
    add_action('shutdown', static function () use (&$observed): void { echo '<!-- B13_OBSERVATION ' . base64_encode(wp_json_encode($observed)) . ' -->'; }, PHP_INT_MAX);
});
