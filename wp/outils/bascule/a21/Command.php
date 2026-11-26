<?php

declare(strict_types=1);

namespace Imagine\ExternalDoors;

final class Command
{
    public static function main(array $args): int
    {
        $options = [];
        foreach (array_slice($args, 1) as $arg) {
            if (!preg_match('/\A--(wp-path|output|audit|as-of)=(.+)\z/D', $arg, $match) || isset($options[$match[1]])) {
                throw new \RuntimeException('A21_USAGE');
            }
            $options[$match[1]] = $match[2];
        }
        if (!isset($options['wp-path'], $options['output'], $options['audit']) || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A21_USAGE');
        }
        $site = realpath($options['wp-path']);
        $parent = realpath(dirname($options['output']));
        $base = basename($options['output']);
        $repo = dirname(__DIR__, 4);
        if (!is_file($repo . '/wp/outils/bascule/audit')) {
            $repo = dirname(__DIR__);
        }
        if (
            !$site || !$parent || !is_dir($site) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)
            || !\Imagine\ContentInventory\Command::disjointOutput($parent, $site, $repo)
        ) {
            throw new \RuntimeException('A21_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A21_OUTPUT_EXISTS');
        }
        $audit = realpath($options['audit']);
        if (
            !$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A21_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
        ) {
            throw new \RuntimeException('A21_AUDIT_GUARD');
        }
        if (getenv('A21_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A21_CONFINEMENT_REQUIRED');
        }
        $report = Inventory::collect($site, $options['as-of'] ?? gmdate('Y-m-d\TH:i:s\Z'));
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A21_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $flags = JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR;
        $json = json_encode($report, $flags) . "\n";
        $markdown = "# Portes vers l’extérieur — lecture seule\n\n"
            . "Comptes seulement ; aucune révocation ni décision.\n\n```json\n" . $json . "```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A21_OUTPUT_CREATE');
        }
        foreach (['portes.json' => $json, 'portes.md' => $markdown] as $file => $text) {
            $handle = fopen($out . '/' . $file, 'xb');
            if (!$handle || !chmod($out . '/' . $file, 0600) || fwrite($handle, $text) !== strlen($text)) {
                throw new \RuntimeException('A21_OUTPUT_WRITE');
            }
            fclose($handle);
        }
        return 0;
    }
}
