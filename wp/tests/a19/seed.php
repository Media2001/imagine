<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
foreach (get_posts(['post_type' => 'wc_user_membership', 'post_status' => 'any', 'numberposts' => -1]) as $m) {
    wp_delete_post($m->ID, true);
}
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $s) {
    $s->delete(true);
}
$users = [];
for ($i = 0; $i < 3; $i++) {
    $users[] = wp_insert_user(['user_login' => 'a19-fictif-' . $i . '-PERSONAL_CANARY',
        'user_email' => 'a19-' . $i . '@example.org', 'user_pass' => wp_generate_password(40)]);
}
$plan = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_status' => 'publish',
    'post_title' => 'A19_PLAN_PRIVATE_CANARY']);
update_post_meta($plan, '_access_method', 'manual-only');
update_post_meta($plan, '_access_length', 'unlimited');
$subs = [];
foreach ([[$users[0], false, 'a19_fixture'], [$users[0], true, 'cheque'],
    [$users[1], false, 'a19_fixture'], [$users[2], true, 'bacs']] as $i => [$user, $manual, $gateway]) {
    $s = wcs_create_subscription(['customer_id' => $user, 'status' => 'pending', 'billing_period' => 'month',
        'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00']);
    if (is_wp_error($s)) {
        throw new RuntimeException('A19_FIXTURE_SUBSCRIPTION');
    }
    $s->set_payment_method($gateway);
    $s->set_requires_manual_renewal($manual);
    $s->set_billing_first_name('A19_PERSONAL_CANARY');
    $s->update_meta_data('_a19_payment_reference', $i === 0 ? 'A19_TOKEN_PRIVATE_CANARY' : '');
    $s->save();
    $s->update_status('active');
    if ($i === 3) {
        $s->update_status('on-hold');
    }
    $s->update_dates(['next_payment' => $i === 2 ? '2026-10-01 00:00:00' : '2026-12-26 00:00:00']);
    $subs[] = $s;
}
$paidParent = wc_create_order(['customer_id' => $users[0]]);
$paidParent->set_total('12.50');
$paidParent->save();
$paidParent->payment_complete('A19_TRANSACTION_PRIVATE_CANARY');
$subs[0]->set_parent_id($paidParent->get_id());
$subs[0]->save();
$paidRenewal = wcs_create_renewal_order($subs[1]);
if (is_wp_error($paidRenewal)) {
    throw new RuntimeException('A19_FIXTURE_RENEWAL');
}
$paidRenewal->set_total('12.50');
$paidRenewal->save();
$paidRenewal->payment_complete('A19_RENEWAL_PRIVATE_CANARY');
$coherent = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $users[0]]);
$link = new WC_Memberships_Integration_Subscriptions_User_Membership($coherent->get_id());
$link->set_subscription_id($subs[0]->get_id());
$coherent->update_status('active');
$orphan = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $users[2]]);
$orphan->update_status('active');
$stale = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $users[1]]);
$stale->update_status('active');
$dead = wcs_create_subscription(['customer_id' => $users[1], 'status' => 'pending',
    'billing_period' => 'month', 'billing_interval' => 1]);
$deadId = $dead->get_id();
$dead->delete(true);
// Deliberate inherited inconsistencies in the owned synthetic fixture, never site data.
update_post_meta($stale->get_id(), '_subscription_id', $deadId);
wp_insert_post(['post_type' => 'wc_user_membership', 'post_status' => 'wcm-active', 'post_parent' => $plan,
    'post_author' => $users[0], 'post_title' => 'A19_DUPLICATE_PRIVATE_CANARY']);
$token = new WC_Payment_Token_CC();
$token->set_user_id($users[0]);
$token->set_gateway_id('a19_fixture');
$token->set_token('A19_PAYMENT_PRIVATE_CANARY');
$token->set_card_type('visa');
$token->set_last4('4242');
$token->set_expiry_month('12');
$token->set_expiry_year('2030');
$token->save();
$subs[0]->add_payment_token($token);
update_option('a19_fixture_schema_enabled', 'yes');
$oracle = [
    'past_next_native' => wcs_get_subscription($subs[2]->get_id())->get_time('next_payment', 'gmt')
        === strtotime('2026-10-01 00:00:00 UTC'),
    'plan' => $plan,
    'coherent_link_native' => $link->get_subscription_id() === $subs[0]->get_id(),
    'stale_native_absent' => (new WC_Memberships_Integration_Subscriptions_User_Membership($stale->get_id()))
        ->get_subscription() === null,
    'paid_parent_native' => $paidParent->is_paid(), 'paid_renewal_native' => $paidRenewal->is_paid(),
    'renewal_native_link' => in_array($paidRenewal->get_id(), $subs[1]->get_related_orders('ids', 'any'), true),
    'subscriptions_native' => count(wcs_get_subscriptions(['subscriptions_per_page' => -1,
        'subscription_status' => 'any'])),
];
echo 'A19_JSON=' . json_encode($oracle) . "\n";
