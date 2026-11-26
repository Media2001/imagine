<?php

declare(strict_types=1);

namespace Imagine\ExternalDoors;

final class Analysis
{
    public static function report(
        array $keys,
        array $hooks,
        array $helper,
        bool $neutralised,
        \DateTimeImmutable $clock,
        \DateTimeZone $zone,
        string $home
    ): array {
        if ($neutralised) {
            return [
                'api_keys' => ['status' => 'inconnu après neutralisation', 'counts' => null],
                'webhooks' => ['status' => 'inconnu après neutralisation', 'counts' => null],
                'extension_store' => ['status' => 'inconnu après neutralisation', 'connected' => null],
            ];
        }
        return [
            'api_keys' => ['status' => 'connu', 'counts' => self::keys($keys, $clock, $zone)],
            'webhooks' => ['status' => 'connu', 'counts' => self::webhooks($hooks, $home)],
            'extension_store' => ['status' => 'connu', 'connected' => !empty($helper['auth']['access_token'])],
        ];
    }

    private const TOPICS = [
        'coupon.created', 'coupon.updated', 'coupon.deleted', 'coupon.restored',
        'customer.created', 'customer.updated', 'customer.deleted',
        'order.created', 'order.updated', 'order.deleted', 'order.restored',
        'product.created', 'product.updated', 'product.deleted', 'product.restored', 'product.published',
    ];

    private static function host(string $url): ?string
    {
        $parts = parse_url($url);
        if (
            !$parts || !in_array(strtolower($parts['scheme'] ?? ''), ['http', 'https'], true)
            || empty($parts['host']) || isset($parts['user']) || isset($parts['pass'])
            || preg_match('/[\x00-\x20\x7f]/', $url)
        ) {
            return null;
        }
        return strtolower(rtrim($parts['host'], '.'));
    }

    public static function webhooks(array $rows, string $home): array
    {
        $site = self::host($home);
        $counts = ['total' => count($rows),
            'by_status' => ['active' => 0, 'paused' => 0, 'disabled' => 0, 'unknown' => 0],
            'by_topic' => [], 'active_destination' => ['same_domain' => 0, 'external_domain' => 0, 'unknown' => 0]];
        foreach ($rows as $row) {
            $status = in_array($row['status'] ?? '', ['active', 'paused', 'disabled'], true)
                ? $row['status'] : 'unknown';
            $topic = in_array($row['topic'] ?? '', self::TOPICS, true) ? $row['topic'] : 'unknown';
            $counts['by_status'][$status]++;
            $counts['by_topic'][$topic] = ($counts['by_topic'][$topic] ?? 0) + 1;
            if ($status === 'active') {
                $host = self::host((string) ($row['delivery_url'] ?? ''));
                $counts['active_destination'][$host === null || $site === null ? 'unknown'
                    : ($host === $site ? 'same_domain' : 'external_domain')]++;
            }
        }
        ksort($counts['by_topic']);
        return $counts;
    }

    public static function keys(array $rows, \DateTimeImmutable $clock, \DateTimeZone $zone): array
    {
        $local = $clock->setTimezone($zone);
        $year = (int) $local->format('Y') - 1;
        $month = (int) $local->format('m');
        $days = (int) $local->setDate($year, $month, 1)->format('t');
        $cutoff = $local->setDate($year, $month, min((int) $local->format('d'), $days));
        $counts = ['total' => count($rows),
            'by_permission' => ['read' => 0, 'write' => 0, 'read_write' => 0, 'unknown' => 0],
            'never_used' => 0, 'unused_twelve_months' => 0, 'last_access_unknown' => 0];
        foreach ($rows as $row) {
            $permission = in_array($row['permissions'] ?? '', ['read', 'write', 'read_write'], true)
                ? $row['permissions'] : 'unknown';
            $counts['by_permission'][$permission]++;
            $value = $row['last_access'] ?? null;
            if ($value === null || $value === '' || $value === '0000-00-00 00:00:00') {
                $counts['never_used']++;
                continue;
            }
            $date = is_string($value) ? \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, $zone) : false;
            if (!$date || $date->format('Y-m-d H:i:s') !== $value || $date > $local) {
                $counts['last_access_unknown']++;
            } elseif ($date < $cutoff) {
                $counts['unused_twelve_months']++;
            }
        }
        return $counts;
    }
}
