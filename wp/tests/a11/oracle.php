<?php

declare(strict_types=1);

$ids = get_option('a11_fixture_ids');
$expected = [];
$add = static function ($url, string $nature, string $type) use (&$expected): void {
    if (is_wp_error($url) || !$url) {
        throw new RuntimeException('ORACLE_URL:' . $nature . ':' . $type . ':' . json_encode(get_post_type_object($type)));
    }
    $p = wp_parse_url($url);
    $relative = ($p['path'] ?? '/') . (isset($p['query']) ? '?' . $p['query'] : '');
    $expected[$relative][] = [$nature, $type];
};
foreach (['article' => 'article', 'unicode' => 'article', 'parent' => 'page', 'child' => 'page', 'story' => 'article', 'shop' => 'page', 'product' => 'produit'] as $key => $nature) {
    $add(get_permalink($ids[$key]), $nature, get_post_type($ids[$key]));
}
if (get_option('wp_attachment_pages_enabled')) {
    foreach (['attachment', 'unattached'] as $key) {
        $add(get_attachment_link($ids[$key]), 'pièce jointe', 'attachment');
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
echo 'A11_JSON=' . json_encode(['expected' => $expected, 'excluded' => ['draft' => 1, 'private' => 1, 'password' => 1, 'attachment_parent_not_public' => 1, 'attachment_pages_disabled' => get_option('wp_attachment_pages_enabled') ? 0 : 2], 'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION]]) . "\n";
