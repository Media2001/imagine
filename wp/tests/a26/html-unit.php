<?php

declare(strict_types=1);

// Native HTML bank: invoked by the parent in the disposable WordPress fixture, never php -n.
require '/subject/a26/Analysis.php';

use Imagine\ThirdParties\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
try {
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
    $check(
        'html_quoted_gt_real_youtube',
        Analysis::services(Analysis::htmlUrls(
            '<iframe title="a > b" src="https://www.youtube.com/embed/A26_QUOTED_PRIVATE_CANARY"></iframe>'
        ), 'example.org') === ['youtube']
    );
    $check(
        'html_title_src_no_phantom_vimeo',
        Analysis::services(Analysis::htmlUrls(
            '<img title=\'src="https://vimeo.com/123"\' src="/local.png">'
        ), 'example.org') === []
    );
    $check(
        'ordinary_url_anchor_text_not_autoembed',
        Analysis::htmlUrls('<a href="/local">https://vimeo.com/123</a>') === []
    );
    $check(
        'literal_standalone_urls_not_autoembeds',
        Analysis::htmlUrls("<pre title=\"a > b\">\nhttps://vimeo.com/123\n</pre>"
            . "<!--\nhttps://vimeo.com/123\n-->") === []
    );
    $check(
        'raw_script_text_not_parsed_as_resource',
        Analysis::htmlUrls('<script>const x = \'<iframe src="https://vimeo.com/123">\';</script>') === []
    );
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'detail' => get_class($error)];
}
$result = ['suite' => 'A26-native-HTML', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
echo json_encode($result, JSON_PRETTY_PRINT) . "\n";
exit($result['exit_code']);
