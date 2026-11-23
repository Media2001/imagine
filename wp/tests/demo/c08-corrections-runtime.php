<?php
/** Régression de la recherche : aucun verrou natif ne masque le résultat. */
declare(strict_types=1);
namespace Imagine\Demo\C08Corrections;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C08 requise.');
}
$checks = [];
$f = get_option('imagine_c08_fixture');
$article = get_post($f['article']);
$checks['fixture_sans_mot_de_passe_natif'] = $article->post_password === '';
$search = static function (string $term): array {
    $q = new \WP_Query(['post_type' => 'post', 's' => $term, 'posts_per_page' => -1,
        'fields' => 'ids', 'suppress_filters' => false]);
    return array_map('intval', $q->posts);
};
wp_set_current_user(0);
$checks['anonyme_phrase_corps_non_appariee'] = !in_array($article->ID, $search('"Les lucioles violettes de C08 gardent le secret du village fictif."'), true);
$checks['anonyme_titre_public_apparie'] = in_array($article->ID, $search('"Article réservé fictif article"'), true);
$checks['anonyme_extrait_public_apparie'] = in_array($article->ID, $search('"Extrait public C08"'), true);
wp_set_current_user($f['users']['actif']);
$checks['abonne_phrase_corps_appariee'] = in_array($article->ID, $search('"Les lucioles violettes de C08 gardent le secret du village fictif."'), true);
wp_set_current_user(0);
// Écritures natives et REST sur un article jetable, jamais un profil B00/C09.
$temp = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish',
    'post_title' => 'Canari éphémère C08 booléen', 'post_content' => 'CORPS_CANARI_C08_BOOL',
    'post_excerpt' => 'Extrait canari public', 'post_date' => '2026-01-01 12:00:00',
    'meta_input' => ['imagine_numero_id' => get_post_meta($article->ID, 'imagine_numero_id', true)]], true);
if (is_wp_error($temp)) { throw new \RuntimeException('Canari non créé.'); }
try {
    $p = get_post($temp);
    update_post_meta($temp, 'imagine_reserve', false);
    $checks['booleen_natif_false_stocke_vide'] = metadata_exists('post', $temp, 'imagine_reserve')
        && get_post_meta($temp, 'imagine_reserve', true) === '';
    $checks['booleen_natif_false_ouvert'] = \Imagine\Site\Paywall::decision($p)['complet'];
    update_post_meta($temp, 'imagine_reserve', true);
    $checks['booleen_natif_true_ferme'] = !\Imagine\Site\Paywall::decision($p)['complet'];
    delete_post_meta($temp, 'imagine_reserve');
    $checks['booleen_absent_ferme'] = !\Imagine\Site\Paywall::decision($p)['complet'];
    update_post_meta($temp, 'imagine_reserve', 'invalide');
    $checks['booleen_invalide_ferme'] = !\Imagine\Site\Paywall::decision($p)['complet'];
    foreach (['0' => true, '1' => false] as $flag => $expected) {
        update_post_meta($temp, 'imagine_reserve', (string) $flag);
        $checks['chaine_legacy_' . $flag] = \Imagine\Site\Paywall::decision($p)['complet'] === $expected;
    }
    $admin = get_users(['role' => 'administrator', 'number' => 1])[0];
    foreach ([false, true] as $flag) {
        wp_set_current_user($admin->ID);
        $r = new \WP_REST_Request('POST', '/wp/v2/posts/' . $temp);
        $r->set_param('meta', ['imagine_reserve' => $flag]);
        $response = rest_do_request($r);
        $checks['rest_ecriture_' . (int) $flag] = $response->get_status() === 200
            && $response->get_data()['meta']['imagine_reserve'] === $flag;
        wp_set_current_user(0);
        $checks['rest_ecriture_effet_anonyme_' . (int) $flag] = \Imagine\Site\Paywall::decision($p)['complet'] === !$flag;
    }
    wp_set_current_user(0);
    $r = new \WP_REST_Request('POST', '/wp/v2/posts/' . $temp);
    $r->set_param('meta', ['imagine_reserve' => false]);
    $checks['rest_ecriture_anonyme_interdite'] = rest_do_request($r)->get_status() === 401;
} finally {
    wp_delete_post($temp, true);
    wp_set_current_user(0);
}
$checks['canari_article_supprime'] = get_post($temp) === null;
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
