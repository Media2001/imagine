<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

/** Protection CSV C-04 partagée, sans modification de la règle existante. */
final class CsvProtection
{
    public static function cellule(mixed $value): mixed
    {
        return is_string($value) && preg_match('/\\A[\\x00-\\x20]*[=+@-]/', $value) === 1
            ? "'" . $value : $value;
    }
}
