<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Validation pure ; aucun calcul de droit propre aux packs. */
final class PacksRegles
{
    public static function numeros(mixed $value): ?array
    {
        if (!is_array($value) || !array_is_list($value)) {
            return null;
        }
        $ids = [];
        foreach ($value as $id) {
            if ((!is_int($id) && !is_string($id))
                || !preg_match('/\A[1-9][0-9]*\z/D', (string) $id)
                || (string) (int) $id !== (string) $id) {
                return null;
            }
            $ids[(int) $id] = (int) $id;
        }
        return array_values($ids);
    }

    public static function instantane(mixed $value): array
    {
        if (!is_array($value) || !is_int($value['paye_le'] ?? null) || $value['paye_le'] <= 0
            || !is_int($value['produit'] ?? null) || $value['produit'] <= 0) {
            return [];
        }
        return self::numeros($value['numeros'] ?? null) ?? [];
    }
}
