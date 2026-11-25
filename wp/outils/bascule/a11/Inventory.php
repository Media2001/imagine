<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

final class Inventory
{
    private array $rows = [];
    private string $home;

    private function add(string $url, string $nature, string $type, string $status = 'public', ?string $modified = null): void
    {
        $relative = Address::relative($url, $this->home);
        $context = ['nature' => $nature, 'type_contenu' => $type];
        if (!isset($this->rows[$relative])) {
            $this->rows[$relative] = ['ancienne' => $relative, 'nature' => $nature, 'type_contenu' => $type, 'etat_publication' => $status, 'derniere_modification_utc' => $modified, 'contextes' => []];
        }
        if (!in_array($context, $this->rows[$relative]['contextes'], true)) {
            $this->rows[$relative]['contextes'][] = $context;
        }
    }

    private static function publicAttachment(\WP_Post $post): bool
    {
        $seen = [];
        while ($post->post_parent) {
            if (isset($seen[$post->ID])) {
                throw new \RuntimeException('A11_ATTACHMENT_PARENT_CYCLE');
            }
            $seen[$post->ID] = true;
            $post = get_post($post->post_parent);
            if (!$post || $post->post_password !== '') {
                return false;
            }
            if ($post->post_type !== 'attachment') {
                return $post->post_status === 'publish' && is_post_publicly_viewable($post);
            }
        }
        return true;
    }

    public function collect(): array
    {
        global $wpdb;
        $this->home = home_url('/');
        $excluded = ['draft' => 0, 'private' => 0, 'password' => 0, 'attachment_parent_not_public' => 0, 'attachment_pages_disabled' => 0];
        $other = [];
        $authors = [];
        $types = get_post_types(['public' => true], 'objects');
        $types = array_filter($types, static fn ($t): bool => is_post_type_viewable($t));
        foreach ($types as $type) {
            $ids = $wpdb->get_col($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_type = %s ORDER BY ID", $type->name));
            foreach ($ids as $id) {
                $post = get_post((int) $id);
                if (in_array($post->post_status, ['draft', 'auto-draft', 'private'], true)) {
                    $excluded[$post->post_status === 'auto-draft' ? 'draft' : $post->post_status]++;
                    continue;
                }
                if ($post->post_password !== '') {
                    $excluded['password']++;
                    continue;
                }
                if ($post->post_type === 'attachment') {
                    if (!in_array($post->post_status, ['inherit', 'publish'], true)) {
                        $other[$post->post_status] = ($other[$post->post_status] ?? 0) + 1;
                        continue;
                    }
                    if (!self::publicAttachment($post)) {
                        $excluded['attachment_parent_not_public']++;
                        continue;
                    }
                    if (!get_option('wp_attachment_pages_enabled', true)) {
                        $excluded['attachment_pages_disabled']++;
                        continue;
                    }
                    $url = get_attachment_link($post);
                    $nature = 'pièce jointe';
                } else {
                    if ($post->post_status !== 'publish') {
                        $other[$post->post_status] = ($other[$post->post_status] ?? 0) + 1;
                        continue;
                    }
                    $url = get_permalink($post);
                    $nature = match ($post->post_type) {
                        'page' => 'page',
                        'product' => 'produit',
                        default => 'article',
                    };
                    if (post_type_supports($post->post_type, 'author') && $post->post_author) {
                        $authors[(int) $post->post_author] = true;
                    }
                }
                if (!$url) {
                    throw new \RuntimeException('A11_NATIVE_URL_MISSING');
                }
                $date = preg_match('/\A[1-9][0-9]{3}-[0-9]{2}-[0-9]{2} [0-9:]{8}\z/D', $post->post_modified_gmt) ? str_replace(' ', 'T', $post->post_modified_gmt) . 'Z' : null;
                $this->add($url, $nature, $post->post_type, $post->post_status, $date);
            }
        }
        foreach (get_taxonomies(['public' => true], 'objects') as $tax) {
            if (!$tax->publicly_queryable) {
                continue;
            }
            $terms = get_terms(['taxonomy' => $tax->name, 'hide_empty' => false]);
            if (is_wp_error($terms)) {
                throw new \RuntimeException('A11_TERMS_FAILED');
            }
            foreach ($terms as $term) {
                $url = get_term_link($term);
                if (is_wp_error($url)) {
                    throw new \RuntimeException('A11_NATIVE_URL_MISSING');
                }
                $this->add($url, 'terme de taxonomie', $tax->name);
            }
        }
        ksort($authors);
        foreach (array_keys($authors) as $id) {
            $this->add(get_author_posts_url($id), "archive d'auteur", 'author');
        }
        foreach ($types as $type) {
            if ($type->has_archive || $type->name === 'post') {
                $url = get_post_type_archive_link($type->name);
                if ($url) {
                    $this->add($url, 'archive de type de contenu', $type->name);
                }
            }
        }
        ksort($this->rows, SORT_STRING);
        ksort($other);
        $counts = [];
        foreach ($this->rows as $row) {
            foreach (array_unique(array_column($row['contextes'], 'nature')) as $nature) {
                $counts[$nature] = ($counts[$nature] ?? 0) + 1;
            }
        }
        ksort($counts);
        return ['schema' => 'imagine-a11-public-addresses-v1', 'read_only' => true, 'total' => count($this->rows), 'par_nature' => $counts, 'exclus' => $excluded, 'autres_etats_non_listes' => $other, 'permaliens' => ['structure' => get_option('permalink_structure'), 'base_categories' => get_option('category_base'), 'base_etiquettes' => get_option('tag_base'), 'woocommerce' => function_exists('wc_get_permalink_structure') ? wc_get_permalink_structure() : null], 'native_guards' => Runtime::$guards, 'adresses' => array_values($this->rows)];
    }
}
