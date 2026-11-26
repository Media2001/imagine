<?php

declare(strict_types=1);

namespace Imagine\RetentionInventory;

final class Forms
{
    public static function iban(string $value): bool
    {
        $value = strtoupper(preg_replace('/[\s\x{00a0}\x{202f}-]+/u', '', $value) ?? '');
        if (!preg_match('/\A[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}\z/D', $value)) {
            return false;
        }
        $formats = json_decode(file_get_contents(__DIR__ . '/iban-structures.json'), true, 8, JSON_THROW_ON_ERROR);
        $format = $formats[substr($value, 0, 2)] ?? '';
        $bban = preg_replace_callback('/([0-9]+)!([nac])/', static function (array $m): string {
            return ['n' => '[0-9]', 'a' => '[A-Z]', 'c' => '[A-Z0-9]'][$m[2]] . '{' . $m[1] . '}';
        }, $format);
        if (!$format || !preg_match('/\A' . $bban . '\z/D', substr($value, 4))) {
            return false;
        }
        $rotated = substr($value, 4) . substr($value, 0, 4);
        $remainder = 0;
        foreach (str_split($rotated) as $character) {
            foreach (str_split(ctype_alpha($character) ? (string) (ord($character) - 55) : $character) as $digit) {
                $remainder = ($remainder * 10 + (int) $digit) % 97;
            }
        }
        return $remainder === 1;
    }

    public static function card(string $value): bool
    {
        $digits = preg_replace('/[\s\x{00a0}\x{202f}-]+/u', '', $value) ?? '';
        if (!preg_match('/\A[0-9]{13,19}\z/D', $digits) || preg_match('/\A([0-9])\1+\z/D', $digits)) {
            return false;
        }
        $sum = 0;
        foreach (str_split(strrev($digits)) as $index => $digit) {
            $n = (int) $digit * ($index % 2 ? 2 : 1);
            $sum += $n > 9 ? $n - 9 : $n;
        }
        return $sum % 10 === 0;
    }

    public static function national(string $value): bool
    {
        $digits = preg_replace('/[ .-]+/', '', $value) ?? '';
        if (!preg_match('/\A[0-9]{11}\z/D', $digits)) {
            return false;
        }
        $base = substr($digits, 0, 9);
        $check = (int) substr($digits, 9);
        return $check === 97 - (int) $base % 97 || $check === 97 - (int) ('2' . $base) % 97;
    }

    public static function scan(string $value): array
    {
        $found = ['iban' => false, 'card' => false, 'national' => false];
        // Search textual/serialized bytes, never instantiate serialized objects.
        $value = str_replace(["\xc2\xa0", "\xe2\x80\xaf"], ' ', $value);
        $space = '[ \t-]?';
        $formats = json_decode(file_get_contents(__DIR__ . '/iban-structures.json'), true, 8, JSON_THROW_ON_ERROR);
        foreach ($formats as $country => $format) {
            preg_match_all('/([0-9]+)!/', $format, $parts);
            $size = array_sum(array_map('intval', $parts[1])) + 4;
            $pattern = '/(?<![A-Za-z0-9])' . $country . $space . '[0-9]' . $space . '[0-9](?:'
                . $space . '[A-Z0-9]){' . ($size - 4) . '}(?![A-Za-z0-9])/i';
            preg_match_all($pattern, $value, $matches);
            foreach ($matches[0] as $candidate) {
                $found['iban'] = $found['iban'] || self::iban($candidate);
            }
        }
        preg_match_all('/(?<![A-Za-z0-9])(?:[0-9][ .\t-]?){10,18}[0-9](?![A-Za-z0-9])/', $value, $matches);
        foreach ($matches[0] as $candidate) {
            $found['card'] = $found['card'] || self::card($candidate);
            $found['national'] = $found['national'] || self::national($candidate);
        }
        return $found;
    }
}
