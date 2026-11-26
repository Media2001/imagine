<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Validation pure ; aucune recherche de compte. */
final class SujetRegles
{
    public static function email(string $email): string
    {
        return strtolower(trim($email));
    }

    public static function valide(string $nom, string $email, string $sujet): bool
    {
        return $nom !== '' && mb_strlen($nom) <= 200 && strlen($email) <= 254
            && filter_var($email, FILTER_VALIDATE_EMAIL) !== false && $sujet !== '' && mb_strlen($sujet) <= 10000;
    }
}
