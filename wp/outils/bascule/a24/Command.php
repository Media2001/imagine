<?php

declare(strict_types=1);

namespace Imagine\ShippingAddresses;

final class Command
{
    public static function main(array $arguments): int
    {
        $options = [];
        foreach (array_slice($arguments, 1) as $argument) {
            if (!preg_match('/\A--(wp-path|audit|output)=(.+)\z/D', $argument, $match) || isset($options[$match[1]])) {
                throw new \RuntimeException('A24_USAGE');
            }
            $options[$match[1]] = $match[2];
        }
        if (count($options) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A24_USAGE');
        }
        if (getenv('A24_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A24_CONFINEMENT_REQUIRED');
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
            throw new \RuntimeException('A24_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A24_OUTPUT_EXISTS');
        }
        $audit = realpath($options['audit']);
        if (
            !$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A24_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
        ) {
            throw new \RuntimeException('A24_AUDIT_GUARD');
        }
        $report = Inventory::collect($site);
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A24_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $flags = JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR;
        $json = json_encode($report, $flags) . "\n";
        $markdown = "# Adresses d’expédition — lecture seule\n\n"
            . "Comptes seulement ; aucune adresse ni décision postale.\n\n```json\n" . $json . "```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A24_OUTPUT_CREATE');
        }
        foreach (['expedition.json' => $json, 'expedition.md' => $markdown] as $name => $text) {
            $stream = fopen($out . '/' . $name, 'xb');
            if (!$stream || !chmod($out . '/' . $name, 0600) || fwrite($stream, $text) !== strlen($text)) {
                throw new \RuntimeException('A24_OUTPUT_WRITE');
            }
            fclose($stream);
        }
        return 0;
    }
}
