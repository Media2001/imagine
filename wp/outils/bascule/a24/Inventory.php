<?php

declare(strict_types=1);

namespace Imagine\ShippingAddresses;

/** Thin native read adapter. No setters, saves, validation or address fallback. */
final class Inventory
{
    public static function collect(string $site): array
    {
        // Prevent erased Action Scheduler work being recreated at bootstrap.
        foreach (
            ['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook
        ) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('wcs_get_subscriptions') || !class_exists('WC_Customer') || !WC()->countries) {
            throw new \RuntimeException('A24_NATIVE_API_UNAVAILABLE');
        }
        $countries = array_keys(WC()->countries->get_countries());
        $closed = json_decode(file_get_contents(__DIR__ . '/country_codes.json'), true, 16, JSON_THROW_ON_ERROR);
        if (array_diff($countries, $closed) !== []) {
            throw new \RuntimeException('A24_NATIVE_COUNTRIES_UNSUPPORTED');
        }
        $rows = [];
        foreach (
            wcs_get_subscriptions(['subscriptions_per_page' => -1,
                'subscription_status' => ['active', 'pending', 'on-hold', 'pending-cancel']]) as $subscription
        ) {
            $shipping = [];
            $billing = [];
            foreach (Analysis::FIELDS as $field) {
                $getter = 'get_shipping_' . $field;
                $shipping[$field] = (string) $subscription->$getter('edit');
                $getter = 'get_billing_' . $field;
                $billing[$field] = (string) $subscription->$getter('edit');
            }
            $required = [];
            // Woo's own locale overlay, shop visibility options and native filters.
            // Missing country uses Woo's own base-country fallback, not ours.
            foreach (WC()->countries->get_address_fields($shipping['country'], 'shipping_') as $key => $definition) {
                if (!in_array($key, array_map(static fn(string $f): string => 'shipping_' . $f, Analysis::FIELDS), true)) {
                    throw new \RuntimeException('A24_NATIVE_FIELDS_UNSUPPORTED');
                }
                if (!empty($definition['required'])) {
                    $required[] = $key;
                }
            }
            $id = (int) $subscription->get_customer_id('edit');
            $customer = null;
            if ($id > 0 && get_userdata($id) !== false) {
                $native = new \WC_Customer($id);
                $customer = [];
                foreach (Analysis::FIELDS as $field) {
                    $getter = 'get_shipping_' . $field;
                    $customer[$field] = (string) $native->$getter('edit');
                }
            }
            $rows[] = ['shipping' => $shipping, 'billing' => $billing,
                'customer' => $customer, 'required' => $required];
        }
        global $wpdb;
        $marker = $wpdb->get_results("SELECT option_id FROM `{$wpdb->prefix}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'", ARRAY_A);
        if (!is_array($marker) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A24_QUERY_FAILED');
        }
        $neutralised = count($marker) > 0;
        return ['schema' => 'imagine-a24-shipping-addresses-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe',
            'counts' => Analysis::analyse($rows, $countries, $neutralised)];
    }
}
