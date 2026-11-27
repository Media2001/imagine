<?php

declare(strict_types=1);

use Imagine\Site\Navigation;

if (!class_exists(Navigation::class)) {
    throw new RuntimeException('B13 navigation absente');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$b13MenuBefore = get_option('imagine_b08_menu');
$b13IdsBefore = array_map(static fn ($p): int => $p->ID, wp_get_nav_menu_items($b13MenuBefore['menu']));
for ($b13Pass = 1; $b13Pass <= 2; $b13Pass++) {
    ob_start();
    require WP_CONTENT_DIR . '/imagine-demo-build/b13-b08-sequence.php';
    ob_end_clean();
    $check('b08_retablit_ancre_' . $b13Pass, get_post_meta((int)$b13MenuBefore['items']['abonnement'], '_menu_item_url', true) === home_url('/#imagine-abonnement'));
    ob_start();
    require WP_CONTENT_DIR . '/imagine-demo-build/b13-seed-correction.php';
    ob_end_clean();
    $check('b13_repare_destination_' . $b13Pass, get_post_meta((int)$b13MenuBefore['items']['abonnement'], '_menu_item_url', true) === Navigation::abonnementUrl());
    $check('sequence_ids_et_nombre_conserves_' . $b13Pass, array_map(static fn ($p): int => $p->ID, wp_get_nav_menu_items($b13MenuBefore['menu'])) === $b13IdsBefore);
}
$menu = get_option('imagine_b08_menu');
$items = wp_get_nav_menu_items($menu['menu']);
$top = array_values(array_filter($items, static fn ($p): bool => (int)$p->menu_item_parent === 0));
$check('huit_entrees_natives_ordre', array_column($top, 'title') === [
    'Nos numéros', 'Thématiques', 'Nos newsletters', 'Nos événements', 'Notre coopérative', 'Soutenir', "S'abonner", 'Connexion',
]);
$check('ids_menu_b08_conserves', array_column($top, 'ID') === array_values(array_slice($menu['items'], 0, 8, true)));
Navigation::invalider();
$html = Navigation::thematiques();
$check('cache_construit', get_transient(Navigation::CACHE) === $html && $html !== '');
$check('cache_reutilise', Navigation::thematiques() === $html);
$terms = get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => false]);
$check('thematiques_non_vides', count($terms) >= 3);
foreach ($terms as $term) {
    $check('thematique_' . $term->term_id, str_contains($html, esc_html($term->name)));
}
$fixture = get_option('imagine_b13_fixture');
$article = (int)$fixture['articles'][0];
$check('titre_image_lien_selection', str_contains($html, get_the_title($article))
    && str_contains($html, 'data-b13-article="' . $article . '"') && str_contains($html, '<img')
    && str_contains($html, esc_url(get_permalink($article))));
wp_update_post(['ID' => $article, 'post_status' => 'draft']);
$check('depublication_invalide', get_transient(Navigation::CACHE) === false);
$check('depublication_retire_article', !str_contains(Navigation::thematiques(), 'data-b13-article="' . $article . '"'));
wp_update_post(['ID' => $article, 'post_status' => 'publish']);
$check('publication_reintegre_article', str_contains(Navigation::thematiques(), 'data-b13-article="' . $article . '"'));
$empty = wp_insert_term('B13 — Thématique vide fictive', 'imagine_thematique');
$check('creation_terme_invalide', get_transient(Navigation::CACHE) === false);
$check('thematique_vide_conservee', str_contains(Navigation::thematiques(), 'B13 — Thématique vide fictive'));
wp_delete_term((int)$empty['term_id'], 'imagine_thematique');
wp_set_object_terms($article, [], 'imagine_thematique');
$check('affectation_invalide', get_transient(Navigation::CACHE) === false);
$check('affectation_retire_selection', !str_contains(Navigation::thematiques(), 'data-b13-article="' . $article . '"'));
update_option(Navigation::NOMBRE, 1, false);
$check('reglage_invalide', get_transient(Navigation::CACHE) === false);
$small = Navigation::thematiques();
$check('reglage_nombre_applique', substr_count($small, 'data-b13-article=') <= count($terms));
$check('reglage_defaut_et_bornes', Navigation::nombre('bad') === 3 && Navigation::nombre(0) === 1 && Navigation::nombre(99) === 10);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
