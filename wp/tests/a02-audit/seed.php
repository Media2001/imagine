<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$uid = wp_insert_user(['user_login' => 'a02-fictif', 'user_email' => 'fiction-a02@example.org', 'user_pass' => wp_generate_password(40), 'display_name' => 'A02_PERSONAL_CANARY']);
if (is_wp_error($uid)) {
    throw new RuntimeException('A02_FIXTURE_USER');
}
$posts = [];
foreach ([2024, 2025, 2025] as $year) {
    $posts[] = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'A02_PERSONAL_CANARY', 'post_content' => 'A02_CONTENT_PRIVATE_CANARY', 'post_date' => $year . '-01-15 12:00:00']);
    update_post_meta(end($posts), 'a02_editorial_field', 'A02_FIELD_PRIVATE_CANARY');
}
$term = wp_insert_term('A02_TERM_PRIVATE_CANARY', 'category');
$plan = wp_insert_post(['post_type' => 'wc_membership_plan', 'post_status' => 'publish', 'post_title' => 'A02_PLAN_PRIVATE_CANARY']);
update_post_meta($plan, '_access_method', 'manual-only');
update_post_meta($plan, '_access_length', 'unlimited');
wc_memberships()->get_rules_instance()->set_rules(['add' => [
    ['membership_plan_id' => $plan, 'active' => 'yes', 'rule_type' => 'content_restriction', 'content_type' => 'post_type', 'content_type_name' => 'post', 'object_ids' => [$posts[0]], 'access_schedule' => 'immediate'],
    ['membership_plan_id' => $plan, 'active' => 'yes', 'rule_type' => 'content_restriction', 'content_type' => 'taxonomy', 'content_type_name' => 'category', 'object_ids' => [$term['term_id']], 'access_schedule' => '7 days'],
]]);
foreach (['active', 'expired', 'cancelled'] as $i => $state) {
    $u = $i === 0 ? $uid : wp_insert_user(['user_login' => 'a02-fictif-' . $i, 'user_email' => 'fiction-a02-' . $i . '@example.org', 'user_pass' => wp_generate_password(40)]);
    $m = wc_memberships_create_user_membership(['plan_id' => $plan, 'user_id' => $u]);
    $m->update_status($state);
}
$product = new WC_Product_Subscription();
$product->set_name('A02_PRODUCT_PRIVATE_CANARY');
$product->set_regular_price('12.50');
$product->save();
foreach (['_subscription_period' => 'month', '_subscription_period_interval' => '2', '_subscription_trial_length' => '7', '_subscription_trial_period' => 'day', '_subscription_sign_up_fee' => '4.50', '_subscription_payment_sync_date' => '15'] as $k => $v) {
    update_post_meta($product->get_id(), $k, $v);
}
$subs = [];
foreach (['active', 'on-hold', 'pending-cancel'] as $i => $status) {
    $s = wcs_create_subscription(['customer_id' => $uid, 'status' => 'pending', 'billing_period' => $i === 2 ? 'year' : 'month', 'billing_interval' => $i + 1]);
    if (is_wp_error($s)) {
        throw new RuntimeException('A02_FIXTURE_SUBSCRIPTION');
    }
    $s->set_billing_email('fiction-a02@example.org');
    $s->set_billing_first_name('A02_PERSONAL_CANARY');
    $s->set_payment_method('');
    $s->set_requires_manual_renewal(true);
    $s->add_product($product);
    $s->save();
    $s->update_status('active');
    if ($status !== 'active') {
        $s->update_status($status);
    }
    $subs[] = $s->get_id();
}
foreach ([2023, 2025, 2025] as $year) {
    $order = wc_create_order(['customer_id' => $uid]);
    $order->set_date_created($year . '-06-01 12:00:00');
    $order->set_billing_email('fiction-a02@example.org');
    $order->save();
}
update_option('a02_heavy_secret_setting', str_repeat('A02_SECRET_VALUE_CANARY', 5000), true);
update_option('woocommerce_bacs_settings', ['enabled' => 'yes', 'account' => 'A02_BANK_PRIVATE_CANARY']);
wp_schedule_event(time() + 3600, 'daily', 'a02_fixture_cron', ['A02_CRON_ARGUMENT_PRIVATE_CANARY']);
as_schedule_single_action(time() + 7200, 'a02_fixture_action', ['A02_ACTION_ARGUMENT_PRIVATE_CANARY'], 'a02');
as_schedule_single_action(time() - 7200, 'a02_fixture_failed', [], 'a02');
$active = get_option('active_plugins');
update_option('active_plugins', array_merge($active, ['fixture-builder/fixture-builder.php']));
set_site_transient('update_plugins', (object) ['last_checked' => time(), 'response' => ['fixture-builder/fixture-builder.php' => (object) ['new_version' => '3.0.0', 'requires' => '6.9', 'requires_php' => '8.2', 'last_updated' => '2020-01-01', 'package' => 'https://private.invalid/A02_PACKAGE_TOKEN_CANARY']]], 86400);
set_site_transient('update_themes', ['last_checked' => time(), 'response' => ['a02-theme' => ['new_version' => '2.0.0', 'requires' => '6.0', 'requires_php' => '8.2']]], 86400);
update_option('stylesheet', 'a02-theme');
update_option('template', 'a02-theme');
global $wpdb;
$wpdb->query("CREATE TABLE {$wpdb->prefix}orphan_fixture (id bigint PRIMARY KEY, private_value text)");
$wpdb->insert($wpdb->prefix . 'orphan_fixture', ['id' => 1, 'private_value' => 'A02_TABLE_PRIVATE_CANARY']);
$wpdb->query("UPDATE {$wpdb->prefix}actionscheduler_actions SET status='failed' WHERE hook='a02_fixture_failed'");
$rules = wc_memberships()->get_rules_instance()->get_rules_raw();
echo 'A02_JSON=' . json_encode([
    'plan_id' => $plan, 'product_id' => $product->get_id(),
    'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC()->version, 'subscriptions' => WC_Subscriptions::$version, 'memberships' => wc_memberships()->get_version()],
    'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),
    'subscriptions' => count($subs), 'rules' => count($rules), 'restriction_real' => wc_memberships_is_post_content_restricted($posts[0]),
    'gateway_ids' => array_keys(WC()->payment_gateways()->payment_gateways()),
]) . "\n";
