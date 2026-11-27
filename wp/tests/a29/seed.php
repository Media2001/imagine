<?php

declare(strict_types=1);

// Oracle setup ONLY in the disposable fictitious database, before fingerprints.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
global $wpdb;
$repetitions = (int) (getenv('A29_REPETITIONS') ?: 1);
if (!in_array($repetitions, [1, 5], true)) {
    throw new RuntimeException('A29_SEED_REPETITIONS');
}
$clock = new DateTimeImmutable('2026-11-26T12:00:00+00:00');
$now = $clock->getTimestamp();
$active = get_option('active_plugins', []);
$active[] = 'a29-inconnu/a29-inconnu.php';
update_option('active_plugins', array_values(array_unique($active)));
update_option('timezone_string', 'Pacific/Auckland');
$sub = wcs_create_subscription(['status' => 'pending', 'billing_period' => 'month', 'billing_interval' => 1]);
if (is_wp_error($sub)) {
    throw new RuntimeException('A29_SEED_SUBSCRIPTION');
}
// All scheduler changes below belong to fixture preparation, not the subject.
$wpdb->query("DELETE FROM {$wpdb->prefix}actionscheduler_logs");
$wpdb->query("DELETE FROM {$wpdb->prefix}actionscheduler_actions");
$wpdb->query("DELETE FROM {$wpdb->prefix}actionscheduler_claims");
$store = ActionScheduler::store();
if (get_class($store) !== 'ActionScheduler_DBStore') {
    throw new RuntimeException('A29_SEED_STORE');
}
$expected = [];
$cron = ['version' => 2];
$renewal = 'woocommerce_scheduled_subscription_payment';
for ($n = 0; $n < $repetitions; $n++) {
    $args = ['subscription_id' => $sub->get_id(), 'private' => 'A29_ARGUMENT_PRIVATE_CANARY_' . $n];
    $cases = [];
    foreach ([-1, 0, 604799, 604800, 1209599, 1209600, 4838399, 4838400] as $offset) {
        $cases[] = [$renewal, $now + $offset, 'pending'];
    }
    $cases[] = ['woocommerce_scheduled_subscription_payment_retry', $now + 10, 'pending'];
    $cases[] = ['woocommerce_scheduled_subscription_expiration', $now + 20, 'pending'];
    $cases[] = [$renewal, $now - 500, 'failed'];
    $cases[] = ['A29_UNKNOWN_ACTIVE_PRIVATE_CANARY', $now + 30, 'pending'];
    $cases[] = ['A29_UNKNOWN_ORPHAN_PRIVATE_CANARY', $now + 40, 'pending'];
    foreach ($cases as [$hook, $time, $status]) {
        $id = as_schedule_single_action($time, $hook, $args, 'a29-fictif', false);
        if (!$id) {
            throw new RuntimeException('A29_SEED_ACTION');
        }
        if ($status === 'failed') {
            $store->mark_failure($id);
        }
        $native = $store->fetch_action($id);
        $date = $native->get_schedule()->get_date();
        if (
            $store->get_status($id) !== $status || $native->get_hook() !== $hook
            || $date->getTimestamp() !== $time || $native->get_args() !== $args
        ) {
            throw new RuntimeException('A29_SEED_NATIVE_READBACK');
        }
        $expected[$status] = ($expected[$status] ?? 0) + 1;
    }
    $cronCases = [[$renewal, $now + 604800], ['wp_1_wc_emailer_cron', $now + 60], ['wp_version_check', $now - 2]];
    foreach ($cronCases as [$hook, $time]) {
        $cron[$time][$hook][md5(serialize($args))] = ['schedule' => false, 'args' => $args];
    }
}
// The installed safety MU refuses pre_schedule_event. Seed the native storage,
// then read through the real WordPress reader instead of weakening that guard.
update_option('cron', $cron);
$read = _get_cron_array();
$cronCount = 0;
foreach ($read as $hooks) {
    foreach ($hooks as $events) {
        $cronCount += count($events);
    }
}
if ($cronCount !== 3 * $repetitions || $expected !== ['pending' => 12 * $repetitions, 'failed' => $repetitions]) {
    throw new RuntimeException('A29_SEED_COUNTS');
}
$stored = $wpdb->get_results(
    "SELECT status,COUNT(*) AS n FROM {$wpdb->prefix}actionscheduler_actions GROUP BY status",
    ARRAY_A
);
$actual = [];
foreach ($stored as $row) {
    $actual[$row['status']] = (int) $row['n'];
}
ksort($actual);
ksort($expected);
if ($actual !== $expected) {
    throw new RuntimeException('A29_SEED_SQL_COUNTS');
}
echo "A29_SEED_OK\n";
