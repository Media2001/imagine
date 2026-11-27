<?php

declare(strict_types=1);

namespace Imagine\ArchiveTests;

$checks = [];
$check = static function (string $key, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$source = '/subject/a33/Analysis.php';
$check('analysis_exists', is_file($source));
if (is_file($source)) {
    require $source;
    $class = \Imagine\ArchiveWeight\Analysis::class;
    $empty = $class::files([], false);
    $check('empty_is_exact_zero', $empty === ['count' => 0, 'present' => 0, 'missing' => 0, 'known_bytes' => 0, 'total_bytes' => 0]);
    $known = $class::files([11, 13, 0], false);
    $check('known_stat_sizes_exact', $known === ['count' => 3, 'present' => 3, 'missing' => 0, 'known_bytes' => 24, 'total_bytes' => 24]);
    foreach ([false, true] as $imported) {
        $r = $class::files([11, null], $imported);
        $check('missing_separate_' . (int) $imported, $r['missing'] === 1 && $r['present'] === 1 && $r['count'] === 2);
        $check('missing_never_zero_' . (int) $imported, $r['total_bytes'] === ($imported ? 'inconnu après import' : 'inconnu fichiers absents') && $r['known_bytes'] === 11);
    }
    $mapping = ['numero_type' => 'secret_numero', 'article_type' => 'secret_article'];
    foreach (['secret_numero' => 'numero', 'secret_article' => 'article', 'post' => 'post', 'page' => 'page', 'product' => 'product', 'product_variation' => 'product_variation', 'PRIVATE_CANARY' => 'autre'] as $raw => $expected) {
        $check('closed_type_' . $expected, $class::type($raw, $mapping) === $expected);
    }
    foreach (['2024-01-01 12:00:00' => 2024, '0000-00-00 00:00:00' => 'inconnu', 'CANARY' => 'inconnu'] as $raw => $expected) {
        $check('utc_year_' . $expected, $class::year($raw) === $expected);
    }
}
$result = ['suite' => 'A33-pure', 'checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
echo 'A33_UNIT ' . count($checks) . "\n";
exit($result['exit_code']);
