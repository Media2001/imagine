<?php

declare(strict_types=1);

namespace Imagine\ThirdParties;

final class Command
{
    public static function main(array $arguments): int
    {
        $options = [];
        foreach (array_slice($arguments, 1) as $argument) {
            if (!preg_match('/\A--(wp-path|audit|output|a16-map)=(.+)\z/D', $argument, $m) || isset($options[$m[1]])) {
                throw new \RuntimeException('A26_USAGE');
            }
            $options[$m[1]] = $m[2];
        }
        if (count(array_intersect(['wp-path', 'audit', 'output'], array_keys($options))) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A26_USAGE');
        }
        if (getenv('A26_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A26_CONFINEMENT_REQUIRED');
        }
        $site = realpath($options['wp-path']);
        $parent = realpath(dirname($options['output']));
        $base = basename($options['output']);
        $repository = dirname(__DIR__, 4);
        if (!is_file($repository . '/wp/outils/bascule/audit')) {
            $repository = dirname(__DIR__);
        }
        if (
            !$site || !$parent || !is_dir($site) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)
            || !\Imagine\ContentInventory\Command::disjointOutput($parent, $site, $repository)
        ) {
            throw new \RuntimeException('A26_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A26_OUTPUT_EXISTS');
        }
        $audit = realpath($options['audit']);
        if (
            !$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A26_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
        ) {
            throw new \RuntimeException('A26_AUDIT_GUARD');
        }
        $mapping = null;
        if (isset($options['a16-map'])) {
            $map = realpath($options['a16-map']);
            if (!$map || !is_file($map) || is_link($options['a16-map']) || filesize($map) > 1048576
                || dirname($map) !== dirname($audit)) {
                throw new \RuntimeException('A26_MAPPING_INVALID');
            }
            $mapping = json_decode(file_get_contents($map), true, 32, JSON_THROW_ON_ERROR);
            if (!is_array($mapping)) {
                throw new \RuntimeException('A26_MAPPING_INVALID');
            }
            \Imagine\IssueInventory\Mapping::validate($mapping);
        }
        $report = Inventory::collect($site, $mapping);
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A26_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $flags = JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR;
        $json = json_encode($report, $flags) . "\n";
        $markdown = "# Ressources tierces — lecture seule\n\n"
            . "Déclarations et intégrations statiques ; ni requêtes observées ni conformité.\n\n```json\n"
            . $json . "```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A26_OUTPUT_CREATE');
        }
        foreach (['tiers.json' => $json, 'tiers.md' => $markdown] as $name => $text) {
            $h = fopen($out . '/' . $name, 'xb');
            if (!$h || !chmod($out . '/' . $name, 0600) || fwrite($h, $text) !== strlen($text)) {
                throw new \RuntimeException('A26_OUTPUT_WRITE');
            }
            fclose($h);
        }
        return 0;
    }
}
