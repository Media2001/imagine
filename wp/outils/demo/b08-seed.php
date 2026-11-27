<?php

declare(strict_types=1);

use Imagine\Site\Cooperative;
use Imagine\Site\CooperativeRegles;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible refusée');
}
$pages = [];
$create = static function (string $slug, string $title, int $parent = 0) use (&$pages): int {
    $path = $parent ? 'notre-cooperative/' . $slug : $slug;
    $old = get_page_by_path($path);
    if ($old && (get_post_meta($old->ID, 'imagine_b08_page', true) !== '1' || $old->post_title !== $title
        || $old->post_content !== '' || $old->post_parent !== $parent || $old->post_status !== 'publish')) {
        throw new RuntimeException('Collision page B08');
    }
    $id = $old ? $old->ID : wp_insert_post(['post_type' => 'page', 'post_status' => 'publish',
        'post_name' => $slug, 'post_title' => $title, 'post_content' => '', 'post_excerpt' => '',
        'post_parent' => $parent, 'post_author' => 0, 'meta_input' => ['imagine_b08_page' => '1']], true);
    if (is_wp_error($id) || !$id) {
        throw new RuntimeException('Création refusée');
    }
    $pages[] = $id;
    return $id;
};
$map = ['cooperative' => $create('notre-cooperative', 'Notre coopérative'),
    'soutenir' => $create('soutenir', 'Soutenir'), 'sujet' => $create('proposer-un-sujet', 'Proposer un sujet'), 'enfants' => []];
foreach (CooperativeRegles::PAGES as $slug => $title) {
    $map['enfants'][$slug] = $create($slug, $title, $map['cooperative']);
}
update_option(Cooperative::OPTION, $map, false);
$prior = get_option('imagine_b08_menu', []);
$menu = wp_get_nav_menu_object('imagine-b08-principal');
if ($menu && (int)($prior['menu'] ?? 0) !== $menu->term_id) {
    throw new RuntimeException('Collision menu B08');
}
$rememberMenu = static function (int $id) use (&$prior): void {
    $prior = ['menu' => $id, 'items' => []];
    update_option('imagine_b08_menu', $prior, false);
    if (get_option('imagine_b08_menu') !== $prior) {
        throw new RuntimeException('Témoin menu refusé');
    }
};
// Le hook natif inscrit l'appartenance avant que la création rende la main.
add_action('wp_create_nav_menu', $rememberMenu);
try {
    $menuId = $menu ? $menu->term_id : wp_create_nav_menu('imagine-b08-principal');
} finally {
    remove_action('wp_create_nav_menu', $rememberMenu);
}
if (is_wp_error($menuId)) {
    throw new RuntimeException('Menu refusé');
}
$entries = [
    'kiosque' => ['Nos numéros', get_post_type_archive_link('imagine_numero'), 0],
    'thematiques' => ['Thématiques', home_url('/#imagine-thematiques'), 0],
    'newsletters' => ['Nos newsletters', get_permalink(get_page_by_path('nos-newsletters')), 0],
    'agenda' => ['Nos événements', get_post_type_archive_link('imagine_evenement'), 0],
    'cooperative' => ['Notre coopérative', get_permalink($map['cooperative']), $map['cooperative']],
    'soutenir' => ['Soutenir', get_permalink($map['soutenir']), $map['soutenir']],
    'abonnement' => ["S'abonner", home_url('/#imagine-abonnement'), 0],
    'compte' => ['Connexion', wc_get_page_permalink('myaccount'), 0],
];
$items = [];
$owned = [];
$keys = [...array_keys($entries), ...array_keys($map['enfants'])];
foreach (wp_get_nav_menu_items((int)$menuId, ['post_status' => 'any']) as $item) {
    $key = get_post_meta($item->ID, 'imagine_b08_menu_item', true);
    if (!in_array($key, $keys, true) || isset($owned[$key])
        || (isset($prior['items'][$key]) && (int)$prior['items'][$key] !== $item->ID)) {
        throw new RuntimeException('Item étranger');
    }
    $owned[$key] = $item->ID;
}
foreach ($prior['items'] ?? [] as $key => $id) {
    if (($owned[$key] ?? 0) !== (int)$id) {
        throw new RuntimeException('Item étranger');
    }
}
$put = static function (string $key, array $args) use ($menuId, &$prior, $owned, &$items): int {
    $id = (int)($owned[$key] ?? 0);
    $rememberItem = static function (int $menu, int $item) use ($key, $menuId, &$prior): void {
        if ($menu !== (int)$menuId) {
            throw new RuntimeException('Item étranger');
        }
        update_post_meta($item, 'imagine_b08_menu_item', $key);
        $prior['items'][$key] = $item;
        update_option('imagine_b08_menu', $prior, false);
        if (get_post_meta($item, 'imagine_b08_menu_item', true) !== $key
            || get_option('imagine_b08_menu') !== $prior) {
            throw new RuntimeException('Témoin item refusé');
        }
    };
    // Marquer dès l'insertion ; un item interrompu sera complété au rejeu.
    add_action('wp_add_nav_menu_item', $rememberItem, 10, 2);
    try {
        $id = wp_update_nav_menu_item((int)$menuId, $id, $args + ['menu-item-status' => 'publish']);
    } finally {
        remove_action('wp_add_nav_menu_item', $rememberItem, 10);
    }
    if (is_wp_error($id) || !$id) {
        throw new RuntimeException('Item refusé');
    }
    $items[$key] = $id;
    return $id;
};
$order = 0;
foreach ($entries as $key => [$title, $url, $page]) {
    $put($key, ['menu-item-title' => $title, 'menu-item-type' => $page ? 'post_type' : 'custom',
        'menu-item-object' => $page ? 'page' : 'custom', 'menu-item-object-id' => $page,
        'menu-item-url' => $url, 'menu-item-position' => ++$order, 'menu-item-parent-id' => 0,
        'menu-item-classes' => 'imagine-nav-' . $key]);
}
foreach ($map['enfants'] as $slug => $id) {
    $put($slug, ['menu-item-title' => CooperativeRegles::PAGES[$slug], 'menu-item-type' => 'post_type',
        'menu-item-object' => 'page', 'menu-item-object-id' => $id, 'menu-item-url' => get_permalink($id),
        'menu-item-position' => ++$order, 'menu-item-parent-id' => $items['cooperative']]);
}
$locations = get_nav_menu_locations();
if (!empty($locations['imagine-principal']) && (int)$locations['imagine-principal'] !== (int)$menuId) {
    throw new RuntimeException('Menu principal déjà attribué');
}
$locations['imagine-principal'] = (int)$menuId;
set_theme_mod('nav_menu_locations', $locations);
update_option('imagine_b08_menu', ['menu' => $menuId, 'items' => $items], false);
echo wp_json_encode(['pages' => $map, 'menu' => $menuId, 'items' => $items]);
