<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

final class Report
{
    public static function compare(array $before, array $after): array
    {
        if (($before['schema'] ?? '') !== 'imagine-a03-v1' || ($after['schema'] ?? '') !== 'imagine-a03-v1') {
            throw new \RuntimeException('A03_REPORT_SCHEMA');
        }
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
