<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible refusée');
}
$prior = (int) get_option('imagine_b10_page', 0);
$page = get_page_by_path('points-de-vente');
if ($page && ((int) $page->ID !== $prior || get_post_meta($prior, 'imagine_b10_page', true) !== '1'
    || $page->post_status !== 'publish' || $page->post_type !== 'page')) {
    throw new RuntimeException('Collision page B10');
}
$id = $page ? $page->ID : wp_insert_post(['post_type' => 'page', 'post_status' => 'publish',
    'post_name' => 'points-de-vente', 'post_title' => 'Points de vente',
    'post_content' => '<!-- wp:paragraph --><p>Démonstration : commerces, localités et adresses entièrement fictifs.</p><!-- /wp:paragraph -->',
    'post_excerpt' => '', 'post_author' => 0, 'post_parent' => 0,
    'meta_input' => ['imagine_b10_page' => '1']], true);
if (is_wp_error($id) || !$id) {
    throw new RuntimeException('Page B10 refusée');
}
update_option('imagine_b10_page', (int) $id, false);
$locations = get_nav_menu_locations();
$footer = (int) ($locations['imagine-footer'] ?? 0);
$item = (int) get_option('imagine_b10_menu_item', 0);
if ($footer) {
    $marked = get_posts(['post_type' => 'nav_menu_item', 'post_status' => 'any', 'numberposts' => -1,
        'meta_key' => 'imagine_b10_menu_item', 'meta_value' => '1', 'fields' => 'ids']);
    if (count($marked) > 1 || ($item && $marked !== [$item])) {
        throw new RuntimeException('Collision item B10');
    }
    $item = $marked[0] ?? 0;
    if ($item) {
        $menus = wp_get_object_terms($item, 'nav_menu', ['fields' => 'ids']);
        if ($menus !== [] && $menus !== [$footer]) {
            throw new RuntimeException('Item B10 déplacé');
        }
    }
    if (!$item || wp_get_object_terms($item, 'nav_menu', ['fields' => 'ids']) === []) {
        $remember = static function (int $menu, int $item) use ($footer): void {
            if ($menu !== $footer) {
                throw new RuntimeException('Menu inattendu B10');
            }
            update_post_meta($item, 'imagine_b10_menu_item', '1');
            update_option('imagine_b10_menu_item', $item, false);
        };
        add_action('wp_add_nav_menu_item', $remember, 10, 2);
        try {
            $item = wp_update_nav_menu_item($footer, $item, [
                'menu-item-title' => 'Points de vente', 'menu-item-type' => 'post_type', 'menu-item-object' => 'page',
                'menu-item-object-id' => $id, 'menu-item-status' => 'publish',
                'menu-item-url' => get_permalink($id), 'menu-item-parent-id' => 0,
                'menu-item-position' => count(wp_get_nav_menu_items($footer)) + 1,
            ]);
        } finally {
            remove_action('wp_add_nav_menu_item', $remember, 10);
        }
        if (is_wp_error($item) || !$item) {
            throw new RuntimeException('Item B10 refusé');
        }
    }
    update_option('imagine_b10_menu_item', (int) $item, false);
}
if (get_nav_menu_locations() !== $locations || (int) get_option('imagine_b10_page') !== (int) $id) {
    throw new RuntimeException('Readback B10 refusé');
}
echo wp_json_encode(['page' => (int) $id, 'url' => get_permalink($id), 'footer' => $footer, 'item' => (int) $item]);
