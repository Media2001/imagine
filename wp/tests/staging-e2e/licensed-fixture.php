<?php

declare(strict_types=1);

namespace Imagine\E2E;

if (!defined('ABSPATH') || wp_get_environment_type() !== 'staging'
    || !function_exists('wcs_create_subscription') || !class_exists('WC_Memberships')) {
    throw new \RuntimeException('Approved licensed plugins must actually be active');
}
add_filter('pre_wp_mail', '__return_true', PHP_INT_MAX); // Seed process only; never installed.
$fixture = get_option('imagine_e2e_fixture');
$ids = [];
foreach (array_slice($fixture['orders'], 0, 6) as $index => $orderId) {
    $order = wc_get_order($orderId);
    $subscription = wcs_create_subscription([
        'order_id' => $orderId, 'customer_id' => $order->get_customer_id(),
        'status' => ['active', 'on-hold', 'pending-cancel'][$index % 3],
        'billing_period' => 'month', 'billing_interval' => 1,
        'date_created' => '2026-10-01 12:00:00', 'start_date' => '2026-10-01 12:00:00',
    ]);
    if (is_wp_error($subscription)) {
        throw new \RuntimeException('SYNTHETIC_SUBSCRIPTION_CREATE_FAILED');
    }
    $subscription->add_product(wc_get_product($fixture['product']), ($index % 3) + 1);
    $subscription->set_address($order->get_address('billing'), 'billing');
    $subscription->set_address($order->get_address('shipping'), 'shipping');
    $subscription->set_payment_method($order->get_payment_method());
    $subscription->set_currency('EUR');
    $subscription->update_dates(['next_payment' => '2027-01-01 12:00:00', 'end' => '2027-12-31 12:00:00']);
    $subscription->calculate_totals();
    $subscription->save();
    $ids[] = $subscription->get_id();
}
update_option('imagine_e2e_subscriptions', $ids);
echo 'E2E_JSON=' . json_encode([
    'subscriptions_created' => count($ids), 'subscriptions_version' => WC_Subscriptions::$version,
    'memberships_active' => class_exists('WC_Memberships'),
    'staging_mode_observed' => \WCS_Staging::is_duplicate_site(),
    'no_license_activation' => true,
], JSON_THROW_ON_ERROR) . "\n";
