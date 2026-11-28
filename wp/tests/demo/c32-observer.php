<?php
// Sonde uniquement de recette C32, retirée dans finally.
if (defined('WP_CLI') && WP_CLI) { return; }
add_action('init', static function (): void {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') { return; }
    add_filter('pre_http_request', static fn () => new WP_Error('c32_offline', 'FICTIF'), PHP_INT_MAX);
    add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
    if (($_GET['c32_cookie'] ?? '') === 'header') { setcookie('c32_sonde_hors_liste', 'fictif', 0, '/'); }
    if (($_GET['c32_cookie'] ?? '') === 'script') {
        add_action('wp_footer', static function (): void { echo '<script>document.cookie="c32_sonde_hors_liste=fictif; path=/";</script>'; });
    }
}, 0);
