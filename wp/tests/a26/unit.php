<?php

declare(strict_types=1);

$root = is_dir('/subject/a26') ? '/subject/a26' : dirname(__DIR__, 2) . '/outils/bascule/a26';
require $root . '/Analysis.php';

use Imagine\ThirdParties\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
try {
    $map = Analysis::plugins();
    $active = array_keys($map);
    $families = Analysis::families($active, serialize(['measurementID' => 'A26_ID_PRIVATE_CANARY']), false, []);
    $check('ten_closed_families', count($families) === 10);
    foreach ($families as $family => $row) {
        $check(
            'exact_count_' . $family,
            $row['active'] === count(array_filter($map, static fn(string $f): bool => $f === $family))
        );
    }
    $check('service_identifier_present_only_boolean', $families['mesure']['identifier'] === 'oui'
        && !str_contains(json_encode($families), 'CANARY'));
    $only = ['google-site-kit/google-site-kit.php'];
    $check('absent_identifier_non', Analysis::families($only, null, false, [])['mesure']['identifier'] === 'non');
    $check(
        'empty_identifier_non',
        Analysis::families($only, serialize(['measurementID' => '']), false, [])['mesure']['identifier'] === 'non'
    );
    $check(
        'malformed_settings_illisible',
        Analysis::families($only, 'a:broken', false, [])['mesure']['identifier'] === 'illisible'
    );
    $check(
        'object_settings_never_instantiated',
        Analysis::families($only, 'O:8:"stdClass":0:{}', false, [])['mesure']['identifier'] === 'illisible'
    );
    $check(
        'array_identifier_illisible',
        Analysis::families($only, serialize(['measurementID' => ['x']]), false, [])['mesure']['identifier']
            === 'illisible'
    );
    $check(
        'unknown_plugin_not_classified',
        Analysis::families(['A26_PLUGIN_PRIVATE_CANARY/x.php'], null, false, [])['mesure']['active'] === 0
    );
    $check(
        'duplicate_active_not_counted_twice',
        Analysis::families([...$only, ...$only], null, false, [])['mesure']['active'] === 1
    );
    $n = Analysis::families([], null, true, $only);
    $check(
        'disabled_import_not_zero',
        $n['mesure'] === ['active' => Analysis::UNKNOWN, 'identifier' => Analysis::UNKNOWN]
    );
    $check('unaffected_family_count_preserved', $n['carte'] === ['active' => 0, 'identifier' => 'non']);
    $check(
        'unreadable_marker_conservative_unknown',
        Analysis::families([], null, true, null)['pixel']['active'] === Analysis::UNKNOWN
    );
    $urls = ['https://www.youtube.com/embed/A26_ID_PRIVATE_CANARY', '//youtu.be/second',
        'https://vimeo.com/123', 'https://A26_DOMAIN_PRIVATE_CANARY.invalid/a',
        'https://example.org/local', 'javascript:alert(1)', '/relative',
        'https://youtube.com.A26_DOMAIN_PRIVATE_CANARY.invalid/embed/1'];
    $services = Analysis::services($urls, 'example.org');
    $check('closed_service_once_per_content', $services === ['youtube', 'vimeo', 'autre']);
    $check(
        'host_boundary_no_spoof',
        Analysis::services(['https://notyoutube.com/embed/1'], 'example.org') === ['autre']
    );
    $check(
        'case_trailing_dot_supported',
        Analysis::services(['https://WWW.YOUTUBE.COM./embed/1'], 'example.org') === ['youtube']
    );
    $html = '<iframe src="https://youtube.com/embed/a"></iframe><iframe src="https://youtube.com/embed/b"></iframe>'
        . '<a href="https://vimeo.com/123">ordinary link</a><img src="https://A26_DOMAIN_PRIVATE_CANARY.invalid/p.png">'
        . '<audio src="/local.mp3"></audio>';
    $check(
        'html_resources_not_ordinary_links',
        Analysis::services(Analysis::htmlUrls($html), 'example.org') === ['youtube', 'autre']
    );
    $check(
        'plain_oembed_line',
        Analysis::services(Analysis::htmlUrls("\nhttps://vimeo.com/123\n"), 'example.org') === ['vimeo']
    );
    $literalExample = '<pre><iframe src="https://vimeo.com/1"></iframe></pre>'
        . '<!-- <iframe src="https://vimeo.com/2"></iframe> -->';
    $check('code_and_comments_not_resources', Analysis::htmlUrls($literalExample) === []);
    $rows = [['year' => 2026, 'services' => ['youtube', 'youtube', 'autre'], 'selected' => true],
        ['year' => 2025, 'services' => ['youtube'], 'selected' => false]];
    $year = Analysis::content($rows, false, false);
    $check('content_service_deduplicated', $year['all']['youtube'] === 2 && $year['all']['autre'] === 1);
    $check('annual_fallback_sorted', array_column($year['selection']['years'], 'year') === [2025, 2026]);
    $last = Analysis::content($rows, true, false);
    $check('last_ten_selection_no_ids', $last['selection']['mode'] === 'dix_derniers'
        && $last['selection']['last_ten']['youtube'] === 1 && $last['selection']['years'] === []);
    $check(
        'neutral_content_unknown_possible_whole_value_scrub',
        Analysis::content($rows, false, true) === Analysis::UNKNOWN
    );
    $check('no_canary_in_any_aggregate', !str_contains(json_encode([$year, $families, $services]), 'CANARY'));
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'detail' => get_class($error)];
}
$result = ['suite' => 'A26-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
if (getenv('A26_PURE_INCLUDE') !== '1') {
    file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
    echo 'A26_UNIT ' . count($checks) . "\n";
    exit($result['exit_code']);
}
