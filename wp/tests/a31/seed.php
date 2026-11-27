<?php

declare(strict_types=1);

// Oracle-only fixture setup; all records invented. Never called by the subject.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
add_filter('pre_http_request', static fn () => new WP_Error('a31_offline'), PHP_INT_MAX);
register_post_status('wc-a31canary', ['public' => true, 'label' => 'A31_STATUS_PRIVATE_CANARY']);
add_filter('wc_order_statuses', static fn (array $s): array => $s + ['wc-a31canary' => 'A31_STATUS_PRIVATE_CANARY']);
global $wpdb;
$hpos = Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
$rows = $wpdb->get_results($hpos
    ? "SELECT id AS object_id FROM {$wpdb->prefix}wc_orders"
        . " WHERE type IN ('shop_order','shop_subscription','shop_order_refund')"
    : "SELECT ID AS object_id FROM {$wpdb->posts}"
        . " WHERE post_type IN ('shop_order','shop_subscription','shop_order_refund')");
foreach ($rows as $row) {
    $object = wc_get_order((int) $row->object_id);
    if ($object) {
        $object->delete(true);
    }
}
$repetitions = (int) (getenv('A31_REPETITIONS') ?: 1);
if (!in_array($repetitions, [1, 5], true)) {
    throw new RuntimeException('A31_SEED_REPETITIONS');
}
$makeOrder = static function (int $year, int $user = 0): WC_Order {
    $o = wc_create_order(['customer_id' => $user, 'status' => 'completed']);
    if (is_wp_error($o)) {
        throw new RuntimeException('A31_SEED_ORDER');
    }
    $o->set_date_created($year . '-06-15T12:00:00+00:00');
    $o->set_billing_first_name('A31_ACCOUNT_PRIVATE_CANARY');
    $o->set_billing_email('a31-fictif@example.org');
    $o->set_total('97.31');
    $o->save();
    return $o;
};
$fixtureUser = get_user_by('login', 'a02-fictif');
if (!$fixtureUser instanceof WP_User) {
    throw new RuntimeException('A31_SEED_CUSTOMER');
}
$makeSub = static function (int $parent, string $status) use ($fixtureUser): WC_Subscription {
    // Installed WCS refuses guest subscriptions, even if the original order is a guest order.
    $sub = wcs_create_subscription(['order_id' => $parent, 'customer_id' => $fixtureUser->ID,
        'status' => 'pending', 'billing_period' => 'month',
        'billing_interval' => 1, 'start_date' => '2020-01-01 00:00:00']);
    if (is_wp_error($sub)) {
        throw new RuntimeException('A31_SEED_SUBSCRIPTION');
    }
    $sub->set_payment_method('');
    $sub->set_requires_manual_renewal(true);
    $sub->save();
    $sub->update_status($status);
    return $sub;
};
$store = WCS_Related_Order_Store::instance();
$metrics = ['orphan_renewals', 'living_without_parent', 'orders_missing_account', 'orders_link_unknown'];
$case = getenv('A31_SCALAR_CASE');
if (is_string($case) && $case !== '') {
    $parts = explode(':', $case);
    if (count($parts) !== 3 || !in_array($parts[0], $metrics, true)
        || !in_array($parts[1], ['0', '1', '4', '5'], true) || !in_array($parts[2], ['alone', 'mixed'], true)) {
        throw new RuntimeException('A31_SEED_SCALAR_CASE');
    }
    foreach ($metrics as $metric) {
        $count = $metric === $parts[0] ? (int) $parts[1] : ($parts[2] === 'mixed' ? 4 : 0);
        for ($i = 0; $i < $count; $i++) {
            if ($metric === 'living_without_parent') {
                $makeSub(0, 'active');
                continue;
            }
            $entry = $makeOrder(2020);
            if ($metric === 'orphan_renewals') {
                $entry->add_meta_data('_subscription_renewal', 987654321, false);
            } elseif ($metric === 'orders_missing_account') {
                $entry->set_customer_id(987654321);
            } else {
                $entry->add_meta_data('_a31_fixture_unreadable', 'yes', true);
            }
            $entry->save();
        }
    }
    echo "A31_SEED_OK\n";
    return;
}
update_option('timezone_string', 'Europe/Brussels');
for ($n = 0; $n < $repetitions; $n++) {
    $parent = $makeOrder(2018);
    // Local January 1 is UTC December 31: oldest must be 2017, never 2018.
    $parent->set_date_created('2018-01-01T00:30:00+01:00');
    $parent->save();
    $sub = $makeSub($parent->get_id(), 'active');
    foreach (['renewal' => 2019, 'switch' => 2020, 'resubscribe' => 2020] as $type => $year) {
        $order = $makeOrder($year);
        if ($type === 'renewal') {
            // Local December 31 is UTC January 1: bucket must be 2019.
            $order->set_date_created('2018-12-31T23:30:00-01:00');
            $order->save();
        }
        $store->add_relation($order, $sub, $type);
    }
    $standalone = $makeOrder(2020);
    $trash = $makeSub(0, 'active');
    $trashId = $trash->get_id();
    $store->add_relation($standalone, $trash, 'renewal');
    $trash->delete(false);
    $trashed = wcs_get_subscription($trashId);
    if (!$trashed instanceof WC_Subscription || $trashed->get_status('edit') !== 'trash') {
        throw new RuntimeException('A31_SEED_TRASH');
    }
    $orphan = $makeOrder(2020);
    $orphan->add_meta_data('_subscription_renewal', 987654321, false);
    $orphan->save();
    $makeSub(0, 'active');
    $makeSub(0, 'cancelled');
    $user = wp_insert_user(['user_login' => 'a31-fictif-' . $repetitions . '-' . $n,
        'user_email' => 'a31-' . $repetitions . '-' . $n . '@example.org', 'user_pass' => wp_generate_password(40)]);
    if (is_wp_error($user)) {
        throw new RuntimeException('A31_SEED_ACCOUNT');
    }
    $makeOrder(2020, (int) $user);
    $wpdb->delete($wpdb->users, ['ID' => $user]);
    $wpdb->delete($wpdb->usermeta, ['user_id' => $user]);
    $unknown = $makeOrder(2020);
    $unknown->set_status('a31canary');
    $unknown->save();
    $opaque = $makeOrder(2020);
    $opaque->add_meta_data('_subscription_renewal', 'A31_LINK_PRIVATE_CANARY', false);
    $opaque->save();
    $extension = $makeOrder(2020);
    $extension->add_meta_data('_subscription_stripe_subscription_id', $sub->get_id(), false);
    $extension->save();
    $refund = new WC_Order_Refund();
    $refund->set_parent_id($standalone->get_id());
    $refund->set_date_created('2021-03-04T05:06:07+00:00');
    $refund->set_amount('9.31');
    $refund->set_reason('A31_REFUND_PRIVATE_CANARY');
    $refund->save();
}
echo "A31_SEED_OK\n";
