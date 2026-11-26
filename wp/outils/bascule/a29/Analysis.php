<?php

declare(strict_types=1);

namespace Imagine\ScheduledTasks;

final class Analysis
{
    public const UNKNOWN = 'inconnu après neutralisation';
    public const FAMILIES = ['renouvellement', 'nouvelle_tentative', 'fin_abonnement', 'email',
        'entretien_woocommerce', 'entretien_wordpress', 'autre'];
    public const COUNTS = ['pending', 'overdue', 'failed', 'renewal_weeks', 'other_tasks', 'other_active_extensions'];
    public const HOOKS = [
        'woocommerce_scheduled_subscription_payment' => 'renouvellement',
        'woocommerce_scheduled_subscription_payment_retry' => 'nouvelle_tentative',
        'woocommerce_scheduled_subscription_end_of_prepaid_term' => 'fin_abonnement',
        'woocommerce_scheduled_subscription_expiration' => 'fin_abonnement',
        'wp_1_wc_emailer_cron' => 'email',
        'woocommerce_cancel_unpaid_orders' => 'entretien_woocommerce',
        'woocommerce_cleanup_sessions' => 'entretien_woocommerce',
        'woocommerce_scheduled_sales' => 'entretien_woocommerce',
        'woocommerce_cleanup_personal_data' => 'entretien_woocommerce',
        'woocommerce_cleanup_logs' => 'entretien_woocommerce',
        'wp_version_check' => 'entretien_wordpress',
        'wp_update_plugins' => 'entretien_wordpress',
        'wp_update_themes' => 'entretien_wordpress',
        'wp_scheduled_delete' => 'entretien_wordpress',
        'delete_expired_transients' => 'entretien_wordpress',
        'wp_privacy_delete_old_export_files' => 'entretien_wordpress',
        'recovery_mode_clean_expired_keys' => 'entretien_wordpress',
    ];

    public static function clock(string $date): \DateTimeImmutable
    {
        $clock = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:sP', $date, new \DateTimeZone('UTC'));
        if (!$clock || $clock->format('Y-m-d\TH:i:sP') !== $date || !str_ends_with($date, '+00:00')) {
            throw new \RuntimeException('A29_CLOCK_INVALID');
        }
        return $clock;
    }

    public static function family(string $hook): string
    {
        return self::HOOKS[$hook] ?? 'autre';
    }

    public static function pool(array $buckets, string $field): array
    {
        ksort($buckets, $field === 'week' ? SORT_NUMERIC : SORT_STRING);
        $result = ['groups' => [], 'autres' => 0];
        foreach ($buckets as $key => $count) {
            if ($count < 5) {
                $result['autres'] += $count;
            } else {
                $result['groups'][] = [$field => $key, 'count' => $count];
            }
        }
        return $result;
    }

    public static function rare(int $count): int|string
    {
        return $count > 0 && $count < 5 ? 'moins de cinq' : $count;
    }

    /** Only queue records, never callbacks or subscription identities. */
    public static function analyse(array $rows, string $audit, bool $neutralised): array
    {
        $now = self::clock($audit)->getTimestamp();
        if ($neutralised) {
            return array_fill_keys(self::COUNTS, self::UNKNOWN);
        }
        $buckets = ['pending' => [], 'overdue' => [], 'failed' => [], 'renewal_weeks' => []];
        $other = 0;
        foreach ($rows as $row) {
            if (
                !is_string($row['hook'] ?? null) || !is_int($row['timestamp'] ?? null)
                || $row['timestamp'] < 0 || !in_array(
                    $row['status'] ?? null,
                    ['pending', 'failed', 'complete', 'canceled', 'in-progress'],
                    true
                )
            ) {
                throw new \RuntimeException('A29_DATA_UNSUPPORTED');
            }
            $status = $row['status'];
            if (!in_array($status, ['pending', 'failed'], true)) {
                continue;
            }
            $family = self::family($row['hook']);
            $buckets[$status][$family] = ($buckets[$status][$family] ?? 0) + 1;
            $other += (int) ($family === 'autre');
            if ($status !== 'pending') {
                continue;
            }
            $time = $row['timestamp'];
            if ($time < $now) {
                $buckets['overdue'][$family] = ($buckets['overdue'][$family] ?? 0) + 1;
            }
            if ($family === 'renouvellement' && $time >= $now && $time < $now + 4838400) {
                $week = intdiv($time - $now, 604800) + 1;
                $buckets['renewal_weeks'][$week] = ($buckets['renewal_weeks'][$week] ?? 0) + 1;
            }
        }
        $result = [];
        foreach ($buckets as $key => $values) {
            $result[$key] = self::pool($values, $key === 'renewal_weeks' ? 'week' : 'family');
        }
        $result['other_tasks'] = self::rare($other);
        // Hook names, groups and callback files cannot prove who SCHEDULED a job.
        // An active plugin registry alone is not an attribution oracle.
        $result['other_active_extensions'] = $other ? 'attribution indéterminée' : 0;
        return $result;
    }
}
