<?php

declare(strict_types=1);

namespace Imagine\ScheduledTasks;

final class Inventory
{
    private static function select(string $sql): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A29_QUERY_FAILED');
        }
        return $rows;
    }

    private static function cron(string $prefix): array
    {
        $values = self::select("SELECT option_value FROM `{$prefix}options` WHERE option_name='cron'");
        if (!$values) {
            return [];
        }
        $raw = $values[0]['option_value'];
        if (!is_string($raw) || strlen($raw) > 16777216) {
            throw new \RuntimeException('A29_DATA_UNSUPPORTED');
        }
        // No object constructors; arguments remain opaque and never leave this method.
        $cron = unserialize($raw, ['allowed_classes' => false]);
        if (!is_array($cron) || ($cron && ($cron['version'] ?? null) !== 2)) {
            throw new \RuntimeException('A29_DATA_UNSUPPORTED');
        }
        unset($cron['version']);
        $rows = [];
        foreach ($cron as $timestamp => $hooks) {
            if (!is_int($timestamp) || $timestamp < 0 || !is_array($hooks)) {
                throw new \RuntimeException('A29_DATA_UNSUPPORTED');
            }
            foreach ($hooks as $hook => $events) {
                if (!is_string($hook) || !is_array($events)) {
                    throw new \RuntimeException('A29_DATA_UNSUPPORTED');
                }
                foreach ($events as $event) {
                    if (!is_array($event) || !array_key_exists('schedule', $event)) {
                        throw new \RuntimeException('A29_DATA_UNSUPPORTED');
                    }
                    $rows[] = ['hook' => $hook, 'timestamp' => $timestamp, 'status' => 'pending'];
                }
            }
        }
        return $rows;
    }

    private static function timestamp(string $date): int
    {
        if ($date === '0000-00-00 00:00:00') {
            return 0; // Native AS NullSchedule / asynchronous immediate task.
        }
        $parsed = \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $date, new \DateTimeZone('UTC'));
        if (!$parsed || $parsed->format('Y-m-d H:i:s') !== $date || $parsed->getTimestamp() < 0) {
            throw new \RuntimeException('A29_DATA_UNSUPPORTED');
        }
        return $parsed->getTimestamp();
    }

    public static function collect(string $site, string $audit): array
    {
        Analysis::clock($audit);
        foreach (
            ['pre_as_enqueue_async_action', 'pre_as_schedule_single_action',
            'pre_as_schedule_recurring_action', 'pre_as_schedule_cron_action'] as $hook
        ) {
            $GLOBALS['wp_filter'][$hook][PHP_INT_MAX][] = ['function' => static fn(): int => 0, 'accepted_args' => 0];
        }
        \Imagine\PublicAddresses\Runtime::boot($site);
        if (
            !class_exists(\ActionScheduler::class)
            || !class_exists(\Automattic\WooCommerce\Utilities\OrderUtil::class)
        ) {
            throw new \RuntimeException('A29_NATIVE_API_UNAVAILABLE');
        }
        global $wpdb;
        $p = $wpdb->prefix;
        $storage = \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled()
            ? 'hpos' : 'classic';
        $neutralised = (bool) self::select("SELECT option_id FROM `{$p}options`"
            . " WHERE option_name='imagine_staging_disabled_plugins'");
        $rows = [];
        if (!$neutralised) {
            if (get_class(\ActionScheduler::store()) !== 'ActionScheduler_DBStore') {
                throw new \RuntimeException('A29_STORE_UNSUPPORTED');
            }
            $rows = self::cron($p);
            // No IDs, arguments, groups, claims or serialized schedules are queried.
            foreach (self::select("SELECT hook,status,scheduled_date_gmt FROM `{$p}actionscheduler_actions`") as $row) {
                $rows[] = ['hook' => $row['hook'], 'status' => $row['status'],
                    'timestamp' => self::timestamp($row['scheduled_date_gmt'])];
            }
        }
        return ['schema' => 'imagine-a29-scheduled-tasks-v1', 'read_only' => true, 'storage' => $storage,
            'neutralisation' => $neutralised ? Analysis::UNKNOWN : 'observe',
            'failed_scope' => 'action_scheduler_only', 'window' => 'eight_rolling_utc_weeks',
            'counts' => Analysis::analyse($rows, $audit, $neutralised), 'as_of_utc' => $audit];
    }
}
