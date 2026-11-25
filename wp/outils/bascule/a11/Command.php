<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

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
            if (!preg_match('/\A--(wp-path|output|audit)=(.+)\z/D', $arg, $m) || isset($options[$m[1]])) {
                throw new \RuntimeException('A11_USAGE');
            }
            $options[$m[1]] = $m[2];
        }
        if (count($options) !== 3 || PHP_SAPI !== 'cli') {
            throw new \RuntimeException('A11_USAGE');
        }
        $site = realpath($options['wp-path']);
        $parent = realpath(dirname($options['output']));
        $audit = realpath($options['audit']);
        $base = basename($options['output']);
        if (!$site || !is_dir($site) || !$parent || !is_dir($parent) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', $base)) {
            throw new \RuntimeException('A11_PATH_INVALID');
        }
        $repository = dirname(__DIR__, 4);
        if (!is_file($repository . '/wp/outils/bascule/audit')) {
            $repository = dirname(__DIR__);
        }
        if (self::inside($parent, $site) || self::inside($parent, $repository)) {
            throw new \RuntimeException('A11_OUTPUT_UNSAFE');
        }
        $output = $parent . '/' . $base;
        if (file_exists($output) || is_link($output)) {
            throw new \RuntimeException('A11_OUTPUT_EXISTS');
        }
        if (!$audit || !is_file($audit) || is_link($options['audit']) || filesize($audit) > 16777216 || self::inside($audit, $site) || self::inside($audit, $repository) || dirname(dirname($audit)) !== $parent) {
            throw new \RuntimeException('A11_AUDIT_GUARD');
        }
        $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
        if (($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true || !isset($photo['sections']['database']['tables'])) {
            throw new \RuntimeException('A11_AUDIT_GUARD');
        }
        Runtime::boot($site);
        $report = (new Inventory())->collect();
        $report['audit_sha256'] = hash_file('sha256', $audit);
        $json = json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
        $csv = fopen('php://temp', 'w+');
        fwrite($csv, "\xEF\xBB\xBF");
        fputcsv($csv, ['ancienne', 'nature', 'type_contenu', 'etat_publication', 'derniere_modification_utc', 'autres_contextes'], ';', '"', '');
        foreach ($report['adresses'] as $row) {
            $cells = [$row['ancienne'], $row['nature'], $row['type_contenu'], $row['etat_publication'], $row['derniere_modification_utc'] ?? '', implode(' | ', array_map(static fn (array $c): string => $c['nature'] . ' : ' . $c['type_contenu'], array_slice($row['contextes'], 1)))];
            $cells = array_map(static fn (string $s): string => preg_match('/\A[=+@\-\t\r\n]/', $s) ? "'" . $s : $s, $cells);
            fputcsv($csv, $cells, ';', '"', '');
        }
        rewind($csv);
        $csvText = stream_get_contents($csv);
        fclose($csv);
        $summary = "# Adresses publiques — lecture seule\n\n" . $report['total'] . " adresses uniques. Aucun plan de redirections décidé.\n\n## Par nature\n\n";
        foreach ($report['par_nature'] as $nature => $count) {
            $summary .= '- ' . $nature . ' : ' . $count . "\n";
        }
        $summary .= "\nUne adresse commune (page boutique et archive produit) garde tous ses contextes; les nombres par nature ne sont pas additifs.\n\n## Exclus (comptés, jamais listés) et permaliens\n\n```json\n" . json_encode(['exclus' => $report['exclus'], 'autres_etats_non_listes' => $report['autres_etats_non_listes'], 'permaliens' => $report['permaliens']], JSON_PRETTY_PRINT | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR) . "\n```\n\nDates UTC des contenus seulement; les archives et termes n'ont pas de date native de modification : cellule vide. Pièces jointes : pages natives, pas fichiers téléchargeables.\n";
        if (!mkdir($output, 0700)) {
            throw new \RuntimeException('A11_OUTPUT_CREATE');
        }
        foreach (['adresses.csv' => $csvText, 'adresses.json' => $json, 'resume.md' => $summary] as $name => $content) {
            $handle = fopen($output . '/' . $name, 'xb');
            if ($handle === false) {
                throw new \RuntimeException('A11_OUTPUT_WRITE');
            }
            try {
                if (!chmod($output . '/' . $name, 0600) || fwrite($handle, $content) !== strlen($content)) {
                    throw new \RuntimeException('A11_OUTPUT_WRITE');
                }
            } finally {
                fclose($handle);
            }
        }
        return 0;
    }
}
