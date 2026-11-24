<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$restricted = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'Fiction privee', 'post_content' => 'A03_PRIVATE_CONTENT_CANARY']);
$open = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'Fiction ouverte', 'post_content' => 'A03_OPEN_MARKER']);
$plan = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_status' => 'publish', 'post_title' => 'Plan fictif A03']);
update_post_meta($plan, '_access_method', 'manual-only');
update_post_meta($plan, '_access_length', 'unlimited');
wc_memberships()->get_rules_instance()->set_rules(['add' => [
    ['membership_plan_id' => $plan, 'active' => 'yes', 'rule_type' => 'content_restriction', 'content_type' => 'post_type', 'content_type_name' => 'post', 'object_ids' => [$restricted], 'access_schedule' => 'immediate'],
]]);
$users = [];
$membershipIds = [];
$subscriptionIds = [];
$memberStates = ['active', 'paused', 'expired', 'cancelled', 'pending'];
$subStates = ['active', 'on-hold', 'expired', 'cancelled', 'pending', 'pending-cancel'];
foreach ($subStates as $i => $state) {
    $uid = wp_insert_user(['user_login' => 'a03-fictif-' . $i, 'user_email' => 'a03-fictif-' . $i . '@example.org', 'user_pass' => wp_generate_password(40), 'display_name' => 'A03_PERSONAL_CANARY']);
    if (is_wp_error($uid)) {
        throw new RuntimeException('A03_SEED_USER');
    }
    $users[] = $uid;
    if (isset($memberStates[$i])) {
        $m = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $uid]);
        $m->update_status($memberStates[$i]);
        $membershipIds[$memberStates[$i]] = $m->get_id();
    }
    $s = wcs_create_subscription(['customer_id' => $uid, 'status' => 'pending', 'billing_period' => $i % 2 ? 'year' : 'month', 'billing_interval' => $i + 1, 'start_date' => '2025-01-01 00:00:00']);
    if (is_wp_error($s)) {
        throw new RuntimeException('A03_SEED_SUBSCRIPTION');
    }
    $s->set_payment_method($i % 2 ? 'bacs' : '');
    $s->set_requires_manual_renewal(true);
    $s->set_billing_email('a03-private@example.org');
    $s->set_billing_first_name('A03_PERSONAL_CANARY');
    $s->save();
    if ($state !== 'pending') {
        $s->update_status('active');
        $s->update_status($state);
    }
    if (in_array($state, ['active', 'on-hold'], true)) {
        $s->update_dates(['next_payment' => '2027-02-01 10:00:00']);
    }
    $subscriptionIds[] = $s->get_id();
}
foreach ([['2026-11-01', 'completed', '12.30'], ['2026-10-01', 'processing', '20.15'], ['2025-12-01', 'cancelled', '9.99'], ['2025-11-01', 'completed', '999.00']] as [$date, $state, $total]) {
    $order = wc_create_order(['customer_id' => $users[0]]);
    $order->set_status($state);
    $order->set_date_created($date . ' 12:00:00');
    $order->set_currency('EUR');
    $order->set_total($total);
    $order->set_billing_email('a03-private@example.org');
    $order->save();
}
$action = as_schedule_single_action(strtotime('2027-01-14 10:00:00 UTC'), 'a03_fixture_action', ['A03_PRIVATE_ARGS_CANARY'], 'a03');
WC_Install::create_pages();
$pages = ['home' => '/', 'open' => '/?p=' . $open, 'restricted' => '/?p=' . $restricted, 'shop' => '/?page_id=' . wc_get_page_id('shop'), 'cart' => '/?page_id=' . wc_get_page_id('cart'), 'checkout' => '/?page_id=' . wc_get_page_id('checkout'), 'account' => '/?page_id=' . wc_get_page_id('myaccount')];
echo 'A03_JSON=' . json_encode(['users' => $users, 'membership_ids' => $membershipIds, 'restricted' => $restricted, 'open' => $open, 'action' => $action, 'subscription_ids' => $subscriptionIds, 'pages' => $pages, 'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC()->version, 'subscriptions' => WC_Subscriptions::$version, 'memberships' => wc_memberships()->get_version()]]) . "\n";
