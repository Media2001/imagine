<?php

declare(strict_types=1);

namespace Imagine\Site;

final class ComptesPublicsRegles
{
    public static function utilisateurs(string $route): bool
    {
        return preg_match('~\A/wp/v2/users(?:/|\z)~i', $route) === 1;
    }

    public static function signature(mixed $signature, string $site): string
    {
        return is_string($signature) && trim($signature) !== '' ? trim($signature) : $site;
    }
}
