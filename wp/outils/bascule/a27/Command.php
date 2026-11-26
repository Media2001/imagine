<?php

declare(strict_types=1);

namespace Imagine\SavedPayments;

final class Command
{
    public static function main(array $arguments): int
    {
        $options = [];
        foreach (array_slice($arguments, 1) as $argument) {
            if (!preg_match('/\A--(wp-path|audit|output)=(.+)\z/D', $argument, $m) || isset($options[$m[1]])) {
                throw new \RuntimeException('A27_USAGE');
            }
            $options[$m[1]] = $m[2];
        }
        if (count($options) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A27_USAGE');
        }
        if (getenv('A27_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A27_CONFINEMENT_REQUIRED');
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
            throw new \RuntimeException('A27_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A27_OUTPUT_EXISTS');
        }
        $audit = realpath($options['audit']);
        if (
            !$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A27_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
            || !is_string($photo['generated_at_utc'] ?? null)
        ) {
            throw new \RuntimeException('A27_AUDIT_GUARD');
        }
        Analysis::clock($photo['generated_at_utc']);
        $report = Inventory::collect($site, $photo['generated_at_utc']);
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A27_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE
            | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $markdown = "# Moyens de paiement enregistrés — lecture seule\n\n"
            . "Comptes seulement ; aucune garantie de renouvellement.\n\n```json\n" . $json . "```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A27_OUTPUT_CREATE');
        }
        foreach (['paiements.json' => $json, 'paiements.md' => $markdown] as $name => $text) {
            $h = fopen($out . '/' . $name, 'xb');
            if (!$h || !chmod($out . '/' . $name, 0600) || fwrite($h, $text) !== strlen($text)) {
                throw new \RuntimeException('A27_OUTPUT_WRITE');
            }
            fclose($h);
        }
        return 0;
    }
}
