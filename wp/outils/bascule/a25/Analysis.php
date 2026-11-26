<?php

declare(strict_types=1);

namespace Imagine\VisitorRetention;

final class Analysis
{
    public const UNKNOWN = 'inconnu après neutralisation';
    public const STATES = ['0', '1', 'spam', 'trash', 'post-trashed', 'autre'];

    public static function pool(array $rows): array
    {
        $buckets = [];
        foreach ($rows as $row) {
            $year = (int) $row['year'];
            $year = $year >= 1000 && $year <= 9999 ? $year : 0;
            $state = (string) $row['state'];
            if (!in_array($state, array_merge(self::STATES, ['Fluent Forms', 'guest']), true)) {
                $state = 'autre';
            }
            $key = $year . ':' . $state;
            if (!isset($buckets[$key])) {
                $buckets[$key] = ['year' => $year, 'state' => $state, 'count' => 0];
            }
            $buckets[$key]['count'] += (int) ($row['count'] ?? 1);
        }
        ksort($buckets, SORT_STRING);
        $result = ['groups' => [], 'autres' => 0];
        foreach ($buckets as $bucket) {
            if ($bucket['count'] < 5) {
                $result['autres'] += $bucket['count'];
            } else {
                $result['groups'][] = $bucket;
            }
        }
        return $result;
    }

    public static function analyse(array $comments, array $forms, array $guests, bool $neutralised): array
    {
        $counts = ['all' => self::pool($comments)];
        foreach (['email', 'ip', 'account'] as $field) {
            $counts[$field] = $neutralised && $field !== 'account' ? self::UNKNOWN
                : self::pool(array_values(array_filter($comments, static fn(array $row): bool => $row[$field])));
        }
        return ['comments' => $counts, 'forms' => $neutralised ? self::UNKNOWN : self::pool($forms),
            'guests' => self::pool(array_map(
                static fn(int $year): array => ['year' => $year, 'state' => 'guest'],
                $guests
            ))];
    }
}
