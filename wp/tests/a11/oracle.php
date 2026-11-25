<?php

declare(strict_types=1);

$ids = get_option('a11_fixture_ids');
$expected = [];
$fields = [];
$add = static function ($url, string $nature, string $type, string $status = 'public', ?string $date = null) use (&$expected, &$fields): void {
    if (is_wp_error($url) || !$url) {
        throw new RuntimeException('ORACLE_URL:' . $nature . ':' . $type . ':' . json_encode(get_post_type_object($type)));
    }
    $p = wp_parse_url($url);
    $relative = ($p['path'] ?? '/') . (isset($p['query']) ? '?' . $p['query'] : '');
    $expected[$relative][] = [$nature, $type];
    $fields[$relative] ??= ['etat_publication' => $status, 'derniere_modification_utc' => $date];
};
foreach (['article' => 'article', 'unicode' => 'article', 'parent' => 'page', 'child' => 'page', 'story' => 'article', 'shop' => 'page', 'product' => 'produit'] as $key => $nature) {
    $post = get_post($ids[$key]);
    $add(get_permalink($post), $nature, $post->post_type, $post->post_status, get_post_modified_time('Y-m-d\TH:i:s\Z', true, $post));
}
if (get_option('wp_attachment_pages_enabled')) {
    foreach (['attachment', 'unattached'] as $key) {
        $post = get_post($ids[$key]);
        $add(get_attachment_link($post), 'pièce jointe', 'attachment', $post->post_status, get_post_modified_time('Y-m-d\TH:i:s\Z', true, $post));
    }
}
foreach (get_taxonomies(['public' => true], 'objects') as $tax) {
    if (!$tax->publicly_queryable) {
        continue;
    }
    foreach (get_terms(['taxonomy' => $tax->name, 'hide_empty' => false]) as $term) {
        $add(get_term_link($term), 'terme de taxonomie', $tax->name);
    }
}
$add(get_author_posts_url((int) get_option('a11_fixture_author')), "archive d'auteur", 'author');
foreach (['post', 'product', 'a11_story'] as $type) {
    $add(get_post_type_archive_link($type), 'archive de type de contenu', $type);
}
ksort($expected);
echo 'A11_JSON=' . json_encode(['expected' => $expected, 'fields' => $fields, 'permaliens' => ['structure' => get_option('permalink_structure'), 'base_categories' => get_option('category_base'), 'base_etiquettes' => get_option('tag_base'), 'woocommerce' => wc_get_permalink_structure()], 'excluded' => ['draft' => 1, 'private' => 1, 'password' => 1, 'attachment_parent_not_public' => 1, 'attachment_pages_disabled' => get_option('wp_attachment_pages_enabled') ? 0 : 2], 'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION]]) . "\n";
