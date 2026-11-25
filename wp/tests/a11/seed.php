<?php

declare(strict_types=1);

// Oracle runs with the real APIs BEFORE the database/file freeze.
if (getenv('A11_VARIANT') === 'seed') {
    foreach (get_posts(['post_type' => ['post', 'page', 'product', 'attachment', 'a11_story'], 'post_status' => 'any', 'numberposts' => -1]) as $old) {
        wp_delete_post($old->ID, true);
    }
    foreach (get_taxonomies(['public' => true]) as $tax) {
        foreach (get_terms(['taxonomy' => $tax, 'hide_empty' => false]) as $term) {
            wp_delete_term($term->term_id, $tax);
        }
    }
    $author = wp_insert_user(['user_login' => 'a11-public-writer', 'user_nicename' => 'a11-writer', 'user_email' => 'a11-writer@example.org', 'display_name' => 'PRIVATE_AUTHOR_NAME_CANARY', 'role' => 'author']);
    wp_insert_user(['user_login' => 'a11-no-posts', 'user_nicename' => 'PRIVATE_NO_POST_AUTHOR_CANARY', 'user_email' => 'a11-no-posts@example.org', 'role' => 'subscriber']);
    $ids = [];
    foreach ([['article', 'post', 'publish', ''], ['unicode', 'post', 'publish', ''], ['parent', 'page', 'publish', ''], ['child', 'page', 'publish', ''], ['story', 'a11_story', 'publish', ''], ['draft', 'post', 'draft', ''], ['private', 'page', 'private', ''], ['protected', 'post', 'publish', 'invented-password'], ['shop', 'page', 'publish', '']] as [$slug, $type, $status, $password]) {
        $ids[$slug] = wp_insert_post(['post_type' => $type, 'post_status' => $status, 'post_name' => $slug === 'unicode' ? 'a11-école' : 'a11-' . $slug, 'post_title' => 'PRIVATE_CONTENT_TITLE_CANARY', 'post_content' => 'PRIVATE_BODY_CANARY', 'post_author' => $author, 'post_password' => $password, 'post_date' => '2025-02-03 12:00:00', 'post_date_gmt' => '2025-02-03 12:00:00', 'post_parent' => $slug === 'child' ? $ids['parent'] : 0]);
    }
    $p = new WC_Product_Simple();
    $p->set_name('PRIVATE_PRODUCT_NAME_CANARY');
    $p->set_slug('a11-product');
    $p->set_status('publish');
    $p->set_regular_price('4.00');
    $ids['product'] = $p->save();
    // These are attachment PAGE URLs, never upload/download URLs.
    foreach (['attachment' => 'article', 'hidden-attachment' => 'protected'] as $slug => $parent) {
        $ids[$slug] = wp_insert_attachment(['post_title' => 'PRIVATE_ATTACHMENT_CANARY', 'post_name' => 'a11-' . $slug, 'post_status' => 'inherit', 'post_mime_type' => 'image/png'], false, $ids[$parent]);
    }
    $ids['unattached'] = wp_insert_attachment(['post_title' => 'PRIVATE_ATTACHMENT_CANARY', 'post_name' => 'a11-unattached', 'post_status' => 'inherit', 'post_mime_type' => 'image/png']);
    foreach (['category', 'post_tag', 'product_cat', 'product_tag', 'a11_topic'] as $tax) {
        $term = wp_insert_term('PRIVATE_TERM_LABEL_CANARY', $tax, ['slug' => 'a11-' . $tax]);
        wp_set_object_terms($ids[in_array($tax, ['product_cat', 'product_tag'], true) ? 'product' : ($tax === 'a11_topic' ? 'story' : 'article')], [$term['term_id']], $tax);
        wp_insert_term('PRIVATE_EMPTY_TERM_LABEL_CANARY', $tax, ['slug' => 'a11-empty-' . $tax]);
    }
    update_option('woocommerce_shop_page_id', $ids['shop']);
    update_option('a11_fixture_ids', $ids);
    update_option('a11_fixture_author', $author);
}
$variant = getenv('A11_VARIANT');
update_option('home', $variant === 'subdir' ? 'https://a02.synthetic.test/magazine' : 'https://a02.synthetic.test');
update_option('permalink_structure', $variant === 'plain' ? '' : '/%category%/%postname%/');
update_option('category_base', 'rubriques');
update_option('tag_base', 'mots');
update_option('woocommerce_permalinks', ['product_base' => '/boutique/%product_cat%', 'category_base' => 'familles', 'tag_base' => 'etiquettes', 'attribute_base' => 'attributs']);
update_option('wp_attachment_pages_enabled', $variant !== 'attachments-disabled' ? '1' : '0');
echo "A11_JSON=" . json_encode(['configured' => true]) . "\n";
