<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

final class Report
{
    private static function requireValid(bool $valid): void
    {
        if (!$valid) {
            throw new \RuntimeException('A03_REPORT_STRUCTURE');
        }
    }

    private static function shape(mixed $row, array $fields): void
    {
        self::requireValid(is_array($row));
        self::requireValid(count($row) === count($fields));
        foreach ($fields as $key => $type) {
            self::requireValid(array_key_exists($key, $row) && get_debug_type($row[$key]) === $type);
        }
    }

    private static function values(array $rows, string $type): void
    {
        foreach ($rows as $value) {
            self::requireValid(get_debug_type($value) === $type);
        }
    }

    private static function validatePhoto(array $report): void
    {
        self::shape($report, [
            'schema' => 'string', 'generated_at_utc' => 'string', 'versions' => 'array',
            'storage' => 'string', 'sample_states' => 'array', 'samples' => 'array',
            'memberships' => 'array', 'access' => 'array', 'subscriptions' => 'array',
            'subscription_counts' => 'array', 'actions' => 'array', 'action_days' => 'array',
            'order_months' => 'array', 'orders' => 'array', 'pages' => 'array', 'renewal' => 'array',
        ]);
        self::requireValid(in_array($report['storage'], ['classic', 'hpos'], true));
        self::shape($report['versions'], array_fill_keys(
            ['wordpress', 'php', 'woocommerce', 'memberships', 'subscriptions'],
            'string'
        ));
        self::shape($report['sample_states'], ['membership' => 'array', 'subscription' => 'array']);
        foreach ($report['sample_states'] as $states) {
            foreach ($states as $present) {
                self::requireValid($present === true);
            }
        }
        self::values($report['samples'], 'int');
        self::values($report['access'], 'bool');
        foreach ($report['memberships'] as $row) {
            self::shape($row, ['user_id' => 'int', 'plan_id' => 'int', 'status' => 'string']);
        }
        foreach ($report['subscriptions'] as $row) {
            self::shape($row, ['status' => 'string', 'gateway' => 'string', 'period' => 'string',
                'interval' => 'int', 'next_payment_utc' => 'string']);
        }
        self::shape($report['subscription_counts'], ['status' => 'array', 'gateway' => 'array', 'period' => 'array']);
        foreach ($report['subscription_counts'] as $counts) {
            self::values($counts, 'int');
        }
        foreach ($report['actions'] as $row) {
            self::shape($row, ['hook' => 'string', 'date' => 'string']);
        }
        self::values($report['action_days'], 'int');
        self::requireValid(array_is_list($report['order_months']) && count($report['order_months']) === 12);
        self::values($report['order_months'], 'string');
        foreach ($report['orders'] as $row) {
            self::shape($row, ['count' => 'int', 'amount_minor' => 'int', 'decimals' => 'int']);
        }
        foreach ($report['pages'] as $row) {
            self::shape($row, ['status' => 'int', 'final_status' => 'int', 'marker' => 'bool', 'php_error' => 'bool']);
        }
        self::shape($report['renewal'], ['enabled' => 'bool']);
        self::requireValid($report['renewal']['enabled'] === false);
    }

    public static function compare(array $before, array $after): array
    {
        if (($before['schema'] ?? '') !== 'imagine-a03-v1' || ($after['schema'] ?? '') !== 'imagine-a03-v1') {
            throw new \RuntimeException('A03_REPORT_SCHEMA');
        }
        self::validatePhoto($before);
        self::validatePhoto($after);
        $changes = [];
        $walk = static function (mixed $a, mixed $b, string $path) use (&$walk, &$changes): void {
            if ($a === $b) {
                return;
            }
            if (is_array($a) && is_array($b)) {
                foreach (array_unique(array_merge(array_keys($a), array_keys($b))) as $key) {
                    $walk($a[$key] ?? null, $b[$key] ?? null, $path === '' ? (string) $key : $path . '.' . $key);
                }
                return;
            }
            $root = explode('.', $path)[0];
            if (in_array($root, ['generated_at_utc'], true)) {
                return;
            }
            $class = $root === 'versions' ? 'attendu' : (in_array(
                $root,
                ['pages', 'renewal'],
                true
            ) ? 'a regarder' : 'anormal');
            if (
                $root === 'pages' && ((str_ends_with($path, '.marker') && $b !== true)
                || (str_ends_with($path, '.php_error') && $b !== false)
                || (str_ends_with($path, 'status') && (!is_int($b) || $b < 200 || $b >= 400)))
            ) {
                $class = 'anormal';
            }
            // Values deliberately excluded: even malformed inputs never echo PII.
            $changes[] = ['path' => preg_match('/\A[A-Za-z0-9_.:-]{1,240}\z/D', $path) ? $path : '[masque]',
                'class' => $class];
        };
        $walk($before, $after, '');
        return ['schema' => 'imagine-a03-comparison-v1', 'changes' => $changes,
            'anormal' => count(array_filter($changes, static fn(array $c): bool => $c['class'] === 'anormal'))];
    }
}
