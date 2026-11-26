<?php

declare(strict_types=1);

namespace Imagine\ThirdParties;

final class Issues
{
    public static function select(object $db, array $mapping): array
    {
        \Imagine\IssueInventory\Mapping::validate($mapping);
        $read = static function (string $sql, array $args = []) use ($db): array {
            $rows = $db->get_results($args ? $db->prepare($sql, ...$args) : $sql, ARRAY_A);
            if (!is_array($rows) || $db->last_error !== '') {
                throw new \RuntimeException('A26_QUERY_FAILED');
            }
            return $rows;
        };
        $taxonomy = ($mapping['numero_source'] ?? 'post_type') === 'taxonomy';
        $link = $mapping['liaison'];
        if (
            !post_type_exists($mapping['article_type'])
            || ($taxonomy && (!taxonomy_exists($mapping['numero_type'])
                || !is_object_in_taxonomy($mapping['article_type'], $mapping['numero_type'])
                || $mapping['date_cle'] === 'post_date_gmt' || $link['source'] === 'post_parent'))
            || (!$taxonomy && !post_type_exists($mapping['numero_type']))
            || ($link['source'] === 'taxonomy' && (!$taxonomy || $link['cle'] !== $mapping['numero_type']))
        ) {
            throw new \RuntimeException('A26_MAPPING_INVALID');
        }
        $meta = static function (int $id, string $key, bool $term) use ($read, $db): ?string {
            $table = $term ? $db->termmeta : $db->postmeta;
            $owner = $term ? 'term_id' : 'post_id';
            $rows = $read(
                "SELECT meta_value FROM {$table} WHERE {$owner}=%d AND BINARY meta_key=BINARY %s",
                [$id, $key]
            );
            if (count($rows) > 1) {
                throw new \RuntimeException('A26_MAPPING_INVALID');
            }
            return $rows[0]['meta_value'] ?? null;
        };
        $issues = $taxonomy
            ? $read("SELECT term_id AS ID FROM {$db->term_taxonomy} WHERE taxonomy=%s", [$mapping['numero_type']])
            : $read("SELECT ID,post_date_gmt FROM {$db->posts} WHERE post_type=%s", [$mapping['numero_type']]);
        if ($issues === []) {
            throw new \RuntimeException('A26_MAPPING_INVALID');
        }
        foreach ($issues as &$issue) {
            $date = $mapping['date_cle'] === 'post_date_gmt' ? $issue['post_date_gmt']
                : $meta((int) $issue['ID'], $mapping['date_cle'], $taxonomy);
            $parsed = is_string($date)
                ? \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $date, new \DateTimeZone('UTC')) : false;
            if (!$parsed || $parsed->format('Y-m-d H:i:s') !== $date || str_starts_with($date, '0000')) {
                throw new \RuntimeException('A26_MAPPING_INVALID');
            }
            $issue['date'] = $date;
        }
        unset($issue);
        usort($issues, static fn(array $a, array $b): int => strcmp($b['date'], $a['date'])
            ?: ((int) $b['ID'] <=> (int) $a['ID']));
        $recent = array_map('intval', array_column(array_slice($issues, 0, 10), 'ID'));
        $articles = $read(
            "SELECT ID,post_parent FROM {$db->posts} WHERE post_status='publish' AND post_type=%s",
            [$mapping['article_type']]
        );
        $selected = [];
        foreach ($articles as $article) {
            $id = (int) $article['ID'];
            if ($link['source'] === 'taxonomy') {
                $numbers = array_map('intval', array_column($read(
                    "SELECT DISTINCT t.term_id FROM {$db->term_relationships} r JOIN {$db->term_taxonomy} t"
                    . ' ON t.term_taxonomy_id=r.term_taxonomy_id WHERE r.object_id=%d AND t.taxonomy=%s',
                    [$id, $link['cle']]
                ), 'term_id'));
            } elseif ($link['source'] === 'post_parent') {
                $numbers = [(int) $article['post_parent']];
            } else {
                $value = $meta($id, $link['cle'], false);
                if ($value !== null && $value !== '' && !preg_match('/\A(?:0|[1-9][0-9]{0,17})\z/D', $value)) {
                    throw new \RuntimeException('A26_MAPPING_INVALID');
                }
                $numbers = [(int) $value];
            }
            if (array_intersect($numbers, $recent)) {
                $selected[] = $id;
            }
        }
        return $selected;
    }
}
