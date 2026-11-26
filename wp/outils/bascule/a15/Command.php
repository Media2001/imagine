<?php

declare(strict_types=1);

namespace Imagine\EmailInventory;

final class Command
{
    public static function main(array $args): int
    {
        $o = [];
        foreach (array_slice($args, 1) as $arg) {
            if (!preg_match('/\A--(wp-path|output|audit)=(.+)\z/D', $arg, $m) || isset($o[$m[1]])) {
                throw new \RuntimeException('A15_USAGE');
            }
            $o[$m[1]] = $m[2];
        }
        if (count($o) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A15_USAGE');
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
            throw new \RuntimeException('A15_OUTPUT_UNSAFE');
        }
        $out = $parent . '/' . $base;
        if (file_exists($out) || is_link($out)) {
            throw new \RuntimeException('A15_OUTPUT_EXISTS');
        }
        $audit = realpath($o['audit']);
        if (
            !$audit || !is_file($audit) || is_link($o['audit']) || filesize($audit) > 16777216
            || dirname(dirname($audit)) !== $parent
        ) {
            throw new \RuntimeException('A15_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (
            ($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true
            || !isset($photo['sections']['database']['tables'], $photo['sections']['commerce']['order_storage'])
        ) {
            throw new \RuntimeException('A15_AUDIT_GUARD');
        }
        if (getenv('A15_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
            throw new \RuntimeException('A15_CONFINEMENT_REQUIRED');
        }
        $report = Inventory::collect($site);
        if ($report['storage'] !== $photo['sections']['commerce']['order_storage']) {
            throw new \RuntimeException('A15_AUDIT_STORAGE_MISMATCH');
        }
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $markdown = "# Emails declares — lecture seule\n\nRegistre WC_Emails reellement charge, "
            . "pas un historique d'envoi. Aucun email declenche.\n\n";
        foreach ($report['summary']['active_by_extension'] as $extension => $count) {
            $markdown .= $extension . ' : ' . $count . " actif(s)\n";
        }
        $markdown .= 'Gabarits surcharges distincts : '
            . $report['summary']['overridden_template_files'] . "\n\n```json\n"
            . json_encode(
                $report,
                JSON_PRETTY_PRINT | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR
            ) . "\n```\n";
        if (!mkdir($out, 0700)) {
            throw new \RuntimeException('A15_OUTPUT_CREATE');
        }
        foreach (['emails.json' => $json, 'emails.md' => $markdown] as $file => $text) {
            $handle = fopen($out . '/' . $file, 'xb');
            if (!$handle || !chmod($out . '/' . $file, 0600) || fwrite($handle, $text) !== strlen($text)) {
                throw new \RuntimeException('A15_OUTPUT_WRITE');
            }
            fclose($handle);
        }
        return 0;
    }
}
