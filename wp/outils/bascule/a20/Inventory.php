<?php

declare(strict_types=1);

namespace Imagine\SubscriptionPrices;

final class Inventory
{
    public static function collect(string $site): array
    {
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('wcs_get_subscriptions')) {
            throw new \RuntimeException('A20_NATIVE_API_UNAVAILABLE');
        }
        $rows = [];
        foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1,
            'subscription_status' => ['active', 'pending', 'on-hold', 'pending-cancel']]) as $subscription) {
            $items = $subscription->get_items('line_item');
            $products = [];
            foreach ($items as $item) {
                $products[] = ['product' => (int) $item->get_product_id('edit'),
                    'variation' => (int) $item->get_variation_id('edit')];
            }
            $rows[] = ['status' => $subscription->get_status('edit'),
                'period' => $subscription->get_billing_period('edit'),
                'interval' => (int) $subscription->get_billing_interval('edit'),
                'total' => (string) $subscription->get_total('edit'),
                'currency' => $subscription->get_currency('edit'),
                'country' => $subscription->get_shipping_country('edit'),
                'products' => $products, 'line_count' => count($items),
                'fees' => count($subscription->get_items('fee')) > 0,
                'shipping' => count($subscription->get_items('shipping')) > 0];
        }
        $currency = (string) get_option('woocommerce_currency');
        return ['schema' => 'imagine-a20-recurring-prices-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'counts' => Analysis::analyse($rows, $currency),
            'scope' => 'Magasin natif faisant autorite ; totaux recurrents enregistres, pas prelevements garantis ; aucune correspondance de tarif.'];
    }
}
