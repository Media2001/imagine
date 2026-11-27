<?php

declare(strict_types=1);

namespace Imagine\OrderHistory;

final class Inventory
{
    private static function select(string $sql): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A31_QUERY_FAILED');
        }
        return $rows;
    }

    private static function year(\WC_Abstract_Order $order): int|string
    {
        $date = $order->get_date_created('edit');
        return $date === null ? 'illisible' : (int) gmdate('Y', $date->getTimestamp());
    }

    public static function relations(\WC_Order $order, \WCS_Related_Order_Store $store, bool $parent): array
    {
        $types = $parent ? ['parent'] : [];
        $orphan = false;
        $opaque = false;
        foreach (['renewal', 'switch', 'resubscribe'] as $type) {
            $raw = [];
            foreach ($order->get_meta('_subscription_' . $type, false, 'edit') as $meta) {
                $value = $meta->get_data()['value'];
                if (
                    (!is_int($value) && !is_string($value))
                    || !preg_match('/\A[1-9][0-9]*\z/D', (string) $value)
                    || (string) (int) $value !== (string) $value
                ) {
                    $opaque = true;
                    continue;
                }
                $raw[] = (int) $value;
            }
            $native = $store->get_related_subscription_ids($order, $type);
            $expected = array_values(array_unique($raw));
            $actual = is_array($native) ? array_values(array_unique($native)) : [];
            sort($expected);
            sort($actual);
            if (!is_array($native) || $actual !== $expected) {
                $opaque = true;
            }
            if ($raw !== []) {
                $types[] = $type;
            }
            if ($type === 'renewal') {
                foreach ($raw as $id) {
                    if (!(wcs_get_subscription($id) instanceof \WC_Subscription)) {
                        $orphan = true;
                    }
                }
            }
        }
        // An extension may register a different relation; never turn it into a standalone order.
        foreach ($order->get_meta_data() as $meta) {
            $key = $meta->get_data()['key'];
            if (
                str_starts_with($key, '_subscription_')
                && !in_array($key, ['_subscription_renewal', '_subscription_switch', '_subscription_resubscribe'], true)
            ) {
                $opaque = true;
            }
        }
        return ['nature' => $opaque || count(array_unique($types)) > 1 ? 'illisible' : ($types[0] ?? 'none'),
            'orphan_renewal' => $orphan];
    }

    public static function collect(string $site): array
    {
        foreach (['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (!function_exists('wcs_get_subscription') || !class_exists(\WCS_Related_Order_Store_CPT::class)) {
            throw new \RuntimeException('A31_NATIVE_API_UNAVAILABLE');
        }
        global $wpdb;
        $prefix = $wpdb->prefix;
        $storage = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled()
            ? 'hpos' : 'classic';
        // Enumerate the authoritative store, including unregistered states; do NOT union backup rows.
        $rows = $storage === 'hpos'
            ? self::select("SELECT id AS object_id,type AS object_type FROM `{$prefix}wc_orders`"
                . " WHERE type IN ('shop_order','shop_order_refund','shop_subscription')"
                . " AND status <> 'trash' ORDER BY id")
            : self::select("SELECT ID AS object_id,post_type AS object_type FROM `{$prefix}posts`"
                . " WHERE post_type IN ('shop_order','shop_order_refund','shop_subscription')"
                . " AND post_status <> 'trash' ORDER BY ID");
        $neutralised = (bool) self::select("SELECT option_id FROM `{$prefix}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'");
        $objects = [];
        $subscriptions = [];
        $parents = [];
        foreach ($rows as $row) {
            $id = (int) $row['object_id'];
            $type = $row['object_type'];
            $object = $type === 'shop_subscription' ? wcs_get_subscription($id) : wc_get_order($id);
            if ($type === 'shop_subscription') {
                if (!$object instanceof \WC_Subscription) {
                    throw new \RuntimeException('A31_SUBSCRIPTION_UNREADABLE');
                }
                $parent = (int) $object->get_parent_id('edit');
                $parents[$parent] = true;
                $original = $parent > 0 ? wc_get_order($parent) : false;
                $subscriptions[] = ['status' => $object->get_status('edit'),
                    'parent_exists' => $original instanceof \WC_Order && $original->get_type() === 'shop_order'];
            } else {
                $objects[] = ['object' => $object, 'type' => $type, 'id' => $id];
            }
        }
        // Native uncached reader uses WC_Data in both stores; cached wrapper can persist relation caches.
        $nativeStore = \WCS_Related_Order_Store::instance();
        if (get_class($nativeStore) !== 'WCS_Related_Order_Store_Cached_CPT') {
            throw new \RuntimeException('A31_NATIVE_API_UNAVAILABLE');
        }
        $store = new \WCS_Related_Order_Store_CPT();
        $orders = [];
        $refunds = [];
        foreach ($objects as $entry) {
            $object = $entry['object'];
            if ($entry['type'] === 'shop_order_refund') {
                if (!$object instanceof \WC_Order_Refund) {
                    throw new \RuntimeException('A31_REFUND_UNREADABLE');
                }
                $refunds[] = ['year' => self::year($object)];
                continue;
            }
            if (!$object instanceof \WC_Order || $object instanceof \WC_Subscription) {
                $orders[] = ['year' => 'illisible', 'status' => 'autre', 'nature' => 'illisible',
                    'orphan_renewal' => false, 'account_missing' => false, 'link_unknown' => true];
                continue;
            }
            $user = (int) $object->get_customer_id('edit');
            $orders[] = ['year' => self::year($object), 'status' => $object->get_status('edit'),
                'account_missing' => $user > 0 && get_userdata($user) === false, 'link_unknown' => false]
                + self::relations($object, $store, isset($parents[$entry['id']]));
        }
        return ['schema' => 'imagine-a31-history-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe',
            'counts' => Analysis::analyse($orders, $subscriptions, $refunds, $neutralised)];
    }
}
