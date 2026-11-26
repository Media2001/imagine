<?php

declare(strict_types=1);

use Imagine\SubscriptionPrices\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$path = dirname(__DIR__, 2) . '/outils/bascule/a20/Analysis.php';
if (!is_file($path)) {
    $path = '/subject/a20/Analysis.php';
}
$check('pure_analysis_available', is_file($path));
if (is_file($path)) {
    require_once $path;
    $empty = Analysis::analyse([], 'EUR');
    $check('empty_counts_explicit', $empty['live_subscriptions'] === 0 && $empty['products'] === []
        && $empty['countries'] === [] && $empty['zero_recurring_total'] === 0);
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') !== __FILE__) {
    return $checks;
}
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
exit($result['exit_code']);
