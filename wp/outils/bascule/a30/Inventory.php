<?php

declare(strict_types=1);

namespace Imagine\OfflineDryRun;

final class Inventory
{
    public static function collect(string $site, array $rows): array
    {
        foreach (
            ['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook
        ) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        if (!class_exists(\WC_Subscriptions_Product::class)) {
            throw new \RuntimeException('A30_NATIVE_UNSUPPORTED');
        }
        $storage = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled()
            ? 'hpos' : 'classic';
        $marker = $wpdb->get_var($wpdb->prepare(
            "SELECT option_id FROM {$wpdb->options} WHERE option_name = %s LIMIT 1",
            'imagine_staging_disabled_plugins'
        ));
        if ($wpdb->last_error !== '') {
            throw new \RuntimeException('A30_QUERY_FAILED');
        }
        $neutralised = $marker !== null;
        $products = [];
        foreach ($rows as $row) {
            $id = $row['product'];
            if ($id !== null && !array_key_exists($id, $products)) {
                $product = wc_get_product($id);
                $products[$id] = $product instanceof \WC_Product
                    && $product->is_type(['subscription', 'subscription_variation'])
                    && \WC_Subscriptions_Product::is_subscription($product);
            }
        }
        $matches = [];
        // Email travels only through stdin and memory. No names, addresses, mandates,
        // password, account identifiers or subscription contents are selected/exported.
        if (!$neutralised) {
            foreach ($rows as $row) {
                if ($row['rejected'] || $row['email'] === '' || !($products[$row['product']] ?? false)) {
                    continue;
                }
                $ids = $wpdb->get_col($wpdb->prepare(
                    "SELECT ID FROM {$wpdb->users} WHERE user_email = %s LIMIT 2",
                    $row['email']
                ));
                if ($wpdb->last_error !== '' || !is_array($ids)) {
                    throw new \RuntimeException('A30_QUERY_FAILED');
                }
                $matches[$row['line']] = count($ids);
            }
        }
        return Analysis::analyse($rows, $products, $matches, $neutralised, $storage);
    }
}
