<?php

declare(strict_types=1);

require '/subject/a19/Analysis.php';

use Imagine\SubscriptionCoherence\Analysis;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$subs = [
    10 => ['status' => 'active', 'user' => 5, 'manual' => false, 'gateway' => 'fixture',
        'reference' => 'present', 'next' => 300, 'paid' => true],
    11 => ['status' => 'active', 'user' => 5, 'manual' => false, 'gateway' => 'fixture',
        'reference' => 'absent', 'next' => 100, 'paid' => false],
    12 => ['status' => 'on-hold', 'user' => 9, 'manual' => true, 'gateway' => 'cheque',
        'reference' => 'absent', 'next' => 100, 'paid' => false],
];
$members = [
    ['plan' => 20, 'user' => 5, 'status' => 'active', 'subscription' => 10],
    ['plan' => 20, 'user' => 5, 'status' => 'active', 'subscription' => 0],
    ['plan' => 20, 'user' => 9, 'status' => 'active', 'subscription' => 999],
];
$data = Analysis::analyse($subs, $members, 200);
$check('cross_table_counted_per_linked_membership', ($data['cross'] ?? null)
    === [['plan' => 20, 'subscription_status' => 'active', 'membership_status' => 'active', 'count' => 1]]);
$check('no_link_separate_from_dangling', ($data['subscriptions_without_membership'] ?? null)
    === [['status' => 'active', 'count' => 1], ['status' => 'on-hold', 'count' => 1]]
    && ($data['memberships_without_subscription'] ?? null) === [['plan' => 20, 'status' => 'active', 'count' => 1]]
    && ($data['memberships_missing_subscription'] ?? null) === [['plan' => 20, 'status' => 'active', 'count' => 1]]);
$check('multiple_active_accounts_not_number_of_records', ($data['multiple_active_subscription_accounts'] ?? null) === 1
    && ($data['multiple_active_membership_accounts'] ?? null) === 1
    && ($data['multiple_active_membership_accounts_by_plan'] ?? null) === [['plan' => 20, 'count' => 1]]);
$check('active_payment_date_and_paid_order_counts', ($data['automatic_without_saved_payment'] ?? null)
    === [['gateway' => 'fixture', 'count' => 1]] && ($data['active_past_next_payment'] ?? null) === 1
    && ($data['active_without_paid_order'] ?? null) === 1
    && ($data['manual_by_gateway'] ?? null) === [['gateway' => 'cheque', 'count' => 1]]);
$empty = Analysis::analyse([], [], 200);
$check('empty_site_has_zero_not_missing_counts', $empty['cross'] === []
    && $empty['multiple_active_subscription_accounts'] === 0 && $empty['active_without_paid_order'] === 0);
$boundary = $subs;
$boundary[11]['next'] = 200;
$boundary[11]['reference'] = 'unknown';
$boundary[11]['user'] = 0;
$boundary[11]['gateway'] = '/PRIVATE_CANARY';
$edge = Analysis::analyse($boundary, $members, 200);
$check('strict_clock_boundary_and_guests', $edge['active_past_next_payment'] === 0
    && $edge['multiple_active_subscription_accounts'] === 0);
$check('unknown_not_false_payment_absence', $edge['automatic_without_saved_payment'] === []
    && $edge['automatic_payment_reference_unknown'] === [['gateway' => 'autre', 'count' => 1]]);
$check('privacy_schema_contains_no_person_identifiers', !str_contains(json_encode($edge), 'CANARY')
    && !preg_match('/"(?:user|customer|subscription_id|order_id|id)"/', json_encode($edge)));
$check('every_metric_has_definition', count($data['definitions']) === count($data) - 1);
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
exit($result['exit_code']);
