<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
update_option('timezone_string', 'Europe/Brussels');
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
$now = new DateTimeImmutable('2026-11-25T12:00:00Z');
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
foreach (['winter' => '01-15', 'summer' => '07-15'] as $season => $day) {
    $c = new WC_Coupon();
    $c->set_code('a10-season-' . $season);
    $c->set_discount_type('fixed_cart');
    $c->set_amount('1');
    $c->set_usage_count(1);
    $c->set_date_created('2025-' . $day . 'T12:00:00Z');
    $c->set_date_expires('2035-' . $day . 'T00:00:00Z');
    $c->save();
    $coupons[$season] = $c;
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
    $o->set_date_created($now->modify($offset)->format('Y-m-d\TH:i:s\Z'));
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
$renewal->set_date_created($now->modify('-1 hour')->format('Y-m-d\TH:i:s\Z'));
$renewal->save();
$renewalCarries = in_array('a10-recurring-fee', array_map('strtolower', $renewal->get_coupon_codes()), true);
// Native historical coupon items survive deletion/renaming of their coupon record.
foreach (['deleted', 'renamed'] as $kind) {
    $c = new WC_Coupon();
    $c->set_code('a10-' . $kind . '-old');
    $c->set_discount_type('recurring_fee');
    $c->set_amount('2');
    $c->save();
    $attach($active, $c->get_code(), true);
    if ($kind === 'deleted') {
        $c->delete(true);
    } else {
        $c->set_code('a10-renamed-new');
        $c->save();
        $coupons['renamed-new'] = $c;
    }
}
$orderOnly = wc_create_order();
$orderOnly->set_date_created($now->modify('-1 hour')->format('Y-m-d\TH:i:s\Z'));
$attach($orderOnly, 'a10-order-only-old', true);
$boundaryOrders = [];
foreach (['from' => '2025-11-25T12:00:00Z', 'to' => '2026-11-25T12:00:00Z'] as $edge => $instant) {
    foreach ([-1, 0, 1] as $delta) {
        $label = $edge . '-' . ($delta < 0 ? 'before' : ($delta > 0 ? 'after' : 'equal'));
        $c = new WC_Coupon();
        $c->set_code('a10-boundary-order-' . $label);
        $c->set_discount_type('percent');
        $c->set_amount('1');
        $c->set_usage_count(1);
        $c->save();
        $coupons[$label] = $c;
        $o = wc_create_order();
        $date = (new DateTimeImmutable($instant))->modify(sprintf('%+d seconds', $delta));
        $o->set_date_created($date->format('Y-m-d\TH:i:s\Z'));
        $attach($o, $c->get_code(), true);
        $boundaryOrders[$c->get_code()] = (int) ($edge === 'from' ? $delta >= 0 : $delta <= 0);
    }
}
$boundaryExpiry = [];
foreach ([-1, 0, 1] as $delta) {
    $c = new WC_Coupon();
    $c->set_code('a10-boundary-expiry-' . ($delta < 0 ? 'before' : ($delta > 0 ? 'after' : 'equal')));
    $c->set_discount_type('percent');
    $c->set_amount('1');
    $c->set_usage_count(1);
    $c->set_date_expires($now->getTimestamp() + $delta);
    $c->save();
    $coupons[$c->get_code()] = $c;
    $boundaryExpiry[$c->get_code()] = $delta < 0;
}
$legacyExpiry = [];
foreach (['winter' => '2035-01-15', 'summer' => '2035-07-15'] as $season => $day) {
    $c = new WC_Coupon();
    $c->set_code('a10-legacy-' . $season);
    $c->set_discount_type('percent');
    $c->set_amount('1');
    $c->set_usage_count(1);
    $c->save();
    delete_post_meta($c->get_id(), 'date_expires');
    update_post_meta($c->get_id(), 'expiry_date', $day);
    $coupons['legacy-' . $season] = new WC_Coupon($c->get_id());
    $legacyExpiry[$c->get_code()] = (new DateTimeImmutable($day, new DateTimeZone('Europe/Brussels')))->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d\TH:i:s\Z');
}
// Saved empty amount is unknown, unlike native minimum/maximum defaults.
update_post_meta($coupons['winter']->get_id(), 'coupon_amount', '');
$utc = static function (?WC_DateTime $date): ?string {
    if ($date === null) {
        return null;
    }
    $copy = clone $date;
    $copy->setTimezone(new DateTimeZone('UTC'));
    return $copy->date('Y-m-d\TH:i:s\Z');
};
foreach ($coupons as $c) {
    $c = new WC_Coupon($c->get_id());
    $expected[$c->get_code()] = [
        'type' => $c->get_discount_type(), 'amount' => $c->get_code() === 'a10-season-winter' ? null : $c->get_amount(),
        'usage_count' => $c->get_usage_count(), 'usage_limit' => $c->get_usage_limit(),
        'usage_limit_per_user' => $c->get_usage_limit_per_user(), 'item_limit' => $c->get_limit_usage_to_x_items(),
        'allowed_email_count' => count($c->get_email_restrictions()),
        'product_ids' => $c->get_product_ids(), 'excluded_product_ids' => $c->get_excluded_product_ids(),
        'product_categories' => $c->get_product_categories(),
        'date_expires_utc' => $utc($c->get_date_expires()),
        'date_created_utc' => $utc($c->get_date_created()),
        'date_modified_utc' => $utc($c->get_date_modified()),
        'payment_limit_including_initial' => (int) $c->get_meta('_wcs_number_payments'),
        'individual_use' => $c->get_individual_use(), 'free_shipping' => $c->get_free_shipping(),
        'exclude_sale_items' => $c->get_exclude_sale_items(),
        'minimum_amount' => $c->get_minimum_amount() === '' ? null : $c->get_minimum_amount(),
        'maximum_amount' => $c->get_maximum_amount() === '' ? null : $c->get_maximum_amount(),
    ];
}
$schemaSources = [];
foreach ([WC_ABSPATH . 'includes/data-stores/class-wc-coupon-data-store-cpt.php',
    WC_ABSPATH . 'includes/data-stores/class-wc-order-item-data-store.php',
    WP_PLUGIN_DIR . '/woocommerce-subscriptions/includes/core/class-wc-subscriptions-coupon.php',
    WP_PLUGIN_DIR . '/woocommerce-subscriptions/includes/class-wcs-limited-recurring-coupon-manager.php'] as $source) {
    $schemaSources[str_replace(WP_PLUGIN_DIR . '/', '', $source)] = hash_file('sha256', $source);
}
echo 'A10_JSON=' . json_encode(['expected' => $expected, 'boundary_orders' => $boundaryOrders,
    'boundary_expiry' => $boundaryExpiry, 'legacy_expiry' => $legacyExpiry,
    'native_source_sha256' => $schemaSources, 'renewal_carries_coupon' => $renewalCarries,
    'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC()->version, 'subscriptions' => WC_Subscriptions::$version]]) . "\n";
