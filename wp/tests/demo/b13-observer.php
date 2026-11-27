<?php

declare(strict_types=1);

// Sonde temporaire limitée au site fictif, jamais livrée comme composant fonctionnel.
if (getenv('WP_ENVIRONMENT_TYPE') === 'production') {
    return;
}
add_action('template_redirect', static function (): void {
    if (get_option('imagine_demo_site') !== 'imagine-test-demo') {
        return;
    }
    $observed = ['http' => [], 'mail' => []];
    add_filter('pre_http_request', static function ($pre) use (&$observed) {
        $observed['http'][] = 'blocked';
        return new WP_Error('b13_probe', 'B13 blocked');
    }, PHP_INT_MAX);
    add_filter('pre_wp_mail', static function ($pre) use (&$observed) {
        $observed['mail'][] = 'blocked';
        return false;
    }, PHP_INT_MAX);
    if (isset($_GET['imagine_b13_witness'])) {
        wp_remote_get('https://example.invalid/');
        wp_mail('fictif@example.org', 'FICTIF', 'FICTIF');
    }
    add_action('shutdown', static function () use (&$observed): void {
        echo '<!-- B13_OBSERVATION ' . base64_encode(wp_json_encode($observed)) . ' -->';
    }, PHP_INT_MAX);
});
