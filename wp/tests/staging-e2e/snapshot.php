<?php

declare(strict_types=1);

namespace Imagine\E2E;

if (!defined('ABSPATH') || !class_exists('WooCommerce')) {
    throw new \RuntimeException('Real WordPress/Woo bootstrap required');
}
$orders = wc_get_orders(['limit' => -1, 'orderby' => 'ID', 'order' => 'ASC', 'type' => 'shop_order']);
$result = ['orders' => [], 'users' => []];
foreach ($orders as $order) {
    $items = [];
    foreach ($order->get_items() as $item) {
        $items[] = ['product' => $item->get_product_id(), 'quantity' => $item->get_quantity(),
            'total' => $item->get_total(), 'tax' => $item->get_total_tax()];
    }
    $result['orders'][] = ['id' => $order->get_id(), 'status' => $order->get_status(),
        'created' => $order->get_date_created()->getTimestamp(), 'total' => $order->get_total(),
        'currency' => $order->get_currency(), 'payment_method' => $order->get_payment_method(),
        'billing_country' => $order->get_billing_country(), 'shipping_country' => $order->get_shipping_country(),
        'items' => $items];
}
foreach (get_users(['orderby' => 'ID', 'order' => 'ASC']) as $user) {
    $result['users'][] = ['id' => (int) $user->ID, 'pass_hash' => $user->user_pass,
        'login' => $user->user_login, 'email' => $user->user_email, 'display_name' => $user->display_name,
        'first_name' => get_user_meta($user->ID, 'first_name', true),
        'last_name' => get_user_meta($user->ID, 'last_name', true),
        'billing_country' => get_user_meta($user->ID, 'billing_country', true),
        'shipping_country' => get_user_meta($user->ID, 'shipping_country', true)];
}
$result['versions'] = ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION,
    'hpos' => \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),
    'subscriptions_installed' => class_exists('WC_Subscriptions'),
    'memberships_installed' => function_exists('wc_memberships')];
echo "E2E_JSON=" . wp_json_encode($result) . "\n";
