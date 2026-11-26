<?php

declare(strict_types=1);

namespace Imagine\IssueInventory;

use Imagine\PublicAddresses\Runtime;
use Imagine\PublicAddresses\RuntimeRefusal;

final class Inventory
{
    private object $db;
    private ?string $privateRoot = null;
    public function __construct(private string $site)
    {
        Runtime::boot($site);
        $this->db = $GLOBALS['wpdb'];
    }
    private function rows(string $sql, array $args = []): array
    {
        $result = $this->db->get_results($args ? $this->db->prepare($sql, ...$args) : $sql, ARRAY_A);
        if (!is_array($result) || $this->db->last_error !== '') {
            throw new \RuntimeException('A16_READ_FAILED');
        }
        return $result;
    }
    private function value(int $id, string $key, bool $term = false): ?string
    {
        $table = $term ? $this->db->termmeta : $this->db->postmeta;
        $owner = $term ? 'term_id' : 'post_id';
        $rows = $this->rows("SELECT meta_value FROM $table WHERE $owner=%d AND BINARY meta_key=BINARY %s", [$id, $key]);
        if (count($rows) > 1) {
            throw new RuntimeRefusal('A16_DUPLICATE_META', ['key' => $key]);
        }
        return $rows[0]['meta_value'] ?? null;
    }
    private function canonical(?string $value, string $key): ?int
    {
        if ($value === null || $value === '' || $value === '0') {
            return null;
        }
        if (!preg_match('/\A[1-9][0-9]{0,17}\z/D', $value)) {
            throw new RuntimeRefusal('A16_NONSCALAR_REFERENCE', ['key' => $key]);
        }
        return (int) $value;
    }
    private function media(int $id): array
    {
        $a = $this->rows("SELECT post_type,post_mime_type FROM {$this->db->posts} WHERE ID=%d", [$id]);
        if (!$a || $a[0]['post_type'] !== 'attachment') {
            return ['exists' => false, 'public' => null, 'pdf' => false];
        }
        $relative = $this->value($id, '_wp_attached_file');
        $upload = get_option('upload_path', '');
        $base = $upload === '' ? $this->site . '/wp-content/uploads'
            : (str_starts_with($upload, '/') ? $upload : $this->site . '/' . $upload);
        if (
            !str_starts_with($base . '/', $this->site . '/')
            || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $base)
        ) {
            throw new \RuntimeException('A16_UPLOAD_PATH_UNSUPPORTED');
        }
        if ($relative === null || $relative === '') {
            return ['exists' => false, 'public' => null, 'pdf' => $a[0]['post_mime_type'] === 'application/pdf'];
        }
        $path = str_starts_with($relative, '/') ? $relative : $base . '/' . $relative;
        $public = str_starts_with($path, $base . '/');
        $private = $this->privateRoot !== null && str_starts_with($path, $this->privateRoot . '/');
        $existing = $path;
        while (!file_exists($existing) && !is_link($existing) && $existing !== dirname($existing)) {
            $existing = dirname($existing);
        }
        if (
            (!$public && !$private) || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $path)
            || is_link($existing) || realpath($existing) !== $existing
        ) {
            throw new \RuntimeException('A16_ATTACHMENT_PATH_UNSAFE');
        }
        return ['exists' => is_file($path), 'public' => $public, 'pdf' => $a[0]['post_mime_type'] === 'application/pdf'];
    }
    public function collect(array $m, int $limit): array
    {
        Mapping::validate($m);
        $this->privateRoot = $m['racine_privee'] ?? null;
        if ($this->privateRoot !== null && (!is_dir($this->privateRoot)
            || realpath($this->privateRoot) !== $this->privateRoot
            || $this->privateRoot === $this->site
            || str_starts_with($this->privateRoot, $this->site . '/')
            || str_starts_with($this->site, $this->privateRoot . '/'))) {
            throw new \RuntimeException('A16_PRIVATE_ROOT_UNSAFE');
        }
        $taxonomy = ($m['numero_source'] ?? 'post_type') === 'taxonomy';
        if (
            $taxonomy && (!taxonomy_exists($m['numero_type'])
            || !is_object_in_taxonomy($m['article_type'], $m['numero_type'])
            || $m['date_cle'] === 'post_date_gmt')
        ) {
            throw new RuntimeRefusal('A16_MAPPING_KEY_ABSENT', ['key' => $m['numero_type']]);
        }
        foreach ([$m['article_type'], ...($taxonomy ? [] : [$m['numero_type']])] as $type) {
            if (!post_type_exists($type)) {
                throw new RuntimeRefusal('A16_MAPPING_KEY_ABSENT', ['key' => $type]);
            }
        }
        if (!taxonomy_exists($m['thematique']) || !is_object_in_taxonomy($m['article_type'], $m['thematique'])) {
            throw new RuntimeRefusal('A16_MAPPING_KEY_ABSENT', ['key' => $m['thematique']]);
        }
        $keys = [[$m['pdf_cle'], $m['numero_type']]];
        if ($m['date_cle'] !== 'post_date_gmt') {
            $keys[] = [$m['date_cle'], $m['numero_type']];
        }
        if ($m['liaison']['source'] === 'postmeta') {
            $keys[] = [$m['liaison']['cle'], $m['article_type']];
        }
        foreach ($keys as [$key, $type]) {
            $exists = $taxonomy && $type === $m['numero_type']
                ? $this->rows("SELECT m.term_id FROM {$this->db->termmeta} m "
                    . "JOIN {$this->db->term_taxonomy} t ON t.term_id=m.term_id "
                    . 'WHERE t.taxonomy=%s AND BINARY m.meta_key=BINARY %s LIMIT 1', [$type, $key])
                : $this->rows("SELECT m.post_id FROM {$this->db->postmeta} m "
                    . "JOIN {$this->db->posts} p ON p.ID=m.post_id "
                    . 'WHERE p.post_type=%s AND BINARY m.meta_key=BINARY %s LIMIT 1', [$type, $key]);
            if (!$exists) {
                throw new RuntimeRefusal('A16_MAPPING_KEY_ABSENT', ['key' => $key]);
            }
        }
        if ($m['liaison']['source'] === 'taxonomy' && (!$taxonomy || $m['liaison']['cle'] !== $m['numero_type'])) {
            // No arbitrary term-to-post ID equivalence is inferred.
            throw new \RuntimeException('A16_TAXONOMY_NUMBER_MAPPING_REQUIRED');
        }
        if ($taxonomy && $m['liaison']['source'] === 'post_parent') {
            throw new \RuntimeException('A16_MAPPING_INVALID');
        }
        $issues = $taxonomy
            ? $this->rows("SELECT term_id AS ID FROM {$this->db->term_taxonomy} WHERE taxonomy=%s", [$m['numero_type']])
            : $this->rows("SELECT ID,post_date_gmt FROM {$this->db->posts} WHERE post_type=%s", [$m['numero_type']]);
        foreach ($issues as &$issue) {
            $date = $m['date_cle'] === 'post_date_gmt' ? $issue['post_date_gmt']
                : $this->value((int) $issue['ID'], $m['date_cle'], $taxonomy);
            $parsed = is_string($date)
                ? \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $date, new \DateTimeZone('UTC')) : false;
            if (!$parsed || $parsed->format('Y-m-d H:i:s') !== $date || str_starts_with($date, '0000')) {
                throw new RuntimeRefusal('A16_DATE_INVALID', ['key' => $m['date_cle']]);
            }
            $issue['date_utc'] = $parsed->format('Y-m-d\TH:i:s\Z');
        }
        unset($issue);
        usort($issues, static fn(array $a, array $b): int => strcmp($b['date_utc'], $a['date_utc'])
            ?: ((int) $b['ID'] <=> (int) $a['ID']));
        $allIds = array_map('intval', array_column($issues, 'ID'));
        $groups = [];
        $orphans = [];
        $articles = $this->rows("SELECT ID,post_status,post_date_gmt,post_parent FROM {$this->db->posts} "
            . 'WHERE post_type=%s ORDER BY ID', [$m['article_type']]);
        foreach ($articles as $a) {
            $id = (int) $a['ID'];
            $numbers = $m['liaison']['source'] === 'taxonomy'
                ? array_map('intval', array_column($this->rows(
                    "SELECT DISTINCT t.term_id FROM {$this->db->term_relationships} r "
                    . "JOIN {$this->db->term_taxonomy} t ON t.term_taxonomy_id=r.term_taxonomy_id "
                    . 'WHERE r.object_id=%d AND t.taxonomy=%s',
                    [$id, $m['liaison']['cle']]
                ), 'term_id'))
                : [$m['liaison']['source'] === 'post_parent' ? (int) $a['post_parent']
                    : $this->canonical($this->value($id, $m['liaison']['cle']), $m['liaison']['cle'])];
            $numbers = array_intersect($numbers, $allIds);
            if (!$numbers) {
                if ($a['post_status'] === 'publish') {
                    $year = substr($a['post_date_gmt'], 0, 4);
                    $year = preg_match('/\A[1-9][0-9]{3}\z/D', $year) ? (int) $year : 'inconnu';
                    $orphans[$year] = ($orphans[$year] ?? 0) + 1;
                }
                continue;
            }
            foreach ($numbers as $number) {
                $groups[$number][] = $a;
            }
        }
        $result = [];
        foreach (array_slice($issues, 0, $limit) as $issue) {
            $id = (int) $issue['ID'];
            $row = ['id' => $id, 'date_utc' => $issue['date_utc'], 'articles' => 0, 'published_articles' => 0,
                'unpublished_articles' => 0, 'without_theme' => 0, 'multiple_themes' => 0,
                'without_featured_image' => 0, 'attached_media' => 0, 'missing_media_files' => 0];
            $media = [];
            foreach ($groups[$id] ?? [] as $a) {
                $aid = (int) $a['ID'];
                $row['articles']++;
                $row[$a['post_status'] === 'publish' ? 'published_articles' : 'unpublished_articles']++;
                $terms = $this->rows("SELECT DISTINCT t.term_id FROM {$this->db->term_relationships} r "
                    . "JOIN {$this->db->term_taxonomy} t ON t.term_taxonomy_id=r.term_taxonomy_id "
                    . 'WHERE r.object_id=%d AND t.taxonomy=%s', [$aid, $m['thematique']]);
                $row['without_theme'] += (int) !$terms;
                $row['multiple_themes'] += (int) (count($terms) > 1);
                $thumb = $this->canonical($this->value($aid, '_thumbnail_id'), '_thumbnail_id');
                $row['without_featured_image'] += (int) (!$thumb || !$this->media($thumb)['exists']);
                $attached = $this->rows("SELECT ID FROM {$this->db->posts} "
                    . "WHERE post_type='attachment' AND post_parent=%d", [$aid]);
                foreach ($attached as $attachment) {
                    $media[(int) $attachment['ID']] = true;
                }
            }
            foreach (array_keys($media) as $mid) {
                $row['attached_media']++;
                $row['missing_media_files'] += (int) !$this->media($mid)['exists'];
            }
            $pdf = $this->canonical($this->value($id, $m['pdf_cle'], $taxonomy), $m['pdf_cle']);
            $file = $pdf ? $this->media($pdf) : null;
            if ($file && !$file['pdf']) {
                throw new RuntimeRefusal('A16_PDF_REFERENCE_INVALID', ['key' => $m['pdf_cle']]);
            }
            $row['pdf'] = !$pdf ? 'non' : ($file['exists'] ? 'oui' : 'declare_mais_fichier_absent');
            $row['pdf_public'] = $file['public'] ?? null;
            $result[] = $row;
        }
        ksort($orphans);
        $byYear = [];
        foreach ($orphans as $year => $count) {
            $byYear[] = ['year' => $year, 'articles' => $count];
        }
        return ['schema' => 'imagine-a16-issues-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'limit' => $limit, 'issues' => $result, 'orphan_published_by_year' => $byYear];
    }
}
