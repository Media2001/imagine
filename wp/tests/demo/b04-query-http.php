<?php

declare(strict_types=1);

// Temporary owned HTTP front controller, removed after the measured real requests.
// SQL strings, content, cookies and credentials are never written or exposed.
define('WP_USE_THEMES', true);
define('SAVEQUERIES', true);
$root = dirname(__DIR__, 2);
$_GET = [];
$_POST = [];
$_REQUEST = [];
$_SERVER['QUERY_STRING'] = '';
$_SERVER['REQUEST_URI'] = '/numeros/b04-temoin-fictif-20-articles/';
$_SERVER['SCRIPT_NAME'] = '/index.php';
$_SERVER['PHP_SELF'] = '/index.php';
$_SERVER['SCRIPT_FILENAME'] = $root . '/index.php';
require $root . '/wp-load.php';
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || rtrim(home_url(), '/') !== 'http://192.168.129.32:8085'
    || !in_array($_SERVER['REQUEST_METHOD'] ?? '', ['GET', 'HEAD'], true)) {
    http_response_code(403);
    exit;
}
$fixture = get_option('imagine_b04_fixture', []);
$issue = (int) ($fixture['witness'] ?? 0);
if (!$issue || get_post_meta($issue, '_imagine_b04_fixture', true) !== 'issue-v1') {
    http_response_code(404);
    exit;
}
$beforeTemplate = 0;
add_action('template_redirect', static function () use (&$beforeTemplate): void {
    $beforeTemplate = get_num_queries();
}, PHP_INT_MAX);
ob_start(static function (string $html) use (&$beforeTemplate, $issue): string {
    header('X-Imagine-B04-Queries: ' . get_num_queries());
    header('X-Imagine-B04-Template-Queries: ' . (get_num_queries() - $beforeTemplate));
    header('X-Imagine-B04-Issue: ' . $issue);
    return $html;
});
wp();
require $root . '/wp-includes/template-loader.php';
