<?php

declare(strict_types=1);

namespace Imagine\IssueInventory;

final class Mapping
{
    public static function validate(array $m): array
    {
        $keys = array_keys($m);
        $keys = array_values(array_diff($keys, ['numero_source']));
        if (!in_array($m['numero_source'] ?? 'post_type', ['post_type', 'taxonomy'], true)) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        sort($keys);
        if (
            $keys !== ['article_type', 'date_cle', 'liaison', 'numero_type', 'pdf_cle', 'thematique', 'version']
            || $m['version'] !== 1 || !is_array($m['liaison'])
            || array_keys($m['liaison']) !== ['source', 'cle']
            || !in_array($m['liaison']['source'], ['postmeta', 'taxonomy', 'post_parent'], true)
        ) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        $identifiers = [$m['numero_type'], $m['article_type'], $m['date_cle'],
            $m['pdf_cle'], $m['thematique'], $m['liaison']['cle']];
        foreach ($identifiers as $key) {
            if (!is_string($key) || !preg_match('/\A[a-zA-Z_][a-zA-Z0-9_-]{0,99}\z/D', $key)) {
                throw new \RuntimeException('A16_MAPPING_INVALID');
            }
        }
        return $m;
    }
}
