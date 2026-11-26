<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Un attribut séparé des abonnements et des décisions d'accès aux articles. */
final class CooperateursRegles
{
    public static function administration(array $roles): bool
    {
        return in_array('administrator', $roles, true);
    }

    public static function lecture(mixed $state, array $roles, bool $connecte): bool
    {
        if (!$connecte) {
            return false;
        }
        return self::administration($roles) || (is_array($state)
            && ($state['cooperateur'] ?? null) === true
            && ($state['source'] ?? '') === 'administration'
            && is_string($state['date_utc'] ?? null)
            && preg_match('/\A\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\z/D', $state['date_utc']) === 1);
    }
}
