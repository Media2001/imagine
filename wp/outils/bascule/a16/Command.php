<?php

declare(strict_types=1);

namespace Imagine\IssueInventory;

final class Command
{
    public static function main(array $args): int
    {
        $o = [];
        foreach (array_slice($args, 1) as $arg) {
            if (!preg_match('/\A--(wp-path|output|audit|correspondance|limit)=(.+)\z/D', $arg, $m) || isset($o[$m[1]])) {
                throw new \RuntimeException('A16_USAGE');
            }
            $o[$m[1]] = $m[2];
        }
        if (!isset($o['wp-path'], $o['output'], $o['audit'], $o['correspondance']) || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A16_USAGE');
        }
        $site = realpath($o['wp-path']);
        $parent = realpath(dirname($o['output']));
        $base = basename($o['output']);
        $repository = dirname(__DIR__, 4);
        if (!is_file($repository . '/wp/outils/bascule/audit')) {
            $repository = dirname(__DIR__);
        }
        if (
            !$site || !$parent || !is_dir($site) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)
            || !\Imagine\ContentInventory\Command::disjointOutput($parent, $site, $repository)
        ) {
            throw new \RuntimeException('A16_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A16_OUTPUT_EXISTS');
        }
        $audit = realpath($o['audit']);
        if (
            !$audit || !is_file($audit) || is_link($o['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A16_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
        ) {
            throw new \RuntimeException('A16_AUDIT_GUARD');
        }
        if (getenv('A16_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A16_CONFINEMENT_REQUIRED');
        }
        $map = realpath($o['correspondance']);
        if (!$map || is_link($o['correspondance']) || !is_file($map) || filesize($map) > 65536) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        $mapping = Mapping::validate(json_decode(file_get_contents($map), true, 32, JSON_THROW_ON_ERROR));
        $limit = $o['limit'] ?? '10';
        if (!preg_match('/\A[1-9][0-9]{0,2}\z/D', $limit) || (int) $limit > 100) {
            throw new \RuntimeException('A16_LIMIT_INVALID');
        }
        $report = (new Inventory($site))->collect($mapping, (int) $limit);
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A16_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $report['mapping_sha256'] = hash_file('sha256', $map);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $markdown = "# Numeros — lecture seule\n\nComptes et identifiants uniquement ; aucun rattachement choisi.\n\n```json\n" . $json . "```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A16_OUTPUT_CREATE');
        }
        foreach (['numeros.json' => $json, 'numeros.md' => $markdown] as $file => $text) {
            $handle = fopen($out . '/' . $file, 'xb');
            if (!$handle || !chmod($out . '/' . $file, 0600) || fwrite($handle, $text) !== strlen($text)) {
                throw new \RuntimeException('A16_OUTPUT_WRITE');
            }
            fclose($handle);
        }
        return 0;
    }
}
