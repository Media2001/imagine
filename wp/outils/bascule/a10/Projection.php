<?php

declare(strict_types=1);

namespace Imagine\CouponInventory;

final class Projection
{
    public static function recurring(string $type): ?bool
    {
        if (in_array($type, ['recurring_fee', 'recurring_percent'], true)) {
            return true;
        }
        return in_array($type, ['percent', 'fixed_cart', 'fixed_product', 'sign_up_fee', 'sign_up_fee_percent'], true)
            ? false : null;
    }

    public static function number(string $value): ?int
    {
        return preg_match('/\A[0-9]{1,12}\z/D', $value) ? (int) $value : null;
    }

    public static function decimal(string $value): ?string
    {
        return preg_match('/\A[0-9]{1,12}(?:\.[0-9]{1,8})?\z/D', $value) ? $value : null;
    }

    private static function values(string $value): array
    {
        if ($value === '') {
            return [];
        }
        if (str_starts_with($value, 'a:')) {
            if (strlen($value) > 16777216) {
                throw new \RuntimeException('A10_META_INVALID');
            }
            $items = @unserialize($value, ['allowed_classes' => false, 'max_depth' => 4]);
            if (!is_array($items)) {
                throw new \RuntimeException('A10_META_INVALID');
            }
            foreach ($items as $item) {
                if (!is_string($item) && !is_int($item)) {
                    throw new \RuntimeException('A10_META_INVALID');
                }
            }
            return array_values(array_filter($items, static fn($v): bool => (string) $v !== ''));
        }
        return [$value];
    }

    public static function ids(string $value): array
    {
        $items = str_starts_with($value, 'a:') ? self::values($value) : explode(',', $value);
        $ids = [];
        foreach ($items as $item) {
            if (trim((string) $item) === '') {
                continue;
            }
            $id = self::number(trim((string) $item));
            if ($id === null) {
                throw new \RuntimeException('A10_META_INVALID');
            }
            if ($id > 0) {
                $ids[] = $id;
            }
        }
        return array_values(array_unique($ids));
    }

    public static function emailCount(string $value): int
    {
        return count(self::values($value));
    }

    public static function expiry(string $value, \DateTimeZone $zone): ?string
    {
        if ($value === '' || $value === '0') {
            return null;
        }
        if (self::number($value) !== null) {
            return gmdate('Y-m-d\TH:i:s\Z', (int) $value);
        }
        if (preg_match('/\A[0-9]{4}-[0-9]{2}-[0-9]{2}\z/D', $value)) {
            $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $value, $zone);
            if ($date && $date->format('Y-m-d') === $value) {
                return $date->setTimezone(new \DateTimeZone('UTC'))->format('Y-m-d\TH:i:s\Z');
            }
        }
        throw new \RuntimeException('A10_EXPIRY_INVALID');
    }

    public static function cutoff(\DateTimeImmutable $now): string
    {
        $year = (int) $now->format('Y') - 1;
        $day = min((int) $now->format('d'), (int) $now->setDate($year, (int) $now->format('m'), 1)->format('t'));
        return $now->setDate($year, (int) $now->format('m'), $day)->format('Y-m-d H:i:s');
    }
}
