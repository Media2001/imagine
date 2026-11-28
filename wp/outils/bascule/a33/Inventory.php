<?php

declare(strict_types=1);

namespace Imagine\ArchiveWeight;

final class Inventory
{
    private static function rows(string $sql, array $args = []): array
    {
        global $wpdb;
        $rows = $wpdb->get_results($args ? $wpdb->prepare($sql, ...$args) : $sql, ARRAY_A);
        if (!is_array($rows) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A33_READ_FAILED');
        }
        return $rows;
    }

    private static function size(string $site, ?string $relative): ?int
    {
        $upload = get_option('upload_path', '');
        $base = $upload === '' ? $site . '/wp-content/uploads'
            : (str_starts_with($upload, '/') ? $upload : $site . '/' . $upload);
        if (
            !str_starts_with($base . '/', $site . '/')
            || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $base)
        ) {
            throw new \RuntimeException('A33_UPLOAD_PATH_UNSUPPORTED');
        }
        if ($relative === null || $relative === '') {
            return null;
        }
        $path = str_starts_with($relative, '/') ? $relative : $base . '/' . $relative;
        $ancestor = $path;
        while (!file_exists($ancestor) && !is_link($ancestor) && $ancestor !== dirname($ancestor)) {
            $ancestor = dirname($ancestor);
        }
        if (
            !str_starts_with($path, $base . '/')
            || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $path)
            || is_link($ancestor) || realpath($ancestor) !== $ancestor
        ) {
            throw new \RuntimeException('A33_ATTACHMENT_PATH_UNSAFE');
        }
        if (!is_file($path)) {
            return null;
        }
        $size = filesize($path);
        if (!is_int($size) || $size < 0) {
            throw new \RuntimeException('A33_STAT_FAILED');
        }
        return $size;
    }

    public static function collect(string $site, array $mapping): array
    {
        \Imagine\IssueInventory\Mapping::validate($mapping);
        Analysis::editorial($mapping);
        // The accepted implementation alone owns validation, ordering and refusal semantics.
        $a16 = (new \Imagine\IssueInventory\Inventory($site))->collect($mapping, 10);
        $recentIds = array_column($a16['issues'], 'id');
        global $wpdb;
        $taxonomy = ($mapping['numero_source'] ?? 'post_type') === 'taxonomy';
        $recent = $taxonomy ? [] : array_fill_keys($recentIds, true);
        $p = $wpdb->posts;
        $m = $wpdb->postmeta;
        // A16 has already validated these scalar references (post or term metadata).
        $pdfs = [];
        $pdfTable = $taxonomy ? $wpdb->termmeta : $m;
        $pdfOwner = $taxonomy ? 'term_id' : 'post_id';
        foreach ($recentIds as $issueId) {
            $refs = self::rows("SELECT meta_value FROM $pdfTable WHERE $pdfOwner=%d "
                . 'AND BINARY meta_key=BINARY %s', [(int) $issueId, $mapping['pdf_cle']]);
            $pdf = (int) ($refs[0]['meta_value'] ?? 0);
            if ($pdf > 0) {
                $pdfs[$pdf] = true;
            }
        }
        // Never enumerate an order store or read a commerce object's values.
        $excluded = "('" . implode("','", Analysis::NON_EDITORIAL) . "')";
        $contents = self::rows("SELECT ID,post_type,post_status,post_date_gmt,post_parent FROM $p "
            . "WHERE BINARY post_type NOT IN $excluded ORDER BY ID");
        $outside = [];
        $counts = [];
        $anonymousTypes = [];
        foreach ($contents as $content) {
            $id = (int) $content['ID'];
            $keep = !$taxonomy && isset($recent[$id]);
            if ($content['post_type'] === $mapping['article_type']) {
                if ($mapping['liaison']['source'] === 'taxonomy') {
                    $links = array_column(self::rows("SELECT DISTINCT t.term_id FROM {$wpdb->term_relationships} r "
                        . "JOIN {$wpdb->term_taxonomy} t ON t.term_taxonomy_id=r.term_taxonomy_id "
                        . 'WHERE r.object_id=%d AND t.taxonomy=%s', [$id, $mapping['liaison']['cle']]), 'term_id');
                } elseif ($mapping['liaison']['source'] === 'post_parent') {
                    $links = [$content['post_parent']];
                } else {
                    $links = array_column(self::rows("SELECT meta_value FROM $m WHERE post_id=%d "
                        . 'AND BINARY meta_key=BINARY %s', [$id, $mapping['liaison']['cle']]), 'meta_value');
                }
                // A16 already validated all scalar references; no alternate date/rule parser here.
                $keep = $keep || (bool) array_intersect(array_map('intval', $links), $recentIds);
            }
            if ($keep) {
                $recent[$id] = true;
            } elseif ($content['post_status'] === 'publish') {
                $year = Analysis::year($content['post_date_gmt']);
                $outside[$id] = $year;
                $type = Analysis::type($content['post_type'], $mapping);
                $group = 0;
                if ($type === 'autre') {
                    $anonymousTypes[$content['post_type']] ??= count($anonymousTypes) + 1;
                    $group = $anonymousTypes[$content['post_type']];
                }
                $key = $type . ':' . $group . ':' . $year;
                $counts[$key] ??= ['type' => $type, 'type_group' => $group, 'year' => $year, 'count' => 0];
                $counts[$key]['count']++;
            }
        }
        ksort($counts, SORT_STRING);
        $imported = (bool) self::rows("SELECT option_id FROM {$wpdb->options} "
            . "WHERE option_name='imagine_staging_disabled_plugins'");
        $attachments = self::rows("SELECT a.ID,a.post_parent,parent.ID AS parent_exists,m.meta_value AS attached_path "
            . "FROM $p a LEFT JOIN $p parent ON parent.ID=a.post_parent "
            . "LEFT JOIN $m m ON m.post_id=a.ID AND BINARY m.meta_key=BINARY '_wp_attached_file' "
            . "WHERE BINARY a.post_type=BINARY 'attachment' ORDER BY a.ID");
        $seen = [];
        $byYear = [];
        $orphans = [];
        $kept = [];
        $other = [];
        foreach ($attachments as $attachment) {
            $id = (int) $attachment['ID'];
            if (isset($seen[$id])) {
                throw new \RuntimeException('A33_DUPLICATE_ATTACHED_FILE');
            }
            $seen[$id] = true;
            $size = self::size($site, $attachment['attached_path']);
            $parent = (int) $attachment['post_parent'];
            if ($parent === 0 || $attachment['parent_exists'] === null) {
                $orphans[] = $size;
            }
            // Structural orphans remain separately visible, including referenced PDFs.
            if (isset($pdfs[$id]) || isset($recent[$parent])) {
                $kept[] = $size;
            } elseif (isset($outside[$parent])) {
                $byYear[(string) $outside[$parent]][] = $size;
            } elseif ($parent !== 0 && $attachment['parent_exists'] !== null) {
                $other[] = $size;
            }
        }
        ksort($byYear, SORT_STRING);
        $years = [];
        foreach ($byYear as $year => $sizes) {
            $years[] = ['year' => $year === 'inconnu' ? $year : (int) $year,
                'files' => Analysis::files($sizes, $imported)];
        }
        return ['schema' => 'imagine-a33-archives-v1', 'read_only' => true, 'imported' => $imported,
            'selected_issues' => count($recentIds), 'published_outside' => array_values($counts),
            'outside_media_by_year' => $years, 'orphan_media' => Analysis::files($orphans, $imported),
            'recent_media' => Analysis::files($kept, $imported), 'other_media' => Analysis::files($other, $imported),
            'excluded_directories_bytes' => $imported ? 'inconnu après import' : 'non évalué'];
    }
}
