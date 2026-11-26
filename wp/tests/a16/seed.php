<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
register_post_type('a16_numero', ['public' => false]);
register_post_type('a16_article', ['public' => false]);
register_taxonomy('a16_theme', 'a16_article');
register_taxonomy('a16_issue', 'a16_article');
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
        wp_update_post(['ID' => $id, 'post_parent' => $issues[$i < 2 ? 2 : 1]]);
    }
    if ($i !== 0) {
        wp_set_object_terms($id, $i === 1 ? [$one, $two] : [$one], 'a16_theme');
    }
}
$uploads = wp_upload_dir();
$media = [];
foreach (['present.pdf', 'missing.pdf', 'present.jpg', 'missing.jpg'] as $i => $file) {
    $id = wp_insert_attachment(['post_status' => 'inherit',
        'post_mime_type' => $i < 2 ? 'application/pdf' : 'image/jpeg',
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
$terms = [];
for ($n = 0; $n < 3; $n++) {
    $tid = wp_insert_term('A16_TERM_PRIVATE_CANARY_' . $n, 'a16_issue')['term_id'];
    $terms[] = $tid;
    add_term_meta($tid, '_a16_date', '2026-0' . ($n + 1) . '-01 12:00:00');
    if ($n > 0) {
        add_term_meta($tid, '_a16_pdf_id', (string) $media[$n === 2 ? 0 : 1]);
    }
}
foreach (array_slice($articles, 0, 3) as $i => $aid) {
    wp_set_object_terms($aid, [$terms[$i < 2 ? 2 : 1]], 'a16_issue');
}
echo 'A16_JSON=' . json_encode(['issues' => $issues, 'terms' => $terms,
    'articles' => $articles, 'media' => $media]) . "\n";
