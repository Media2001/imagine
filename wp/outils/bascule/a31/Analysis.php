<?php

declare(strict_types=1);

namespace Imagine\OrderHistory;

final class Analysis
{
    public const UNKNOWN = 'inconnu après neutralisation';
    public const STATUSES = ['pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded',
        'failed', 'checkout-draft', 'autre'];
    public const NATURES = ['parent', 'renewal', 'switch', 'resubscribe', 'none', 'illisible'];

    private static function year(mixed $year): int|string
    {
        return is_int($year) && $year >= 1000 && $year <= 9999 ? $year : 'illisible';
    }

    private static function pool(array $rows): array
    {
        $groups = [];
        $other = 0;
        ksort($rows, SORT_STRING);
        foreach ($rows as $row) {
            if ($row['count'] < 5) {
                $other += $row['count'];
            } else {
                $groups[] = $row;
            }
        }
        return ['groups' => $groups, 'autres' => $other];
    }

    public static function analyse(array $orders, array $subscriptions, array $refunds, bool $neutralised = false): array
    {
        $buckets = array_fill_keys(['years', 'statuses', 'natures', 'orphan_renewals', 'structural_links', 'refunds'], []);
        $add = static function (string $kind, array $fields) use (&$buckets): void {
            $key = implode(':', array_map('strval', array_values($fields)));
            $buckets[$kind][$key] ??= $fields + ['count' => 0];
            $buckets[$kind][$key]['count']++;
        };
        $years = [];
        foreach ($orders as $row) {
            $year = self::year($row['year']);
            $years[$year] = ($years[$year] ?? 0) + 1;
            $add('years', ['year' => $year]);
            $status = in_array($row['status'], self::STATUSES, true) ? $row['status'] : 'autre';
            $add('statuses', ['year' => $year, 'status' => $status]);
            $nature = in_array($row['nature'], self::NATURES, true) ? $row['nature'] : 'illisible';
            $add('natures', ['nature' => $nature]);
            if ($row['orphan_renewal']) {
                $add('orphan_renewals', ['metric' => 'renewals_missing_subscription']);
            }
            if ($row['account_missing']) {
                $add('structural_links', ['metric' => 'orders_missing_account']);
            }
            if ($row['link_unknown']) {
                $add('structural_links', ['metric' => 'orders_link_unknown']);
            }
        }
        foreach ($subscriptions as $row) {
            // A-19 Analysis::analyse lines 63-65: its living/active cohort is exactly active.
            if ($row['status'] === 'active' && !$row['parent_exists']) {
                $add('structural_links', ['metric' => 'living_without_parent']);
            }
        }
        foreach ($refunds as $row) {
            $add('refunds', ['year' => self::year($row['year'])]);
        }
        $result = [];
        foreach ($buckets as $key => $rows) {
            $result[$key] = $neutralised && in_array($key, ['natures', 'orphan_renewals'], true)
                ? self::UNKNOWN : self::pool($rows);
        }
        $oldest = null;
        if (isset($years['illisible'])) {
            $oldest = 'illisible';
        } elseif ($years !== []) {
            $first = min(array_keys($years));
            $oldest = $years[$first] >= 5 ? $first : 'fusionne';
        }
        $result['oldest_year'] = $oldest;
        return $result;
    }
}
