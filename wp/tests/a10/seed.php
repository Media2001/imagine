<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$types = ['percent', 'fixed_cart', 'fixed_product', 'recurring_fee', 'recurring_percent', 'sign_up_fee', 'sign_up_fee_percent'];
$product = new WC_Product_Subscription();
$product->set_name('A10_PRODUCT_PRIVATE_CANARY');
$product->set_regular_price('30.00');
$product->save();
update_post_meta($product->get_id(), '_subscription_period', 'month');
update_post_meta($product->get_id(), '_subscription_period_interval', '1');
$excluded = new WC_Product_Simple();
$excluded->set_name('A10_OTHER_PRIVATE_CANARY');
$excluded->set_regular_price('20');
$excluded->save();
$category = wp_insert_term('A10_CATEGORY_PRIVATE_CANARY', 'product_cat');
$coupons = [];
$expected = [];
foreach ($types as $i => $type) {
    $code = 'a10-' . str_replace('_', '-', $type);
    $c = new WC_Coupon();
    $c->set_code($code);
    $c->set_discount_type($type);
    $c->set_amount('10.50');
    $c->set_date_created('2025-01-01T12:00:00Z');
    $c->set_date_expires('2035-01-01T00:00:00Z');
    $c->set_usage_count($i + 1);
    $c->set_usage_limit(50);
    $c->set_usage_limit_per_user(2);
    $c->set_limit_usage_to_x_items(3);
    $c->set_individual_use(true);
    $c->set_free_shipping(true);
    $c->set_exclude_sale_items(true);
    $c->set_minimum_amount('5.00');
    $c->set_maximum_amount('100.00');
    $c->set_product_ids([$product->get_id()]);
    $c->set_excluded_product_ids([$excluded->get_id()]);
    $c->set_product_categories([$category['term_id']]);
    $c->set_email_restrictions(['a10-private@example.org', '*@example.org']);
    $c->set_description('A10_PERSONAL_PRIVATE_CANARY');
    $c->save();
    if ($type === 'recurring_fee') {
        $c->update_meta_data('_wcs_number_payments', '3');
        $c->save();
    }
    $coupons[$type] = $c;
}
foreach (['expired', 'never-used', 'expired-never-used'] as $i => $code) {
    $c = new WC_Coupon();
    $c->set_code('a10-' . $code);
    $c->set_discount_type('percent');
    $c->set_amount('5');
    $c->set_usage_count($i === 0 ? 9 : 0);
    if ($i !== 1) {
        $c->set_date_expires('2000-01-01T00:00:00Z');
    }
    $c->save();
    $coupons[$code] = $c;
}
$attach = static function ($order, string $code, bool $duplicate = false): void {
    for ($i = 0; $i < ($duplicate ? 2 : 1); $i++) {
        $item = new WC_Order_Item_Coupon();
        $item->set_code($code);
        $item->set_discount('1.00');
        $order->add_item($item);
    }
    $order->save();
};
$fixtureSubscriptions = wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']);
$fixtureCustomer = current($fixtureSubscriptions)->get_customer_id();
foreach ($fixtureSubscriptions as $s) {
    $attach($s, 'a10-recurring-fee', true);
}
foreach (['pending', 'cancelled', 'expired'] as $status) {
    $s = wcs_create_subscription(['customer_id' => $fixtureCustomer, 'status' => 'pending', 'billing_period' => 'month', 'billing_interval' => 1]);
    if (is_wp_error($s)) {
        throw new RuntimeException('A10_FIXTURE_SUBSCRIPTION');
    }
    $s->set_billing_first_name('A10_PERSONAL_PRIVATE_CANARY');
    $s->set_billing_email('a10-private@example.org');
    $attach($s, 'a10-recurring-fee');
    if ($status !== 'pending') {
        $s->update_status($status);
    }
}
foreach ([['pending', '-1 day'], ['completed', '-2 days'], ['cancelled', '-3 days'], ['refunded', '-4 days'], ['pending', '-2 years'], ['pending', '+2 days'], ['trash', '-5 days']] as [$status, $offset]) {
    $o = wc_create_order();
    $o->set_date_created(gmdate('Y-m-d H:i:s', strtotime($offset)));
    $o->set_billing_first_name('A10_PERSONAL_PRIVATE_CANARY');
    $o->set_billing_email('a10-private@example.org');
    $attach($o, 'A10-RECURRING-FEE', true);
    $o->set_status($status);
    $o->save();
}
// Real native renewal proves coupon carry-over, without executing audit-side actions.
$active = current(wcs_get_subscriptions(['subscriptions_per_page' => 1, 'subscription_status' => 'active']));
$renewal = wcs_create_renewal_order($active);
if (is_wp_error($renewal)) {
    throw new RuntimeException('A10_FIXTURE_RENEWAL');
}
$renewal->set_date_created(gmdate('Y-m-d H:i:s', strtotime('-1 hour')));
$renewal->save();
$renewalCarries = in_array('a10-recurring-fee', array_map('strtolower', $renewal->get_coupon_codes()), true);
foreach ($coupons as $c) {
    $c = new WC_Coupon($c->get_id());
    $expected[$c->get_code()] = [
        'type' => $c->get_discount_type(), 'amount' => $c->get_amount(),
        'usage_count' => $c->get_usage_count(), 'usage_limit' => $c->get_usage_limit(),
        'usage_limit_per_user' => $c->get_usage_limit_per_user(), 'item_limit' => $c->get_limit_usage_to_x_items(),
        'allowed_email_count' => count($c->get_email_restrictions()),
        'product_ids' => $c->get_product_ids(), 'excluded_product_ids' => $c->get_excluded_product_ids(),
        'product_categories' => $c->get_product_categories(),
        'date_expires_utc' => $c->get_date_expires()?->date('Y-m-d\TH:i:s\Z'),
        'renewal_payment_limit' => (int) $c->get_meta('_wcs_number_payments'),
    ];
}
echo 'A10_JSON=' . json_encode(['expected' => $expected, 'renewal_carries_coupon' => $renewalCarries,
    'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC()->version, 'subscriptions' => WC_Subscriptions::$version]]) . "\n";
