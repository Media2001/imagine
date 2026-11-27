<?php

declare(strict_types=1);

namespace Imagine\Site;

final class CodesSuivisRegles
{
    public static function liste(mixed $value): ?array
    {
        if (!is_array($value) || count($value) > 50) {
            return null;
        }
        foreach ($value as $code => $label) {
            if (
                !is_string($code) || !preg_match('/^[a-z][a-z0-9-]{0,39}$/D', $code)
                || !is_string($label) || trim($label) !== $label || $label === ''
                || mb_strlen($label) > 80 || preg_match('/[<>\x00-\x1f]/', $label)
            ) {
                return null;
            }
        }
        return $value;
    }

    public static function retenir(mixed $code, array $liste): ?array
    {
        return is_string($code) && isset($liste[$code])
            ? ['code' => $code, 'libelle' => $liste[$code]] : null;
    }

    public static function instantane(mixed $value): bool
    {
        return is_array($value) && isset($value['code'], $value['libelle'])
            && self::liste([$value['code'] => $value['libelle']]) !== null;
    }
}
