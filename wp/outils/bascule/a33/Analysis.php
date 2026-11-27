<?php

declare(strict_types=1);

namespace Imagine\ArchiveWeight;

final class Analysis
{
    public const NON_EDITORIAL = ['attachment', 'revision', 'shop_order', 'shop_order_refund',
        'shop_order_placehold', 'shop_subscription', 'shop_coupon', 'wc_user_membership'];

    public static function editorial(array $mapping): void
    {
        $types = [$mapping['article_type']];
        if (($mapping['numero_source'] ?? 'post_type') === 'post_type') {
            $types[] = $mapping['numero_type'];
        }
        if (array_intersect($types, self::NON_EDITORIAL)) {
            throw new \RuntimeException('A33_NONEDITORIAL_MAPPING_UNSUPPORTED');
        }
    }

    public static function files(array $sizes, bool $imported): array
    {
        $present = count(array_filter($sizes, static fn ($size): bool => $size !== null));
        $missing = count($sizes) - $present;
        $bytes = array_sum($sizes);
        return ['count' => count($sizes), 'present' => $present, 'missing' => $missing,
            'known_bytes' => $bytes, 'total_bytes' => $missing
                ? ($imported ? 'inconnu après import' : 'inconnu fichiers absents') : $bytes];
    }

    public static function year(string $date): int|string
    {
        return preg_match('/\A[1-9][0-9]{3}-/D', $date) ? (int) substr($date, 0, 4) : 'inconnu';
    }

    public static function type(string $type, array $mapping): string
    {
        return match ($type) {
            $mapping['article_type'] => 'article',
            $mapping['numero_type'] => 'numero',
            'post', 'page', 'product', 'product_variation' => $type,
            default => 'autre',
        };
    }
}
