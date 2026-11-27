<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible refusée');
}
$seed = WP_CONTENT_DIR . '/imagine-demo-build/b09-seed.php';
$checks = ['seed_disponible' => is_file($seed)];
if (!$checks['seed_disponible']) {
    echo wp_json_encode(['checks' => $checks]);
    return;
}
global $wpdb;
foreach (['posts', 'postmeta', 'terms', 'term_taxonomy', 'term_relationships', 'termmeta', 'options'] as $table) {
    $engine = $wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s', $wpdb->$table));
    if (!$engine || $engine->Engine !== 'InnoDB' || wp_using_ext_object_cache()) {
        throw new RuntimeException('Transaction indisponible');
    }
}
$execute = static function () use ($seed): array {
    ob_start();
    try {
        require $seed;
        return json_decode((string) ob_get_contents(), true, 512, JSON_THROW_ON_ERROR);
    } finally {
        ob_end_clean();
    }
};
$wpdb->query('START TRANSACTION');
try {
    $locations = get_nav_menu_locations();
    $first = $execute();
    $checks['pages_et_menu_idempotents'] = $first === $execute() && count($first['pages']) === 5
        && count($first['items']) === 5 && count(wp_get_nav_menu_items($first['menu'])) === 5;
    $titles = ['faq' => 'FAQ du service client', 'cgv' => 'Conditions générales de vente',
        'confidentialite' => 'Politique de confidentialité', 'cookies' => 'Gestion des cookies', 'contact' => 'Contact'];
    $checks['intitules_publics_exacts'] = true;
    foreach ($titles as $key => $title) {
        $p = get_post($first['pages'][$key]);
        $checks['intitules_publics_exacts'] = $checks['intitules_publics_exacts'] && $p && $p->post_type === 'page'
            && $p->post_status === 'publish' && $p->post_title === $title && $p->post_parent === 0;
    }
    foreach (['cgv', 'confidentialite', 'cookies', 'contact'] as $key) {
        $checks['contenu_vide_' . $key] = get_post($first['pages'][$key])->post_content === '';
    }
    $checks['privacy_native'] = (int) get_option('wp_page_for_privacy_policy') === $first['pages']['confidentialite']
        && get_privacy_policy_url() === get_permalink($first['pages']['confidentialite']);
    $blocks = parse_blocks(get_post($first['pages']['faq'])->post_content);
    $headings = array_values(array_filter($blocks, static fn($b) => $b['blockName'] === 'core/heading'));
    $checks['FAQ_quatre_rubriques_vides_natives'] = count($headings) === 4
        && array_map(static fn($b) => trim(wp_strip_all_tags($b['innerHTML'])), $headings)
            === ['Accès numérique', 'Abonnement', 'Facturation', 'Livraison']
        && !str_contains(get_post($first['pages']['faq'])->post_content, 'wp:details');
    $text = get_post($first['pages']['faq'])->post_content
        . "\n<!-- wp:details --><details class=\"wp-block-details\"><summary>Question fictive C:\\dossier</summary><!-- wp:paragraph --><p>Réponse fictive C:\\réponse</p><!-- /wp:paragraph --></details><!-- /wp:details -->";
    wp_update_post(wp_slash(['ID' => $first['pages']['faq'], 'post_content' => $text]));
    $execute();
    $checks['FAQ_editable_blocs_sans_code_seed_non_destructif'] = get_post($first['pages']['faq'])->post_content === $text
        && count(array_filter(parse_blocks($text), static fn($b) => $b['blockName'] === 'core/details')) === 1;
    $now = get_nav_menu_locations();
    unset($now['imagine-footer']);
    $old = $locations;
    unset($old['imagine-footer']);
    $checks['menu_principal_non_modifie'] = $now === $old;
    $checks['footer_natif_attribue'] = get_nav_menu_locations()['imagine-footer'] === $first['menu'];
    $foreign = wp_update_nav_menu_item($first['menu'], 0, ['menu-item-title' => 'Étranger fictif B09',
        'menu-item-type' => 'custom', 'menu-item-url' => home_url('/'), 'menu-item-status' => 'publish']);
    try {
        $execute();
        $checks['item_etranger_refuse'] = false;
    } catch (RuntimeException $error) {
        $checks['item_etranger_refuse'] = $error->getMessage() === 'Item étranger B09';
    }
    wp_delete_post($foreign, true);
    $ownership = get_option('imagine_b09_menu');
    delete_option('imagine_b09_menu');
    try {
        $execute();
        $checks['menu_etranger_refuse'] = false;
    } catch (RuntimeException $error) {
        $checks['menu_etranger_refuse'] = $error->getMessage() === 'Collision menu B09';
    }
    update_option('imagine_b09_menu', $ownership, false);
    delete_post_meta($first['pages']['cgv'], 'imagine_b09_page');
    try {
        $execute();
        $checks['page_etrangere_refusee'] = false;
    } catch (RuntimeException $error) {
        $checks['page_etrangere_refusee'] = $error->getMessage() === 'Collision page B09';
    }
} finally {
    $wpdb->query('ROLLBACK');
    wp_cache_flush();
}
echo wp_json_encode(['checks' => $checks]);
