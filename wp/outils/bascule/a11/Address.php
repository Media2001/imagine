<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

final class Address
{
    /** A09: origin-relative ASCII URI, canonical path, byte-preserved query. */
    public static function relative(string $url, string $home): string
    {
        $u = parse_url($url);
        $h = parse_url($home);
        $origin = static fn (array $v): array => [strtolower($v['scheme'] ?? ''), strtolower($v['host'] ?? ''), $v['port'] ?? (($v['scheme'] ?? '') === 'https' ? 443 : 80)];
        if (!$u || !$h || $origin($u) !== $origin($h) || !in_array($u['scheme'] ?? '', ['http', 'https'], true) || isset($u['user'], $u['pass']) || isset($u['user']) || isset($u['fragment'])) {
            throw new \RuntimeException('A11_URL_NOT_A09_COMPATIBLE');
        }
        $value = ($u['path'] ?? '/') . (array_key_exists('query', $u) ? '?' . $u['query'] : '');
        [$path, $query] = array_pad(explode('?', $value, 2), 2, null);
        if (strlen($value) > 2048 || preg_match('/[\x00-\x20\x7f-\xff\\\\#]/', $value) || !str_starts_with($value, '/') || str_starts_with($value, '//') || preg_match('/%(?![a-fA-F0-9]{2})/', $value) || $query === '' || preg_match('/%(?:0[0-9a-f]|1[0-9a-f]|20|2f|5c|7f)/i', $path) || ($query !== null && preg_match('/%(?:0[0-9a-f]|1[0-9a-f]|7f)/i', $query))) {
            throw new \RuntimeException('A11_URL_NOT_A09_COMPATIBLE');
        }
        $path = preg_replace_callback('/%([a-fA-F0-9]{2})/', static function (array $m): string {
            $char = chr(hexdec($m[1]));
            return preg_match('/[A-Za-z0-9_.~-]/', $char) ? $char : '%' . strtoupper($m[1]);
        }, $path);
        if (array_intersect(['.', '..'], explode('/', $path))) {
            throw new \RuntimeException('A11_URL_NOT_A09_COMPATIBLE');
        }
        return $path . ($query === null ? '' : '?' . $query);
    }
}
