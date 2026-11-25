<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

final class Report
{
    // A04 classic + HPOS observed only this deferred native Woo admin task.
    // No migration, renewal, maintenance or prefix-wide exception is justified.
    private const POST_UPDATE_HOOKS = ['woocommerce_run_on_woocommerce_admin_updated'];

    private static function expectedActionChange(array $before, array $after, string $path): bool
    {
        if ($before['versions']['woocommerce'] === $after['versions']['woocommerce']) {
            return false;
        }
        $parts = explode('.', $path, 3);
        if ($parts[0] === 'action_days') {
            $key = substr($path, strlen('action_days.'));
            return in_array(explode(':', $key, 2)[0], self::POST_UPDATE_HOOKS, true);
        }
        if ($parts[0] !== 'actions' || !isset($parts[1])) {
            return false;
        }
        foreach ([$before, $after] as $report) {
            $row = $report['actions'][$parts[1]] ?? null;
            if ($row !== null && !in_array($row['hook'], self::POST_UPDATE_HOOKS, true)) {
                return false;
            }
        }
        return true;
    }

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
            'order_months' => 'array', 'orders' => 'array', 'pages' => 'array', 'php_log' => 'array',
            'renewal' => 'array',
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
                'interval' => 'int',
                'next_payment_utc' => ($row['next_payment_utc'] ?? null) === 0 ? 'int' : 'string']);
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
        self::shape($report['php_log'], [
            'checked' => 'bool', 'from_utc' => 'string', 'until_utc' => 'string', 'errors' => 'int',
        ]);
        self::requireValid($report['php_log']['checked'] === true && $report['php_log']['errors'] >= 0);
        try {
            $from = PhpLog::timestamp($report['php_log']['from_utc']);
            $until = PhpLog::timestamp($report['php_log']['until_utc']);
        } catch (\RuntimeException) {
            self::requireValid(false);
        }
        self::requireValid($until >= $from && $until - $from <= 86400);
        self::shape($report['renewal'], ['enabled' => 'bool']);
        self::requireValid($report['renewal']['enabled'] === false);
        self::validateKeys($report);
    }

    private static function keys(array $map, string $pattern): void
    {
        foreach (array_keys($map) as $key) {
            self::requireValid(preg_match('~\A(?:' . $pattern . ')\z~D', (string) $key) === 1);
        }
    }

    private static function validateKeys(array $report): void
    {
        $id = '[1-9][0-9]*';
        $slug = '(?:[a-z][a-z0-9_-]{0,159}|\[masque\])';
        $month = '[0-9]{4}-(?:0[1-9]|1[0-2])';
        foreach (['memberships', 'subscriptions', 'actions'] as $section) {
            self::keys($report[$section], $id);
        }
        self::keys($report['access'], '(?:0|' . $id . '):' . $id);
        $states = $slug . '(?:\+' . $slug . ')*';
        self::keys($report['samples'], $states . ':' . $states);
        foreach ($report['sample_states'] as $group) {
            self::keys($group, $slug);
        }
        foreach ($report['subscription_counts'] as $kind => $group) {
            self::keys($group, $kind === 'period' ? '[1-9][0-9]*-' . $slug : $slug);
        }
        self::keys($report['pages'], 'home|open|restricted|shop|cart|checkout|account');
        self::keys($report['orders'], $month . ':' . $slug . ':[A-Z]{3}');
        foreach ($report['order_months'] as $value) {
            self::requireValid(preg_match('~\A' . $month . '\z~D', $value) === 1);
        }
        self::keys($report['action_days'], '(?:[A-Za-z0-9_./-]{1,160}|\[masque\]):' . $month . '-[0-9]{2}');
        foreach (array_keys($report['action_days']) as $key) {
            self::requireValid(!str_contains($key, '..') && !str_starts_with($key, '/'));
        }
    }

    private static function mode(array $report): string
    {
        if (!array_key_exists('mode', $report)) {
            return 'photo';
        }
        if ($report['mode'] !== 'renewal_probe') {
            throw new \RuntimeException('A03_REPORT_MODE');
        }
        return 'renewal_probe';
    }

    public static function compare(array $before, array $after): array
    {
        if (($before['schema'] ?? '') !== 'imagine-a03-v1' || ($after['schema'] ?? '') !== 'imagine-a03-v1') {
            throw new \RuntimeException('A03_REPORT_SCHEMA');
        }
        $beforeMode = self::mode($before);
        $afterMode = self::mode($after);
        if ($beforeMode !== $afterMode) {
            throw new \RuntimeException('A03_REPORT_MODE');
        }
        foreach ([$before, $after] as $report) {
            if ($beforeMode === 'renewal_probe') {
                self::shape($report, ['schema' => 'string', 'mode' => 'string', 'renewal' => 'array']);
                self::shape($report['renewal'], array_fill_keys(
                    ['enabled', 'manual_only', 'created', 'linked', 'pending', 'cleaned'],
                    'bool'
                ));
                self::requireValid($report['renewal']['enabled'] === true);
            } else {
                self::validatePhoto($report);
            }
        }
        if ($beforeMode === 'photo') {
            // The baseline must contain every page. A later loss is an anomaly, not a valid baseline.
            foreach (['home', 'open', 'restricted', 'shop', 'cart', 'checkout', 'account'] as $page) {
                self::requireValid(isset($before['pages'][$page]));
            }
        }
        $changes = [];
        $walk = static function (mixed $a, mixed $b, string $path) use (&$walk, &$changes, $before, $after): void {
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
            if (in_array($path, ['generated_at_utc', 'php_log.from_utc', 'php_log.until_utc'], true)) {
                return;
            }
            $class = $root === 'versions' ? 'attendu' : (in_array(
                $root,
                ['pages', 'renewal'],
                true
            ) ? 'a regarder' : 'anormal');
            if (
                $root === 'pages' && (($b === null)
                || (str_ends_with($path, '.marker') && $b !== true)
                || (str_ends_with($path, '.php_error') && $b !== false)
                || (str_ends_with($path, 'status') && (!is_int($b) || $b < 200 || $b >= 400)))
            ) {
                $class = 'anormal';
            }
            if (
                in_array($root, ['actions', 'action_days'], true)
                && self::expectedActionChange($before, $after, $path)
            ) {
                $class = 'attendu';
            }
            // No values are emitted. Free-form slug keys are never proof of anonymity.
            $safePath = in_array(
                $root,
                ['sample_states', 'samples', 'subscription_counts', 'action_days', 'orders'],
                true
            ) ? $root . '.[masque]' : $path;
            $changes[] = ['path' => $safePath, 'class' => $class];
        };
        $walk($before, $after, '');
        if (
            $beforeMode === 'photo' && $after['php_log']['errors'] > 0
            && $after['php_log']['errors'] === $before['php_log']['errors']
        ) {
            $changes[] = ['path' => 'php_log.errors', 'class' => 'anormal'];
        }
        return ['schema' => 'imagine-a03-comparison-v1', 'changes' => $changes,
            'anormal' => count(array_filter($changes, static fn(array $c): bool => $c['class'] === 'anormal'))];
    }
}
