<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $s) {
    $s->delete(true);
}
update_option('woocommerce_currency', 'EUR');
$p = new WC_Product_Subscription();
$p->set_name('A20_PRODUCT_NAME_PRIVATE_CANARY');
$p->set_status('publish');
$p->set_regular_price('999');
$p->update_meta_data('_subscription_period', 'week');
$p->update_meta_data('_subscription_period_interval', '2');
$p->save();
$parent = new WC_Product_Variable_Subscription();
$parent->set_name('A20_SECOND_PRODUCT_PRIVATE_CANARY');
$parent->set_status('publish');
$parent->save();
$v = new WC_Product_Subscription_Variation();
$v->set_parent_id($parent->get_id());
$v->set_status('publish');
$v->set_regular_price('999');
$v->update_meta_data('_subscription_period', 'week');
$v->update_meta_data('_subscription_period_interval', '2');
$v->save();
$observed = [];
for ($i = 0; $i < 9; $i++) {
    $s = wcs_create_subscription(['status' => 'pending', 'billing_period' => $i === 5 ? 'month' : 'year',
        'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00']);
    if (is_wp_error($s)) {
        throw new RuntimeException('A20_FIXTURE_FAILED');
    }
    $s->set_requires_manual_renewal(true);
    $s->set_payment_method('');
    $s->set_billing_first_name('A20_PERSON_NAME_PRIVATE_CANARY');
    $s->set_billing_email('a20-fictif@example.org');
    $s->set_billing_country('US');
    $s->set_shipping_first_name('A20_DELIVERY_PRIVATE_CANARY');
    $s->set_shipping_country($i < 5 ? 'BE' : ($i === 5 ? 'FR' : ($i === 7 ? 'DE' : '')));
    $s->set_currency($i === 6 ? 'USD' : 'EUR');
    $s->add_product($i === 6 ? $v : $p, 1);
    if ($i === 7) {
        $s->add_product($p, 2);
        $s->add_product($v, 1);
    }
    if ($i === 5 || $i === 7) {
        $shipping = new WC_Order_Item_Shipping();
        $shipping->set_method_title('A20_SHIPPING_NAME_PRIVATE_CANARY');
        $shipping->set_method_id('a20_fixture');
        $shipping->set_total($i === 5 ? '2.00' : '0.00');
        $s->add_item($shipping);
    }
    if ($i === 5) {
        $fee = new WC_Order_Item_Fee();
        $fee->set_name('A20_FEE_NAME_PRIVATE_CANARY');
        $fee->set_total('0');
        $s->add_item($fee);
    }
    $s->set_total($i < 5 ? '100.00' : ($i === 5 ? '9.17' : ($i === 6 ? '0' : ($i === 7 ? '80.19' : '1234567.89'))));
    $s->save();
    $status = $i < 5 ? 'active' : ($i === 5 ? 'pending' : ($i === 6 ? 'on-hold' : ($i === 7 ? 'pending-cancel' : 'expired')));
    if ($i === 7) {
        $s->update_status('active');
        $s->update_dates(['next_payment' => '2027-01-01 00:00:00']);
    }
    if ($status !== 'pending') {
        $s->update_status($status);
    }
    $fresh = wcs_get_subscription($s->get_id());
    $observed[] = [$fresh->get_status('edit'), $fresh->get_billing_period('edit'),
        $fresh->get_billing_interval('edit'), (string) $fresh->get_total('edit'),
        $fresh->get_shipping_country('edit'), count($fresh->get_items('line_item'))];
}
echo 'A20_JSON=' . json_encode(['product' => $p->get_id(), 'parent' => $parent->get_id(),
    'variation' => $v->get_id(), 'observed' => $observed,
    'native_count' => count(wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']))]) . "\n";
