<?php

declare(strict_types=1);

namespace Imagine\IssueInventory;

final class Mapping
{
    public static function validate(array $m): array
    {
        $keys = array_keys($m);
        $keys = array_values(array_diff($keys, ['numero_source', 'racine_privee']));
        if (isset($m['racine_privee']) && (!is_string($m['racine_privee'])
            || !preg_match('~\A/(?:[^/\x00-\x1f\\\\:]+/)*[^/\x00-\x1f\\\\:]+\z~D', $m['racine_privee'])
            || preg_match('~(?:^|/)\.\.?(/|$)~', $m['racine_privee']))) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        if (array_key_exists('racine_privee', $m) && $m['racine_privee'] === null) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        if (!in_array($m['numero_source'] ?? 'post_type', ['post_type', 'taxonomy'], true)) {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        sort($keys);
        $linkKeys = is_array($m['liaison'] ?? null) ? array_keys($m['liaison']) : [];
        sort($linkKeys);
        if (
            $keys !== ['article_type', 'date_cle', 'liaison', 'numero_type', 'pdf_cle', 'thematique', 'version']
            || $m['version'] !== 1 || !is_array($m['liaison'])
            || $linkKeys !== ['cle', 'source']
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
