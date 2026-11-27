<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible refusée');
}
global $wpdb;
foreach (['posts', 'postmeta', 'terms', 'term_taxonomy', 'term_relationships', 'termmeta', 'options'] as $table) {
    $engine = $wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s', $wpdb->$table));
    if (!$engine || $engine->Engine !== 'InnoDB' || wp_using_ext_object_cache()) {
        throw new RuntimeException('Transaction indisponible');
    }
}
$checks = [];
foreach (['menu', 'marqueur', 'item', 'reference', 'autre_menu'] as $case) {
    $wpdb->query('START TRANSACTION');
    try {
        $prior = get_option('imagine_b08_menu');
        $id = (int)$prior['items']['kiosque'];
        if ($case === 'menu') {
            delete_option('imagine_b08_menu');
        } elseif ($case === 'marqueur') {
            delete_post_meta($id, 'imagine_b08_menu_item');
        } elseif ($case === 'item') {
            wp_update_nav_menu_item($prior['menu'], 0, ['menu-item-title' => 'Étranger fictif B08',
                'menu-item-type' => 'custom', 'menu-item-url' => home_url('/'), 'menu-item-status' => 'publish']);
        } elseif ($case === 'reference') {
            $prior['items']['kiosque'] = (int)get_option('imagine_b08_pages')['soutenir'];
            update_option('imagine_b08_menu', $prior, false);
        } else {
            $other = wp_create_nav_menu('b08-etranger-fictif');
            wp_set_object_terms($id, [$other], 'nav_menu');
        }
        $testedMenu = (int)$prior['menu'];
        $count = count(wp_get_nav_menu_items($testedMenu));
        ob_start();
        try {
            require WP_CONTENT_DIR . '/imagine-demo-build/b08-seed.php';
            $checks[$case . '_refuse'] = false;
        } catch (RuntimeException $error) {
            $checks[$case . '_refuse'] = $error->getMessage() === ($case === 'menu' ? 'Collision menu B08' : 'Item étranger');
        } finally {
            ob_end_clean();
        }
        $checks[$case . '_sans_creation'] = $count === count(wp_get_nav_menu_items($testedMenu));
    } finally {
        $wpdb->query('ROLLBACK');
        wp_cache_flush();
    }
}
echo wp_json_encode(['checks' => $checks]);
