<?php

declare(strict_types=1);

namespace Imagine\ScheduledTasks\Tests;

$library = dirname(__DIR__, 2) . '/outils/bascule/a29/Analysis.php';
require is_file($library) ? $library : '/subject/a29/Analysis.php';

use Imagine\ScheduledTasks\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$clock = '2026-11-26T12:00:00+00:00';
$now = Analysis::clock($clock)->getTimestamp();
$row = static fn(string $hook, int $time, string $status = 'pending'): array => [
    'hook' => $hook, 'timestamp' => $time, 'status' => $status,
];
$hook = 'woocommerce_scheduled_subscription_payment';
$check('closed_family_renewal', Analysis::family($hook) === 'renouvellement');
$check('closed_family_unknown_canary', Analysis::family('A29_PRIVATE_CANARY') === 'autre');
$check('no_prefix_guess', Analysis::family($hook . '_stripe') === 'autre');
foreach (Analysis::HOOKS as $name => $family) {
    $check('closed_map_' . count($checks), in_array($family, Analysis::FAMILIES, true)
        && Analysis::family($name) === $family);
}
$small = Analysis::analyse([
    $row($hook, $now - 1), $row($hook, $now),
    $row('woocommerce_scheduled_subscription_payment_retry', $now + 1),
    $row('woocommerce_scheduled_subscription_expiration', $now + 2),
    $row($hook, $now, 'failed'), $row('A29_PRIVATE_CANARY', $now + 3),
], $clock, false);
$check('exact_six_cases_pending', $small['pending'] === ['groups' => [], 'autres' => 5]);
$check('exact_six_cases_overdue', $small['overdue'] === ['groups' => [], 'autres' => 1]);
$check('failed_not_pending', $small['failed'] === ['groups' => [], 'autres' => 1]);
$check('renewal_not_retry', $small['renewal_weeks'] === ['groups' => [], 'autres' => 1]);
$check('rare_other_suppressed', $small['other_tasks'] === 'moins de cinq');
$check('unknown_extension_not_inferred', $small['other_active_extensions'] === 'attribution indéterminée');
$check('no_private_values_in_projection', !str_contains(json_encode($small), 'CANARY'));
$rows = [];
foreach ([-1, 0, 604799, 604800, 1209599, 1209600, 4838399, 4838400] as $offset) {
    for ($i = 0; $i < 5; $i++) {
        $rows[] = $row($hook, $now + $offset);
    }
}
$counts = Analysis::analyse($rows, $clock, false);
$check('week_lower_inclusive_upper_exclusive', $counts['renewal_weeks'] === ['groups' => [
    ['week' => 1, 'count' => 10], ['week' => 2, 'count' => 10],
    ['week' => 3, 'count' => 5], ['week' => 8, 'count' => 5],
], 'autres' => 0]);
$check('audit_time_not_wall_clock', $counts['overdue'] === ['groups' => [
    ['family' => 'renouvellement', 'count' => 5],
], 'autres' => 0]);
$empty = Analysis::analyse([], $clock, false);
$check('empty_observed_not_neutral', $empty['other_tasks'] === 0 && $empty['other_active_extensions'] === 0);
$unknown = Analysis::analyse([], $clock, true);
$check('all_import_counts_unknown', $unknown === array_fill_keys(Analysis::COUNTS, Analysis::UNKNOWN));
$check('k5_boundary_four', Analysis::pool(['renouvellement' => 4], 'family') === ['groups' => [], 'autres' => 4]);
$check('k5_boundary_five', Analysis::pool(['renouvellement' => 5], 'family') === ['groups' => [
    ['family' => 'renouvellement', 'count' => 5],
], 'autres' => 0]);
$check('all_rare_families_fused', Analysis::pool(['email' => 2, 'autre' => 3], 'family') === ['groups' => [], 'autres' => 5]);
$check('async_immediate_overdue', Analysis::analyse([$row('A29_PRIVATE_CANARY', 0)], $clock, false)['overdue']
    === ['groups' => [], 'autres' => 1]);
$check('ignore_terminal_and_running', Analysis::analyse([
    $row($hook, $now, 'complete'), $row($hook, $now, 'canceled'), $row($hook, $now, 'in-progress'),
], $clock, false) === $empty);
$timezone = date_default_timezone_get();
date_default_timezone_set('Pacific/Auckland');
$check('utc_independent_of_site_timezone', Analysis::analyse($rows, $clock, false) === $counts);
date_default_timezone_set($timezone);
foreach (['2026-02-30T12:00:00+00:00', '2026-11-26T12:00:00Z', '2026-11-26T12:00:00+01:00', 'CANARY'] as $bad) {
    try {
        Analysis::clock($bad);
        $check('invalid_clock_' . count($checks), false);
    } catch (\RuntimeException $error) {
        $check('invalid_clock_' . count($checks), $error->getMessage() === 'A29_CLOCK_INVALID');
    }
}
try {
    Analysis::analyse([$row($hook, $now, 'A29_STATUS_PRIVATE_CANARY')], $clock, false);
    $check('invalid_status_refused', false);
} catch (\RuntimeException $error) {
    $check('invalid_status_refused', $error->getMessage() === 'A29_DATA_UNSUPPORTED');
}
$exit = (int) in_array('FAIL', array_column($checks, 'status'), true);
if (($argv[1] ?? '') === '--pure') {
    echo 'A29_PURE_' . ($exit ? 'FAIL ' : 'OK ') . count($checks) . "\n";
} else {
    file_put_contents('/report/unit.json', json_encode(['checks' => $checks, 'exit_code' => $exit], JSON_PRETTY_PRINT) . "\n");
}
exit($exit);
