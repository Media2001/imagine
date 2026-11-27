<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('B13 cible refusée');
}
$menu = get_option('imagine_b08_menu');
if (!$menu || get_nav_menu_locations()['imagine-principal'] !== $menu['menu']) {
    throw new RuntimeException('B13 menu natif attendu absent');
}
$old = get_option('imagine_b13_fixture');
if ($old) {
    echo wp_json_encode($old);
    return;
}
$page = get_page_by_path('abonnement-en-attente');
if ($page) {
    throw new RuntimeException('B13 collision page');
}
$page = wp_insert_post(wp_slash([
    'post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'abonnement-en-attente',
    'post_title' => 'Abonnement — page d’attente fictive',
    'post_content' => 'Page d’attente de démonstration. Le tunnel d’abonnement n’est pas disponible. Aucun paiement.',
    'meta_input' => ['imagine_b13_page' => '1'],
]), true);
if (is_wp_error($page)) {
    throw new RuntimeException('B13 page refusée');
}
update_post_meta((int)$menu['items']['abonnement'], '_menu_item_url', get_permalink($page));
$manifest = get_option('imagine_demo_manifest');
$issue = (int)$manifest['demo-2026-t4'];
$image = get_post_thumbnail_id($issue);
if (!$image) {
    throw new RuntimeException('B13 couverture fictive absente');
}
$articles = [];
foreach (get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => false]) as $term) {
    $id = wp_insert_post(wp_slash([
        'post_type' => 'post', 'post_status' => 'publish', 'post_name' => 'b13-selection-fictive-' . $term->term_id,
        'post_title' => 'B13 — Illustration fictive : ' . $term->name,
        'post_content' => 'CONTENU_FICTIF_RESERVE_B13_' . $term->term_id,
        'post_excerpt' => 'EXTRAIT_B13_INTERDIT_DANS_MENU_' . $term->term_id,
        'meta_input' => ['imagine_reserve' => '1', 'imagine_numero_id' => $issue, 'imagine_b13_article' => '1'],
    ]), true);
    if (is_wp_error($id)) {
        throw new RuntimeException('B13 article refusé');
    }
    set_post_thumbnail($id, $image);
    wp_set_object_terms($id, [$term->term_id], 'imagine_thematique');
    $articles[] = $id;
}
$fixture = ['page' => $page, 'menu' => $menu['menu'], 'articles' => $articles];
update_option('imagine_b13_fixture', $fixture, false);
if (get_option('imagine_b13_fixture') !== $fixture) {
    throw new RuntimeException('B13 fixture non relue');
}
echo wp_json_encode($fixture);
