<?php

declare(strict_types=1);

use Imagine\ExternalDoors\Analysis;

$source = dirname(__DIR__, 2) . '/outils/bascule/a21/Analysis.php';
if (is_file($source)) {
    require_once $source;
} elseif (is_file('/subject/a21/Analysis.php')) {
    require_once '/subject/a21/Analysis.php';
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$check('pure_analysis_available', class_exists(Analysis::class));
if (class_exists(Analysis::class)) {
    $clock = new DateTimeImmutable('2026-11-26T00:00:00Z');
    $keys = Analysis::keys([
        ['permissions' => 'read', 'last_access' => null],
        ['permissions' => 'write', 'last_access' => '2025-11-25 23:59:59'],
        ['permissions' => 'read_write', 'last_access' => '2025-11-26 00:00:00'],
        ['permissions' => 'read', 'last_access' => '2026-11-01 00:00:00'],
    ], $clock, new DateTimeZone('UTC'));
    $check(
        'permissions_exact',
        $keys['by_permission'] === ['read' => 2, 'write' => 1, 'read_write' => 1, 'unknown' => 0]
    );
    $check('never_and_old_disjoint_strict_anniversary', $keys['never_used'] === 1
        && $keys['unused_twelve_months'] === 1 && $keys['last_access_unknown'] === 0 && $keys['total'] === 4);
    $check('webhook_analysis_available', method_exists(Analysis::class, 'webhooks'));
    if (method_exists(Analysis::class, 'webhooks')) {
        $hooks = Analysis::webhooks([
            ['status' => 'active', 'topic' => 'order.created', 'delivery_url' => 'https://outside.example.org/CANARY'],
            ['status' => 'paused', 'topic' => 'product.updated',
                'delivery_url' => 'https://outside.example.org/CANARY'],
            ['status' => 'active', 'topic' => 'order.created',
                'delivery_url' => 'http://SHOP.EXAMPLE.ORG.:8080/inside'],
            ['status' => 'disabled', 'topic' => 'action.CANARY', 'delivery_url' => 'https://shop.example.org'],
            ['status' => 'active', 'topic' => 'CANARY', 'delivery_url' => 'bad/CANARY'],
        ], 'https://shop.example.org/base');
        $check(
            'webhook_state_and_topic_counts',
            $hooks['by_status'] === ['active' => 3, 'paused' => 1, 'disabled' => 1, 'unknown' => 0]
            && $hooks['by_topic'] === ['order.created' => 2, 'product.updated' => 1, 'unknown' => 2]
        );
        $check(
            'active_destinations_domain_not_origin',
            $hooks['active_destination'] === ['same_domain' => 1, 'external_domain' => 1, 'unknown' => 1]
        );
        $check('custom_topic_and_url_canary_absent', !str_contains(json_encode($hooks), 'CANARY'));
    }
    $published = Analysis::webhooks([
        ['status' => 'active', 'topic' => 'product.published', 'delivery_url' => 'https://example.org']
    ], 'https://example.org');
    $check('native_product_published_topic_preserved', $published['by_topic'] === ['product.published' => 1]);
    $edge = Analysis::keys([
        ['permissions' => 'CANARY', 'last_access' => '2026-02-30 00:00:00'],
        ['permissions' => 'read', 'last_access' => '2027-01-01 00:00:00'],
        ['permissions' => 'write', 'last_access' => '0000-00-00 00:00:00'],
    ], $clock, new DateTimeZone('UTC'));
    $check('invalid_future_dates_and_permission_closed', $edge['by_permission']['unknown'] === 1
        && $edge['last_access_unknown'] === 2 && $edge['never_used'] === 1
        && !str_contains(json_encode($edge), 'CANARY'));
    $local = Analysis::keys([
        ['permissions' => 'read', 'last_access' => '2025-11-26 00:30:00']
    ], $clock, new DateTimeZone('Europe/Paris'));
    $check('last_access_interpreted_in_site_timezone', $local['unused_twelve_months'] === 1);
    $leap = Analysis::keys([
        ['permissions' => 'read', 'last_access' => '2023-02-28 00:00:00']
    ], new DateTimeImmutable('2024-02-29T00:00:00Z'), new DateTimeZone('UTC'));
    $check('leap_anniversary_clamped_not_march', $leap['unused_twelve_months'] === 0);
    $check('report_projection_available', method_exists(Analysis::class, 'report'));
    if (method_exists(Analysis::class, 'report')) {
        $unknown = Analysis::report([], [], [], true, $clock, new DateTimeZone('UTC'), 'https://example.org');
        $check('neutralisation_never_projects_historical_zero', $unknown === [
            'api_keys' => ['status' => 'inconnu après neutralisation', 'counts' => null],
            'webhooks' => ['status' => 'inconnu après neutralisation', 'counts' => null],
            'extension_store' => ['status' => 'inconnu après neutralisation', 'connected' => null],
        ]);
        $known = Analysis::report(
            [],
            [],
            ['auth' => ['access_token' => 'CANARY']],
            false,
            $clock,
            new DateTimeZone('UTC'),
            'https://example.org'
        );
        $check(
            'store_connection_boolean_only',
            $known['extension_store'] === ['status' => 'connu', 'connected' => true]
            && !str_contains(json_encode($known), 'CANARY')
        );
        $empty = Analysis::report([], [], [], false, $clock, new DateTimeZone('UTC'), 'https://example.org');
        $check('unconnected_not_invented', $empty['extension_store'] === ['status' => 'connu', 'connected' => false]
            && $empty['api_keys']['counts']['total'] === 0 && $empty['webhooks']['counts']['total'] === 0);
    }
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') !== __FILE__) {
    return $checks;
}
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (is_dir('/report')) {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
}
echo json_encode($result) . "\n";
exit($result['exit_code']);
