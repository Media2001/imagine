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
$interruption = static function (int $menu, int $id): void {
    static $count = 0;
    if (++$count === 3) {
        throw new RuntimeException('Interruption fictive B08');
    }
};
$seed = WP_CONTENT_DIR . '/imagine-demo-build/b08-seed.php';
$execute = static function () use ($seed): array {
    ob_start();
    try {
        require $seed;
        return json_decode((string)ob_get_contents(), true, 512, JSON_THROW_ON_ERROR);
    } finally {
        ob_end_clean();
    }
};
$wpdb->query('START TRANSACTION');
try {
    $old = wp_get_nav_menu_object('imagine-b08-principal');
    if ($old) {
        wp_delete_nav_menu($old->term_id);
    }
    delete_option('imagine_b08_menu');
    add_action('wp_update_nav_menu_item', $interruption, 99, 2);
    try {
        $execute();
    } catch (RuntimeException $error) {
        $checks['interruption_reelle_troisieme_item'] = $error->getMessage() === 'Interruption fictive B08';
    } finally {
        remove_action('wp_update_nav_menu_item', $interruption, 99);
    }
    $partial = wp_get_nav_menu_object('imagine-b08-principal');
    $checks['menu_partiel_existe'] = $partial && count(wp_get_nav_menu_items($partial->term_id)) === 3;
    try {
        $first = $execute();
        $second = $execute();
        $checks['reprise_sans_doublon'] = $first === $second && count($first['items']) === 15
            && count(wp_get_nav_menu_items($first['menu'])) === 15;
    } catch (RuntimeException $error) {
        $checks['reprise_sans_doublon'] = false;
        $checks['erreur_reprise'] = $error->getMessage();
    }
    $old = wp_get_nav_menu_object('imagine-b08-principal');
    wp_delete_nav_menu($old->term_id);
    delete_option('imagine_b08_menu');
    $early = static function (): void {
        static $count = 0;
        if (++$count === 3) {
            throw new RuntimeException('Interruption précoce B08');
        }
    };
    add_action('wp_add_nav_menu_item', $early, 99);
    try {
        $execute();
    } catch (RuntimeException $error) {
        $checks['interruption_creation_item'] = $error->getMessage() === 'Interruption précoce B08';
    } finally {
        remove_action('wp_add_nav_menu_item', $early, 99);
    }
    try {
        $first = $execute();
        $checks['reprise_item_inacheve'] = $first === $execute() && count(wp_get_nav_menu_items($first['menu'])) === 15;
    } catch (RuntimeException $error) {
        $checks['reprise_item_inacheve'] = false;
    }
} finally {
    $wpdb->query('ROLLBACK');
    wp_cache_flush();
}
echo wp_json_encode(['checks' => $checks]);
