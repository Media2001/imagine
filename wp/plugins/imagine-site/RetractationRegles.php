<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Délai configuré pour la démonstration ; aucune décision juridique. */
final class RetractationRegles
{
    public static function valide(mixed $config): bool
    {
        return is_array($config) && count($config) === 2
            && is_int($config['jours'] ?? null) && $config['jours'] >= 1 && $config['jours'] <= 365
            && in_array($config['origine'] ?? null, ['paiement', 'manuelle'], true);
    }

    public static function debut(array $config, ?int $paid, ?int $manual): ?int
    {
        if (!self::valide($config)) {
            return null;
        }
        $start = $config['origine'] === 'paiement' ? $paid : $manual;
        return $start !== null && $start > 0 ? $start : null;
    }

    public static function ouverte(array $config, ?int $paid, ?int $manual, int $now): bool
    {
        $start = self::debut($config, $paid, $manual);
        if ($start === null) {
            return false;
        }
        $end = $start + $config['jours'] * 86400;
        return $now >= $start && $now <= $end;
    }
}
