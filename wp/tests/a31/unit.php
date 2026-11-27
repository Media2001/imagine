<?php

declare(strict_types=1);

require '/subject/a31/Analysis.php';

use Imagine\OrderHistory\Analysis;

$checks = [];
$check = static function (string $key, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $key, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$order = static fn (string $nature, int $year = 2020): array => [
    'year' => $year, 'status' => 'completed', 'nature' => $nature,
    'orphan_renewal' => false, 'account_missing' => false, 'link_unknown' => false,
];
$one = Analysis::analyse([$order('renewal')], [], []);
$check('rare_four_no_label', $one['natures'] === ['groups' => [], 'autres' => 1]);
$check('oldest_rare_suppressed', $one['oldest_year'] === 'fusionne');
$five = Analysis::analyse(array_fill(0, 5, $order('renewal')), [], []);
$check('renewal_five', $five['natures'] === ['groups' => [['nature' => 'renewal', 'count' => 5]], 'autres' => 0]);
$check('oldest_five_exact', $five['oldest_year'] === 2020);
foreach (Analysis::NATURES as $nature) {
    $d = Analysis::analyse(array_fill(0, 5, $order($nature)), [], []);
    $check('nature_' . $nature, $d['natures']['groups'] === [['nature' => $nature, 'count' => 5]]);
}
$unknown = $order('none');
$unknown['status'] = 'A31_STATUS_PRIVATE_CANARY';
$d = Analysis::analyse(array_fill(0, 5, $unknown), [], []);
$check('closed_unknown_status', $d['statuses']['groups'] === [['year' => 2020, 'status' => 'autre', 'count' => 5]]);
$check('private_canary_absent', !str_contains(json_encode($d), 'CANARY'));
$unknown['nature'] = 'A31_UNKNOWN_PRIVATE_CANARY';
$d = Analysis::analyse(array_fill(0, 5, $unknown), [], []);
$check('unknown_nature_not_none', $d['natures']['groups'] === [['nature' => 'illisible', 'count' => 5]]);
$broken = $order('renewal');
$broken['orphan_renewal'] = true;
$broken['account_missing'] = true;
$d = Analysis::analyse(
    array_fill(0, 5, $broken),
    array_fill(0, 5, ['status' => 'active', 'parent_exists' => false]),
    []
);
$check('renewal_orphans_count_orders_not_links', $d['orphan_renewals']['groups'] === [
    ['metric' => 'renewals_missing_subscription', 'count' => 5],
]);
$check('missing_account_separate_from_guest', $d['structural_links']['groups'] === [
    ['metric' => 'living_without_parent', 'count' => 5], ['metric' => 'orders_missing_account', 'count' => 5],
]);
foreach (['pending', 'on-hold', 'pending-cancel', 'cancelled', 'expired', 'switched', 'draft'] as $status) {
    $d = Analysis::analyse([], [['status' => $status, 'parent_exists' => false]], []);
    $check('a19_excludes_' . $status, $d['structural_links'] === ['groups' => [], 'autres' => 0]);
}
$d = Analysis::analyse([$order('none', 2019), ...array_fill(0, 5, $order('none', 2020))], [], []);
$check('oldest_not_next_visible_year', $d['oldest_year'] === 'fusionne');
$d = Analysis::analyse([], [], array_fill(0, 5, ['year' => 2021]));
$check('refund_objects_separate', $d['refunds'] === ['groups' => [['year' => 2021, 'count' => 5]], 'autres' => 0]
    && $d['oldest_year'] === null && $d['years'] === ['groups' => [], 'autres' => 0]);
$badDate = $order('none');
$badDate['year'] = '2020-01-01';
$d = Analysis::analyse([$badDate], [], []);
$check('invalid_date_oldest_illisible', $d['oldest_year'] === 'illisible');
$neutral = Analysis::analyse(array_fill(0, 5, $broken), [], [], true);
$check('neutral_natures_unknown', $neutral['natures'] === Analysis::UNKNOWN);
$check('neutral_orphan_readable', $neutral['orphan_renewals'] === [
    'groups' => [['metric' => 'renewals_missing_subscription', 'count' => 5]], 'autres' => 0,
]);
$check('neutral_years_preserved', $neutral['years'] === $five['years'] && $neutral['oldest_year'] === 2020);
$check('empty_not_unknown', Analysis::analyse([], [], [])['oldest_year'] === null);
$code = (int) in_array('FAIL', array_column($checks, 'status'), true);
if (!defined('A31_PURE_PROBE')) {
    file_put_contents(
        '/report/unit.json',
        json_encode(['checks' => $checks, 'exit_code' => $code], JSON_PRETTY_PRINT) . "\n"
    );
}
if ($code !== 0) {
    exit($code);
}
if (!defined('A31_PURE_PROBE')) {
    echo 'A31_UNIT_OK ' . count($checks) . "\n";
}
