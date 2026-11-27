<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Validation locale seulement : aucune découverte ou normalisation distante. */
final class MediasRegles
{
    public static function lien(mixed $url): ?string
    {
        if (!is_string($url) || strlen($url) > 2000 || preg_match('/[\x00-\x20\x7f\\\\]/', $url)) {
            return null;
        }
        $parts = parse_url($url);
        if (!$parts || ($parts['scheme'] ?? '') !== 'https' || empty($parts['host'])
            || isset($parts['user']) || isset($parts['pass']) || isset($parts['port'])
            || !filter_var($url, FILTER_VALIDATE_URL)) {
            return null;
        }
        return $url;
    }

    public static function video(mixed $url, array $hosts): ?string
    {
        $valid = self::lien($url);
        return $valid !== null && in_array(strtolower((string) parse_url($valid, PHP_URL_HOST)), $hosts, true)
            ? $valid : null;
    }
}
