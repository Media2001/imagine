<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
register_post_type('a16_numero', ['public' => false]);
register_post_type('a16_article', ['public' => false]);
register_taxonomy('a16_theme', 'a16_article');
$issues = [];
for ($n = 1; $n <= 3; $n++) {
    $issues[] = wp_insert_post(['post_type' => 'a16_numero', 'post_status' => 'publish',
        'post_title' => 'A16_TITLE_PRIVATE_CANARY', 'post_date_gmt' => '2026-0' . $n . '-01 12:00:00']);
}
$one = wp_insert_term('Theme fictif', 'a16_theme')['term_id'];
$two = wp_insert_term('Autre theme fictif', 'a16_theme')['term_id'];
$articles = [];
foreach (['publish', 'draft', 'publish', 'publish'] as $i => $state) {
    $id = wp_insert_post(['post_type' => 'a16_article', 'post_status' => $state,
        'post_title' => 'A16_ARTICLE_PRIVATE_CANARY', 'post_content' => 'A16_TEXT_PRIVATE_CANARY',
        'post_date_gmt' => '2025-02-01 12:00:00']);
    $articles[] = $id;
    if ($i < 3) {
        add_post_meta($id, '_a16_numero_id', (string) $issues[$i < 2 ? 2 : 1]);
    }
    if ($i !== 0) {
        wp_set_object_terms($id, $i === 1 ? [$one, $two] : [$one], 'a16_theme');
    }
}
$uploads = wp_upload_dir();
$media = [];
foreach (['present.pdf', 'missing.pdf', 'present.jpg', 'missing.jpg'] as $i => $file) {
    $id = wp_insert_attachment(['post_status' => 'inherit', 'post_mime_type' => $i < 2 ? 'application/pdf' : 'image/jpeg',
        'post_title' => 'A16_MEDIA_PRIVATE_CANARY', 'post_parent' => $i < 2 ? 0 : $articles[0]]);
    add_post_meta($id, '_wp_attached_file', $file);
    if ($i % 2 === 0) {
        file_put_contents($uploads['basedir'] . '/' . $file, 'fictif');
    }
    $media[] = $id;
}
add_post_meta($issues[2], '_a16_pdf_id', (string) $media[0]);
add_post_meta($issues[1], '_a16_pdf_id', (string) $media[1]);
add_post_meta($articles[1], '_thumbnail_id', (string) $media[2]);
echo 'A16_JSON=' . json_encode(['issues' => $issues, 'articles' => $articles, 'media' => $media]) . "\n";
