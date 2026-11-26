<?php

declare(strict_types=1);

namespace Imagine\ReaderAccounts;

final class Inventory
{
    private static function select(string $sql): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A23_QUERY_FAILED');
        }
        return $rows;
    }

    public static function collect(string $site): array
    {
        // Native pre-initialised hooks: plugin.php converts these to WP_Hook.
        // Avoid attempts to recreate erased Action Scheduler work on a neutralised copy.
        // SQL READ ONLY remains the non-bypassable backstop, including direct APIs.
        foreach (['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $p = $wpdb->prefix;
        $storageRows = self::select("SELECT option_value FROM `{$p}options`"
            . " WHERE option_name='woocommerce_custom_orders_table_enabled'");
        $storage = ($storageRows[0]['option_value'] ?? '') === 'yes' ? 'hpos' : 'classic';
        $neutralised = count(self::select("SELECT option_id FROM `{$p}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'")) > 0;
        // Native authoritative store, including all statuses. No email-based customer linking.
        $commerce = $storage === 'hpos'
            ? self::select("SELECT id,type,status,customer_id AS customer FROM `{$p}wc_orders`"
                . " WHERE type IN ('shop_order','shop_order_refund','shop_subscription') ORDER BY id")
            : self::select("SELECT p.ID AS id,p.post_type AS type,p.post_status AS status,m.meta_value AS customer"
                . " FROM `{$p}posts` p LEFT JOIN `{$p}postmeta` m ON m.post_id=p.ID AND m.meta_key='_customer_user'"
                . " WHERE p.post_type IN ('shop_order','shop_order_refund','shop_subscription') ORDER BY p.ID");
        $links = [];
        $seen = [];
        foreach ($commerce as $record) {
            $customer = $record['customer'] ?? '0';
            if (!is_string($customer) || !ctype_digit($customer)) {
                throw new \RuntimeException('A23_CUSTOMER_LINK_UNSUPPORTED');
            }
            $id = (int) $customer;
            if (isset($seen[$record['id']]) && $seen[$record['id']] !== $id) {
                throw new \RuntimeException('A23_CUSTOMER_LINK_UNSUPPORTED');
            }
            $seen[$record['id']] = $id;
            if ($id === 0) {
                continue;
            }
            $live = $record['type'] === 'shop_subscription'
                && in_array($record['status'], ['wc-active', 'wc-pending', 'wc-on-hold', 'wc-pending-cancel'], true);
            $links[$id] = ($links[$id] ?? false) || $live;
        }
        $rows = [];
        foreach (self::select("SELECT ID,user_login,user_email,user_pass FROM `{$p}users` ORDER BY ID") as $record) {
            $id = (int) $record['ID'];
            $user = new \WP_User($id);
            $admin = count(array_intersect($user->roles, ['administrator', 'editor', 'shop_manager'])) > 0
                || \Imagine\AccountSecurity\Inventory::management($user->allcaps);
            $rows[] = ['id' => $id, 'hash' => $record['user_pass'], 'email' => $record['user_email'],
                'email_valid' => is_email($record['user_email']) !== false, 'login' => $record['user_login'],
                'admin' => $admin, 'live' => $links[$id] ?? false, 'commerce' => array_key_exists($id, $links)];
        }
        return ['schema' => 'imagine-a23-reader-accounts-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? 'inconnu après neutralisation' : 'observe',
            'counts' => Analysis::analyse($rows, $neutralised)];
    }
}
