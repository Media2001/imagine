<?php

declare(strict_types=1);

// Runs only in the owned fixture, before freezing and giving SELECT credentials to the subject.
if (!post_type_exists('a12_article') || !taxonomy_exists('a12_rubrique')) {
    throw new RuntimeException('A12_FIXTURE_DECLARATIONS_MISSING');
}
// A02 intentionally names its term as a private canary because its report excludes names.
// A12 explicitly permits editorial rubric names: give that inherited synthetic rubric a clear label.
foreach (get_terms(['hide_empty' => false]) as $term) {
    if ($term->name === 'A02_TERM_PRIVATE_CANARY') {
        wp_update_term((int) $term->term_id, $term->taxonomy, ['name' => 'Rubrique A02 fictive']);
    }
}
$ids = [];
foreach (['publish', 'publish', 'draft', 'private', 'trash'] as $i => $status) {
    $ids[] = wp_insert_post([
        'post_type' => 'a12_article', 'post_status' => $status,
        'post_title' => 'A12_TITLE_PRIVATE_CANARY_' . $i,
        'post_content' => 'A12_TEXT_PRIVATE_CANARY',
        'post_date' => ($i === 0 ? '2024' : '2025') . '-02-03 12:00:00',
        'post_date_gmt' => ($i === 0 ? '2024' : '2025') . '-02-03 11:00:00',
    ], true);
    if (is_wp_error(end($ids))) {
        throw new RuntimeException('A12_FIXTURE_POST_FAILED');
    }
    add_post_meta(end($ids), 'a12_field', 'A12_FIELD_PRIVATE_CANARY');
}
add_post_meta($ids[0], 'a12_field', 'A12_SECOND_VALUE_PRIVATE_CANARY');
$terms = [];
foreach (range(1, 23) as $n) {
    $term = wp_insert_term(sprintf('Rubrique fictive %02d', $n), 'a12_rubrique');
    if (is_wp_error($term)) {
        throw new RuntimeException('A12_FIXTURE_TERM_FAILED');
    }
    $terms[] = (int) $term['term_id'];
}
foreach ([$ids[0], $ids[2], $ids[3]] as $id) {
    wp_set_object_terms($id, [$terms[0]], 'a12_rubrique');
}
wp_set_object_terms($ids[0], [$terms[1]], 'a12_rubrique', true);
wp_set_object_terms($ids[1], [$terms[1]], 'a12_rubrique');
$product = new WC_Product_Simple();
$product->set_name('A12_PRODUCT_PRIVATE_CANARY');
$product->set_regular_price('10');
$productId = $product->save();
add_post_meta($ids[0], '_a12_product_id', (string) $productId);
add_post_meta($ids[0], '_a12_product_id', (string) $productId);
add_post_meta($ids[1], '_a12_product_id', (string) $productId);
add_post_meta($ids[2], '_a12_product_id', (string) $ids[0]);
add_post_meta($ids[3], '_a12_product_ids', [$productId]);
add_post_meta($productId, '_a12_article_id', (string) $ids[0]);
$upload = wp_upload_dir();
if ($upload['error']) {
    throw new RuntimeException('A12_FIXTURE_UPLOAD_FAILED');
}
$attachments = [];
$media = [
    ['application/pdf', 'first.pdf', "%PDF-1.4\nA12-FICTIVE-A\n", $ids[0]],
    ['application/pdf', 'second.pdf', "%PDF-1.4\nA12-FICTIVE-ORPHAN\n", 0],
    ['image/png', 'fake.png', 'A12FAKEPNG', $ids[0]],
];
foreach ($media as [$mime, $name, $bytes, $parent]) {
    $path = $upload['path'] . '/' . $name;
    file_put_contents($path, $bytes);
    $id = wp_insert_attachment([
        'post_title' => 'A12_ATTACHMENT_PRIVATE_CANARY', 'post_mime_type' => $mime,
        'post_status' => 'inherit', 'post_parent' => $parent,
    ], $path, $parent, true);
    if (is_wp_error($id)) {
        throw new RuntimeException('A12_FIXTURE_ATTACHMENT_FAILED');
    }
    update_attached_file($id, $path);
    $attachments[] = [
        'mime' => get_post_mime_type($id), 'bytes' => filesize(get_attached_file($id, true)),
        'orphan' => get_post($id)->post_parent === 0,
    ];
}
$states = [];
$articles = get_posts([
    'post_type' => 'a12_article', 'post_status' => ['publish', 'draft', 'private', 'trash'], 'numberposts' => -1,
]);
foreach ($articles as $post) {
    $states[$post->post_status] = ($states[$post->post_status] ?? 0) + 1;
}
ksort($states);
$top = [];
foreach ($terms as $termId) {
    $top[] = [
        'name' => get_term($termId)->name, 'content_count' => count(get_objects_in_term($termId, 'a12_rubrique')),
    ];
}
usort(
    $top,
    static fn(array $a, array $b): int => $b['content_count'] <=> $a['content_count'] ?: strcmp($a['name'], $b['name'])
);
$allAttachments = get_posts(['post_type' => 'attachment', 'post_status' => 'inherit', 'numberposts' => -1]);
$allOrphans = count(array_filter(
    $allAttachments,
    static fn($post): bool => (int) $post->post_parent === 0 || get_post((int) $post->post_parent) === null
));
$oracle = [
    'all_attachment_count' => count($allAttachments), 'all_orphan_count' => $allOrphans,
    'wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION,
    'runtime_registered' => [
        'a12_article' => post_type_exists('a12_article'), 'a12_empty' => post_type_exists('a12_empty'),
        'a12_rubrique' => taxonomy_exists('a12_rubrique'), 'a12_theme' => post_type_exists('a12_theme'),
        'a12_dynamic' => post_type_exists('a12_dynamic'),
    ],
    'runtime_post_types' => array_values(get_post_types()), 'runtime_taxonomies' => array_values(get_taxonomies()),
    'states' => $states, 'top_terms' => array_slice($top, 0, 20), 'term_count' => count($terms),
    'metadata_content_count' => count($ids), 'attachments' => $attachments,
    'hpos' => \Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),
];
echo 'A12_JSON=' . json_encode($oracle, JSON_THROW_ON_ERROR) . "\n";
