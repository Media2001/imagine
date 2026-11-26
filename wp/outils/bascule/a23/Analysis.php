<?php

declare(strict_types=1);

namespace Imagine\ReaderAccounts;

final class Analysis
{
    public static function family(string $value): string
    {
        // Prefix recognition only. No validation, password trial or compatibility verdict.
        foreach ([
            '$wp$2y$' => 'wordpress_bcrypt', '$P$' => 'phpass', '$H$' => 'phpass_h',
            '$2a$' => 'bcrypt', '$2b$' => 'bcrypt', '$2y$' => 'bcrypt',
            '$argon2i$' => 'argon2i', '$argon2id$' => 'argon2id',
        ] as $prefix => $label) {
            if (str_starts_with($value, $prefix)) {
                return $label;
            }
        }
        return $value === '' ? 'vide' : 'autre';
    }

    public static function pool(array $counts): array
    {
        $result = ['groups' => [], 'autres' => 0];
        foreach ($counts as $label => $count) {
            if ($count >= 5) {
                $result['groups'][] = ['label' => $label, 'accounts' => $count];
            } else {
                $result['autres'] += $count;
            }
        }
        return $result;
    }
}
