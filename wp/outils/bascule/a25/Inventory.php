<?php

declare(strict_types=1);

namespace Imagine\VisitorRetention;

final class Inventory
{
    // Closed, documented storage adapter; no submitted content is selected.
    private const FORMS = ['fluentform_submissions' => ['name' => 'Fluent Forms', 'date' => 'created_at']];

    private static function select(string $sql): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A25_QUERY_FAILED');
        }
        return $rows;
    }

    private static function year(string $date): int
    {
        return preg_match('/\A([1-9][0-9]{3})-[0-9]{2}-[0-9]{2}/D', $date, $m) ? (int) $m[1] : 0;
    }

    public static function collect(string $site): array
    {
        foreach (
            ['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook
        ) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $p = $wpdb->prefix;
        $hpos = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled();
        $storage = $hpos ? 'hpos' : 'classic';
        $neutralised = count(self::select("SELECT option_id FROM `{$p}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'")) > 0;
        $comments = [];
        // Enumerate all native comments, including custom types/states, but not Woo order notes.
        $commentIds = self::select("SELECT comment_ID FROM `{$p}comments`"
            . " WHERE comment_type <> 'order_note' ORDER BY comment_ID");
        foreach ($commentIds as $row) {
            $c = get_comment((int) $row['comment_ID']);
            if (!$c instanceof \WP_Comment) {
                throw new \RuntimeException('A25_NATIVE_OBJECT_UNSUPPORTED');
            }
            $comments[] = ['year' => self::year($c->comment_date_gmt), 'state' => $c->comment_approved,
                'email' => $c->comment_author_email !== '', 'ip' => $c->comment_author_IP !== '',
                'account' => (int) $c->user_id > 0];
        }
        // SQL enumerates IDs only, including trash/unregistered statuses. All semantics are native getters.
        $ids = $storage === 'hpos' ? self::select("SELECT id FROM `{$p}wc_orders` WHERE type='shop_order' ORDER BY id")
            : self::select("SELECT ID AS id FROM `{$p}posts` WHERE post_type='shop_order' ORDER BY ID");
        $guests = [];
        foreach ($ids as $row) {
            $order = wc_get_order((int) $row['id']);
            if (!$order instanceof \WC_Order || $order->get_type() !== 'shop_order') {
                throw new \RuntimeException('A25_NATIVE_OBJECT_UNSUPPORTED');
            }
            if ((int) $order->get_customer_id('edit') === 0) {
                $date = $order->get_date_created('edit');
                $guests[] = $date ? (int) gmdate('Y', $date->getTimestamp()) : 0;
            }
        }
        $forms = [];
        $listed = [];
        $other = 0;
        $tables = self::select("SELECT TABLE_NAME FROM information_schema.TABLES"
            . " WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME");
        foreach ($tables as $record) {
            $table = $record['TABLE_NAME'];
            if (!str_starts_with($table, $p) || !preg_match('/\A[A-Za-z0-9_]{1,64}\z/D', $table)) {
                continue;
            }
            $suffix = substr($table, strlen($p));
            $columns = array_column(self::select("SELECT COLUMN_NAME FROM information_schema.COLUMNS"
                . " WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='{$table}'"), 'COLUMN_NAME');
            $known = self::FORMS[$suffix] ?? null;
            // Unknown entry tables: structural evidence, not arbitrary names/values.
            // Avoid field-detail/meta child tables, which would count one message more than once.
            $candidate = in_array('form_id', $columns, true)
                && count(array_intersect(['response', 'message', 'submission', 'fields'], $columns)) > 0
                && !in_array('submission_id', $columns, true) && !in_array('meta_key', $columns, true);
            if (!$known && !$candidate) {
                continue;
            }
            $dates = array_values(array_intersect(['created_at', 'date_created', 'submitted_at'], $columns));
            $date = $known['date'] ?? ($dates[0] ?? null);
            if ($known && !in_array($date, $columns, true)) {
                throw new \RuntimeException('A25_NATIVE_OBJECT_UNSUPPORTED');
            }
            if ($known) {
                $listed[] = $known['name'];
            } else {
                $other++;
            }
            $expr = $date ? "COALESCE(YEAR(`{$date}`),0)" : '0';
            $buckets = self::select("SELECT {$expr} AS year,COUNT(*) AS count FROM `{$table}` GROUP BY 1");
            foreach ($buckets as $count) {
                $forms[] = ['year' => (int) $count['year'], 'state' => $known['name'] ?? 'autre',
                    'count' => (int) $count['count']];
            }
        }
        return ['schema' => 'imagine-a25-visitor-retention-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe',
            'counts' => Analysis::analyse($comments, $forms, $guests, $neutralised),
            'forms' => ['listed_extensions' => array_values(array_unique($listed)), 'other_tables' => $other,
                'clear_messages_after_import' => true]];
    }
}
