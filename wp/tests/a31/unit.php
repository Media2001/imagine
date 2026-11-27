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
$check('rare_one_no_label', $one['natures'] === ['groups' => [], 'autres' => 1]);
$four = Analysis::analyse(array_fill(0, 4, $order('renewal')), [], []);
$check('rare_four_no_label', $four['natures'] === ['groups' => [], 'autres' => 4]);
$check('oldest_four_suppressed', $four['oldest_year'] === 'fusionne');
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
$check('renewal_orphans_count_orders_not_links', $d['orphan_renewals'] === 5);
$check('missing_account_separate_from_guest', $d['living_without_parent'] === 5 && $d['orders_missing_account'] === 5);
foreach (['pending', 'on-hold', 'pending-cancel', 'cancelled', 'expired', 'switched', 'draft'] as $status) {
    $d = Analysis::analyse([], [['status' => $status, 'parent_exists' => false]], []);
    $check('a19_excludes_' . $status, $d['living_without_parent'] === 0);
}
$d = Analysis::analyse([$order('none', 2019), ...array_fill(0, 5, $order('none', 2020))], [], []);
$check('oldest_not_next_visible_year', $d['oldest_year'] === 'fusionne');
$d = Analysis::analyse([], [], array_fill(0, 5, ['year' => 2021]));
$check(
    'refund_objects_separate',
    $d['refunds'] === ['total' => 5, 'groups' => [['year' => 2021, 'count' => 5]], 'autres' => 0]
    && $d['oldest_year'] === null && $d['years'] === ['groups' => [], 'autres' => 0]
);
$badDate = $order('none');
$badDate['year'] = '2020-01-01';
$d = Analysis::analyse([$badDate], [], []);
$check('invalid_date_oldest_illisible', $d['oldest_year'] === 'illisible');
$neutral = Analysis::analyse(array_fill(0, 5, $broken), [], [], true);
$check('neutral_natures_unknown', $neutral['natures'] === Analysis::UNKNOWN);
$check('neutral_orphan_readable', $neutral['orphan_renewals'] === 5);
$check('neutral_years_preserved', $neutral['years'] === $five['years'] && $neutral['oldest_year'] === 2020);
$check('empty_not_unknown', Analysis::analyse([], [], [])['oldest_year'] === null);
// Fusion 08h58: scalar anomalies remain exact independently, not K5 cells.
$metrics = ['orphan_renewals', 'living_without_parent', 'orders_missing_account', 'orders_link_unknown'];
foreach ($metrics as $metric) {
    foreach ([0, 1, 4, 5] as $count) {
        foreach ([false, true] as $mixed) {
            $orders = [];
            $subs = [];
            $expectedLinks = array_fill_keys($metrics, 0);
            foreach ($metrics as $otherMetric) {
                $n = $otherMetric === $metric ? $count : ($mixed ? 4 : 0);
                $expectedLinks[$otherMetric] = $n;
                for ($i = 0; $i < $n; $i++) {
                    if ($otherMetric === 'living_without_parent') {
                        $subs[] = ['status' => 'active', 'parent_exists' => false];
                    } else {
                        $entry = $order('none');
                        $flag = ['orphan_renewals' => 'orphan_renewal',
                            'orders_missing_account' => 'account_missing', 'orders_link_unknown' => 'link_unknown'];
                        $entry[$flag[$otherMetric]] = true;
                        $orders[] = $entry;
                    }
                }
            }
            $result = Analysis::analyse($orders, $subs, []);
            foreach ($expectedLinks as $key => $value) {
                $check(
                    'scalar_' . $metric . '_' . $count . '_' . ($mixed ? 'mixed' : 'alone') . '_' . $key,
                    ($result[$key] ?? null) === $value
                );
            }
        }
    }
}
foreach ([0, 1, 4, 5] as $count) {
    $result = Analysis::analyse([], [], array_fill(0, $count, ['year' => 2021]));
    $check('refund_exact_total_' . $count, ($result['refunds']['total'] ?? null) === $count);
    $check('refund_rare_year_' . $count, $result['refunds']['groups'] === ($count >= 5
        ? [['year' => 2021, 'count' => $count]] : []));
}
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
