<?php

declare(strict_types=1);

namespace Imagine\CouponInventory;

final class Command
{
    private static function inside(string $path, string $root): bool
    {
        return $path === $root || str_starts_with($path . '/', $root . '/');
    }

    public static function main(array $args): int
    {
        $options = [];
        foreach (array_slice($args, 1) as $arg) {
            if (!preg_match('/\A--(wp-path|output|audit)=(.+)\z/D', $arg, $match) || isset($options[$match[1]])) {
                throw new \RuntimeException('A10_USAGE');
            }
            $options[$match[1]] = $match[2];
        }
        if (count($options) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A10_USAGE');
        }
        $site = realpath($options['wp-path']);
        $parent = realpath(dirname($options['output']));
        $base = basename($options['output']);
        $audit = realpath($options['audit']);
        if (!$site || !$parent || !is_dir($site) || !is_dir($parent) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)) {
            throw new \RuntimeException('A10_PATH_INVALID');
        }
        // Canonical checkout layout; standalone fixture/deployment also protects its source root.
        $repository = dirname(__DIR__, 4);
        if (!is_file($repository . '/wp/outils/bascule/audit')) {
            $repository = dirname(__DIR__);
        }
        if (self::inside($parent, $site) || self::inside($parent, $repository)) {
            throw new \RuntimeException('A10_OUTPUT_UNSAFE');
        }
        $output = $parent . '/' . $base;
        if (file_exists($output) || is_link($output)) {
            throw new \RuntimeException('A10_OUTPUT_EXISTS');
        }
        if (!$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216 || self::inside($audit, $site) || self::inside($audit, $repository) || dirname(dirname($audit)) !== $parent) {
            throw new \RuntimeException('A10_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])) {
            throw new \RuntimeException('A10_AUDIT_GUARD');
        }
        $report = (new Inventory($site))->collect();
        if ($photo['sections']['commerce']['order_storage'] !== $report['storage']) {
            throw new \RuntimeException('A10_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $markdown = "# Inventaire des codes — lecture seule\n\nNoms des codes autorises; aucun contact ni identifiant client. Aucun reclassement.\n\n```json\n" . json_encode($report, JSON_PRETTY_PRINT | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR) . "\n```\n";
        if (!mkdir($output, 0700)) {
            throw new \RuntimeException('A10_OUTPUT_CREATE');
        }
        foreach (['codes.json' => $json, 'codes.md' => $markdown] as $file => $content) {
            $handle = fopen($output . '/' . $file, 'xb');
            if ($handle === false) {
                throw new \RuntimeException('A10_OUTPUT_WRITE');
            }
            try {
                if (!chmod($output . '/' . $file, 0600) || fwrite($handle, $content) !== strlen($content)) {
                    throw new \RuntimeException('A10_OUTPUT_WRITE');
                }
            } finally {
                fclose($handle);
            }
        }
        fwrite(STDOUT, "A10_OK codes.json codes.md\n");
        return 0;
    }
}
