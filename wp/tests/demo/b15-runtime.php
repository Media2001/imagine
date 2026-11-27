<?php

declare(strict_types=1);

use Imagine\Site\PiedPage;

if (!class_exists(PiedPage::class)) {
    throw new RuntimeException('B15 pied de page absent');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$menu = get_option('imagine_b09_menu');
$idsBefore = array_map(static fn ($p): int => $p->ID, wp_get_nav_menu_items($menu['menu']));
$builds = 0;
$countBuild = static function (string $html) use (&$builds): string { $builds++; return $html; };
add_filter('post_thumbnail_html', $countBuild);
PiedPage::invalider();
$initial = PiedPage::numero();
$check('numero_cache_construit', $initial !== '' && get_transient(PiedPage::CACHE) === $initial && $builds === 1);
$check('numero_cache_reutilise', PiedPage::numero() === $initial && $builds === 1);
PiedPage::invalider();
$check('numero_cache_reconstruit_apres_invalidation', PiedPage::numero() === $initial && $builds === 2);
remove_filter('post_thumbnail_html', $countBuild);
$issue = Imagine\Site\Accueil::numero();
$check('numero_meme_regle_accueil', str_contains($initial, esc_url(get_permalink($issue))) && str_contains($initial, esc_html(get_the_title($issue))));
ob_start();
PiedPage::rendre();
$anon = ob_get_clean();
preg_match_all('/data-b15-zone="([^"]+)"/', $anon, $matches);
$check('cinq_zones_ordre', $matches[1] === ['abonnement', 'newsletter', 'numero', 'point-vente', 'mentions']);
$check('abonnement_lien_commun', str_contains($anon, esc_url(Imagine\Site\Navigation::abonnementUrl())));
$check('newsletter_et_vente_liens', str_contains($anon, '/nos-newsletters/') && str_contains($anon, '/points-de-vente/'));
$check('pas_saisie_ni_script', !preg_match('/<(input|form|script|iframe)\b/i', $anon));
wp_set_current_user((int)get_option('imagine_c09_fixture')['users']['A-PAPIER']);
ob_start();
PiedPage::rendre();
$reader = ob_get_clean();
// WordPress déduplique les IDs du menu quand il est rendu deux fois dans la même
// requête. La preuve HTTP compare, elle, le footer entier octet pour octet.
$withoutRepeatedIds = static fn (string $html): string => preg_replace('/ id="(?:menu-imagine-b09-footer(?:-[0-9]+)?|menu-item-[0-9]+)"/', '', $html);
$check('contenu_identique_hors_ids_natifs_repetes', $withoutRepeatedIds($reader) === $withoutRepeatedIds($anon));
$check('menu_natif_b09_identifiants_inchanges', $idsBefore === array_map(static fn ($p): int => $p->ID, wp_get_nav_menu_items($menu['menu']))
    && count($menu['items']) === 5 && array_diff(array_values($menu['items']), $idsBefore) === []);
$new = wp_insert_post(wp_slash([
    'post_type' => 'imagine_numero', 'post_status' => 'publish',
    'post_title' => 'FICTIF B15 — numéro temporaire plus récent', 'post_content' => '', 'post_excerpt' => 'FICTIF',
    'meta_input' => ['imagine_sortie' => '2099-12-31', '_thumbnail_id' => get_post_thumbnail_id($issue)],
]), true);
$check('publication_numero_natif_relu', !is_wp_error($new) && get_post($new)->post_status === 'publish');
$check('publication_invalide_cache', get_transient(PiedPage::CACHE) === false);
$changed = PiedPage::numero();
$check('publication_change_numero', $changed !== $initial && str_contains($changed, esc_html(get_the_title($new))));
wp_update_post(['ID' => $new, 'post_status' => 'draft']);
$check('depublication_native_relue', get_post($new)->post_status === 'draft');
$check('depublication_invalide_cache', get_transient(PiedPage::CACHE) === false);
$check('depublication_retour_exact_numero', PiedPage::numero() === $initial);
wp_set_current_user(0);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
