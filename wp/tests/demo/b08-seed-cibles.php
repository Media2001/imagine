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
$wpdb->query('START TRANSACTION');
try {
    $newsletter = get_page_by_path('nos-newsletters');
    $account = get_post(wc_get_page_id('myaccount'));
    $checks['cibles_presentes_avant_absence'] = $newsletter && $account
        && get_post_type_object('imagine_numero')->has_archive && get_post_type_object('imagine_evenement')->has_archive;
    wp_delete_post($newsletter->ID, true);
    wp_delete_post($account->ID, true);
    unregister_post_type('imagine_numero');
    unregister_post_type('imagine_evenement');
    ob_start();
    try {
        require WP_CONTENT_DIR . '/imagine-demo-build/b08-seed.php';
        $map = json_decode((string)ob_get_contents(), true, 512, JSON_THROW_ON_ERROR);
    } finally {
        ob_end_clean();
    }
    foreach (['kiosque', 'agenda', 'newsletters', 'compte'] as $key) {
        $checks[$key . '_sans_url_si_cible_absente'] = get_post_meta($map['items'][$key], '_menu_item_url', true) === '';
    }
    $rendered = [];
    foreach (wp_get_nav_menu_items($map['menu']) as $item) {
        $rendered[$item->ID] = $item->url;
    }
    foreach (['cooperative', 'soutenir'] as $key) {
        $checks[$key . '_cible_existante'] = $rendered[$map['items'][$key]] === get_permalink($map['pages'][$key]);
    }
} finally {
    $wpdb->query('ROLLBACK');
    wp_cache_flush();
}
echo wp_json_encode(['checks' => $checks]);
