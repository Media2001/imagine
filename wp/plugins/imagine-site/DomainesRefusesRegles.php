<?php

declare(strict_types=1);

namespace Imagine\Site;

final class DomainesRefusesRegles
{
    public static function liste(mixed $value): ?array
    {
        if (is_string($value)) { $value = preg_split('/\r\n|\n|\r/', $value); }
        if (!is_array($value) || count($value) > 500) { return null; }
        $out = [];
        foreach ($value as $domain) {
            if (!is_string($domain)) { return null; }
            $domain = strtolower(trim($domain));
            if ($domain === '') { continue; }
            if (strlen($domain) > 253 || !str_contains($domain, '.')) { return null; }
            foreach (explode('.', $domain) as $label) {
                if (!preg_match('/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/D', $label)) { return null; }
            }
            $out[$domain] = $domain;
        }
        return array_values($out);
    }

    public static function refuse(string $email, array $domains): bool
    {
        $pos = strrpos($email, '@');
        return $pos !== false && in_array(strtolower(substr($email, $pos + 1)), $domains, true);
    }
}
