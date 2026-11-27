<?php

declare(strict_types=1);

namespace Imagine\ArchiveTests;

register_post_type('a16_numero', ['public' => false]);
register_post_type('a16_article', ['public' => false]);
register_post_type('PRIVATE_TYPE_CANARY', ['public' => false]);
register_taxonomy('a16_theme', 'a16_article');
update_option('active_plugins', []);
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->posts} WHERE post_status='publish'");
$root = ABSPATH . 'wp-content/uploads';
wp_mkdir_p($root);
$issues = [];
$articles = [];
for ($i = 0; $i < 12; $i++) {
    $date = (2010 + $i) . '-01-01 12:00:00';
    $issues[] = wp_insert_post(['post_type' => 'a16_numero', 'post_status' => 'publish',
        'post_title' => 'A33_TITLE_CANARY', 'post_date' => $date, 'post_date_gmt' => $date]);
    update_post_meta($issues[$i], '_a16_pdf_id', '0');
    $articles[] = wp_insert_post(['post_type' => 'a16_article', 'post_status' => 'publish',
        'post_title' => 'A33_ARTICLE_CANARY', 'post_date' => $date, 'post_date_gmt' => $date,
        'post_parent' => $issues[$i]]);
    update_post_meta($articles[$i], '_a16_numero_id', (string) $issues[$i]);
}
$post = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish', 'post_title' => 'A33_POST_CANARY',
    'post_date' => '2022-01-01 12:00:00', 'post_date_gmt' => '2022-01-01 12:00:00']);
wp_insert_post(['post_type' => 'PRIVATE_TYPE_CANARY', 'post_status' => 'publish',
    'post_title' => 'A33_OTHER_CANARY', 'post_date' => '2023-01-01 12:00:00', 'post_date_gmt' => '2023-01-01 12:00:00']);
$draft = wp_insert_post(['post_type' => 'page', 'post_status' => 'draft']);
$media = [];
foreach ([[$issues[0], 7], [$articles[0], 11], [$articles[0], null], [$articles[1], 13],
    [$issues[11], 17], [$articles[11], 19], [0, 23], [999999, 29], [$draft, 31], [$post, 0]] as $i => [$parent, $size]) {
    $relative = 'A33_FILE_CANARY_' . $i . '.bin';
    if ($size !== null) {
        file_put_contents($root . '/' . $relative, str_repeat('x', $size));
    }
    $id = wp_insert_post(['post_type' => 'attachment', 'post_status' => 'inherit',
        'post_parent' => $parent, 'post_title' => 'A33_MEDIA_CANARY', 'post_mime_type' => 'application/octet-stream']);
    update_post_meta($id, '_wp_attached_file', $relative);
    $media[] = $id;
}
echo 'A33_JSON=' . json_encode(['issues' => $issues, 'articles' => $articles, 'media' => $media], JSON_THROW_ON_ERROR) . "\n";
