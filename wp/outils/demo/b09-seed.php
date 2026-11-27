<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible refusée');
}
$definitions = [
    'faq' => ['faq-service-client', 'FAQ du service client'],
    'cgv' => ['conditions-generales-de-vente', 'Conditions générales de vente'],
    'confidentialite' => ['politique-de-confidentialite', 'Politique de confidentialité'],
    'cookies' => ['gestion-des-cookies', 'Gestion des cookies'],
    'contact' => ['contact', 'Contact'],
];
$faq = '';
foreach (['Accès numérique', 'Abonnement', 'Facturation', 'Livraison'] as $heading) {
    $faq .= '<!-- wp:heading --><h2 class="wp-block-heading">' . esc_html($heading) . '</h2><!-- /wp:heading -->' . "\n";
}
$pages = [];
foreach ($definitions as $key => [$slug, $title]) {
    $old = get_page_by_path($slug);
    if ($old && (get_post_meta($old->ID, 'imagine_b09_page', true) !== $key || $old->post_title !== $title
        || $old->post_status !== 'publish' || $old->post_parent !== 0)) {
        throw new RuntimeException('Collision page B09');
    }
    // Le marqueur est écrit dans l'insertion native ; jamais de réécriture du texte édité au rejeu.
    $id = $old ? $old->ID : wp_insert_post(wp_slash(['post_type' => 'page', 'post_status' => 'publish',
        'post_name' => $slug, 'post_title' => $title, 'post_content' => $key === 'faq' ? $faq : '',
        'post_excerpt' => '', 'post_parent' => 0, 'post_author' => 0,
        'meta_input' => ['imagine_b09_page' => $key]]), true);
    if (is_wp_error($id) || !$id || get_post_meta($id, 'imagine_b09_page', true) !== $key) {
        throw new RuntimeException('Création page B09 refusée');
    }
    $pages[$key] = (int) $id;
}
update_option('imagine_b09_pages', $pages, false);
if (get_option('imagine_b09_pages') !== $pages) {
    throw new RuntimeException('Pages B09 non relues');
}
$policy = (int) get_option('wp_page_for_privacy_policy');
if ($policy && $policy !== $pages['confidentialite']) {
    $oldPolicy = get_post($policy);
    // Seul le brouillon livré par le cœur est remplacé comme désignation, sans toucher son texte.
    if (!$oldPolicy || $oldPolicy->post_status !== 'draft' || $oldPolicy->post_name !== 'privacy-policy'
        || $oldPolicy->post_title !== 'Privacy Policy') {
        throw new RuntimeException('Politique existante B09 refusée');
    }
}
update_option('wp_page_for_privacy_policy', $pages['confidentialite']);
if ((int) get_option('wp_page_for_privacy_policy') !== $pages['confidentialite']
    || get_privacy_policy_url() !== get_permalink($pages['confidentialite'])) {
    throw new RuntimeException('Politique B09 non relue');
}
$prior = get_option('imagine_b09_menu', []);
$menu = wp_get_nav_menu_object('imagine-b09-footer');
if ($menu && (int) ($prior['menu'] ?? 0) !== $menu->term_id) {
    throw new RuntimeException('Collision menu B09');
}
$rememberMenu = static function (int $id) use (&$prior): void {
    $prior = ['menu' => $id, 'items' => []];
    update_option('imagine_b09_menu', $prior, false);
    if (get_option('imagine_b09_menu') !== $prior) {
        throw new RuntimeException('Témoin menu B09 refusé');
    }
};
add_action('wp_create_nav_menu', $rememberMenu);
try {
    $menuId = $menu ? $menu->term_id : wp_create_nav_menu('imagine-b09-footer');
} finally {
    remove_action('wp_create_nav_menu', $rememberMenu);
}
if (is_wp_error($menuId) || !$menuId) {
    throw new RuntimeException('Menu B09 refusé');
}
$owned = [];
foreach (wp_get_nav_menu_items((int) $menuId, ['post_status' => 'any']) as $item) {
    $key = get_post_meta($item->ID, 'imagine_b09_menu_item', true);
    if (!isset($definitions[$key]) || isset($owned[$key])
        || (isset($prior['items'][$key]) && (int) $prior['items'][$key] !== $item->ID)) {
        throw new RuntimeException('Item étranger B09');
    }
    $owned[$key] = $item->ID;
}
foreach ($prior['items'] ?? [] as $key => $id) {
    if (!isset($owned[$key])) {
        $post = get_post((int) $id);
        $menus = wp_get_object_terms((int) $id, 'nav_menu', ['fields' => 'ids']);
        if (!isset($definitions[$key]) || !$post || $post->post_type !== 'nav_menu_item'
            || get_post_meta((int) $id, 'imagine_b09_menu_item', true) !== $key || $menus !== []) {
            throw new RuntimeException('Item étranger B09');
        }
        $owned[$key] = (int) $id;
    }
    if ($owned[$key] !== (int) $id) {
        throw new RuntimeException('Item étranger B09');
    }
}
// Le marqueur précède l'option et le rattachement dans le cœur : rechercher aussi hors des deux.
global $wpdb;
$marked = $wpdb->get_col($wpdb->prepare("SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key=%s ORDER BY post_id", 'imagine_b09_menu_item'));
if ($wpdb->last_error !== '') {
    throw new RuntimeException('Lecture items B09 refusée');
}
foreach ($marked as $id) {
    $id = (int) $id;
    $post = get_post($id);
    $markers = get_post_meta($id, 'imagine_b09_menu_item', false);
    $key = $markers[0] ?? '';
    $menus = wp_get_object_terms($id, 'nav_menu', ['fields' => 'ids']);
    if (!$post || $post->post_type !== 'nav_menu_item' || count($markers) !== 1
        || !is_string($key) || !isset($definitions[$key]) || is_wp_error($menus)
        || array_diff($menus, [(int) $menuId]) !== []
        || (isset($owned[$key]) && $owned[$key] !== $id)
        || (isset($prior['items'][$key]) && (int) $prior['items'][$key] !== $id)) {
        throw new RuntimeException('Item étranger B09');
    }
    $owned[$key] = $id;
}
$items = [];
$order = 0;
foreach ($definitions as $key => [$slug, $title]) {
    $position = ++$order;
    $existing = isset($owned[$key]) ? wp_setup_nav_menu_item(get_post($owned[$key])) : null;
    if ($existing && $existing->post_status === 'publish' && $existing->title === $title
        && $existing->type === 'post_type' && $existing->object === 'page'
        && (int) $existing->object_id === $pages[$key] && $existing->url === get_permalink($pages[$key])
        && (int) $existing->menu_order === $position && (int) $existing->menu_item_parent === 0
        && wp_get_object_terms($existing->ID, 'nav_menu', ['fields' => 'ids']) === [(int) $menuId]) {
        $items[$key] = $existing->ID;
        continue;
    }
    $rememberItem = static function (int $menu, int $item) use ($key, $menuId, &$prior): void {
        if ($menu !== (int) $menuId) {
            throw new RuntimeException('Item étranger B09');
        }
        update_post_meta($item, 'imagine_b09_menu_item', $key);
        $prior['items'][$key] = $item;
        update_option('imagine_b09_menu', $prior, false);
        if (get_post_meta($item, 'imagine_b09_menu_item', true) !== $key
            || get_option('imagine_b09_menu') !== $prior) {
            throw new RuntimeException('Témoin item B09 refusé');
        }
    };
    add_action('wp_add_nav_menu_item', $rememberItem, 10, 2);
    try {
        $id = wp_update_nav_menu_item((int) $menuId, (int) ($owned[$key] ?? 0), [
            'menu-item-title' => $title, 'menu-item-type' => 'post_type', 'menu-item-object' => 'page',
            'menu-item-object-id' => $pages[$key], 'menu-item-url' => get_permalink($pages[$key]),
            'menu-item-status' => 'publish', 'menu-item-position' => $position, 'menu-item-parent-id' => 0,
        ]);
    } finally {
        remove_action('wp_add_nav_menu_item', $rememberItem, 10);
    }
    if (is_wp_error($id) || !$id) {
        throw new RuntimeException('Item B09 refusé');
    }
    $items[$key] = $id;
}
$locations = get_nav_menu_locations();
if (!empty($locations['imagine-footer']) && (int) $locations['imagine-footer'] !== (int) $menuId) {
    throw new RuntimeException('Pied de page déjà attribué B09');
}
$locations['imagine-footer'] = (int) $menuId;
set_theme_mod('nav_menu_locations', $locations);
update_option('imagine_b09_menu', ['menu' => $menuId, 'items' => $items], false);
if (get_nav_menu_locations() !== $locations || get_option('imagine_b09_menu') !== ['menu' => $menuId, 'items' => $items]) {
    throw new RuntimeException('Menu B09 non relu');
}
echo wp_json_encode(['pages' => $pages, 'menu' => $menuId, 'items' => $items]);
