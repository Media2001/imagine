<?php
/** Une tranche réelle : droit Memberships/Subscriptions -> décision C-06. */
declare(strict_types=1);
namespace Imagine\Demo\C08Tests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C08 requise.');
}
$checks = [];
$fixture = get_option('imagine_c08_fixture');
$checks['adaptateur_present'] = class_exists('Imagine\\Site\\Paywall');
if ($checks['adaptateur_present']) {
    $post = get_post($fixture['article']);
    wp_set_current_user(0);
    $anon = \Imagine\Site\Paywall::decision($post);
    $checks['anonyme_extrait_connexion'] = !$anon['complet'] && $anon['bloc'] === 'connexion';
    wp_set_current_user($fixture['users']['actif']);
    $active = \Imagine\Site\Paywall::decision($post);
    $checks['actif_natif_complet'] = $active['complet'] && $active['motif'] === 'abonnement_actif';
    wp_set_current_user($fixture['users']['grace']);
    $grace = \Imagine\Site\Paywall::decision($post);
    $checks['grace_native_bandeau'] = $grace['complet'] && $grace['bloc'] === 'regularisation';
    wp_set_current_user($fixture['users']['sans-droit']);
    $checks['connecte_sans_droit_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    $orphan = new \WP_Post((object) ['ID' => 0, 'post_type' => 'post', 'post_content' => 'Texte fictif sans métadonnées', 'post_excerpt' => '']);
    $checks['article_sans_metadonnees_garde_ferme'] = \Imagine\Site\Paywall::managed($orphan)
        && !\Imagine\Site\Paywall::decision($orphan)['complet'];
    $witness = 'Les lucioles violettes de C08 gardent le secret du village fictif.';
    $original = $post->post_content;
    wp_set_current_user(0);
    $safe = \Imagine\Site\Paywall::sanitizePosts([$post])[0];
    $checks['objet_retourne_expurge'] = !str_contains($safe->post_content, $witness);
    $checks['cache_objet_source_non_mute'] = str_contains(get_post($post->ID)->post_content, $witness)
        && $post->post_content === $original && $post !== $safe;
    $GLOBALS['post'] = $post;
    setup_postdata($post);
    $checks['filtre_contenu_direct'] = !str_contains(apply_filters('the_content', $original), $witness);
    $checks['filtre_flux_direct'] = !str_contains(apply_filters('the_content_feed', $original), $witness);
    $automatic = get_post($fixture['automatique']);
    $checks['extrait_automatique_ne_lit_pas_corps'] = !str_contains(get_the_excerpt($automatic), $witness)
        && !str_contains(get_the_excerpt($automatic), 'La place imaginaire');
    $checks['extrait_vide_repli_neutre'] = \Imagine\Site\Paywall::excerpt($automatic) === 'Cet article est réservé aux abonnés.';
    $checks['ancien_mot_de_passe_pas_un_droit'] = post_password_required($post);
    $response = new \WP_REST_Response(['content' => ['raw' => $original, 'rendered' => $original],
        'excerpt' => ['raw' => $original, 'rendered' => $original], 'password' => 'test-fictif']);
    $safeResponse = \Imagine\Site\Paywall::rest($response, $post)->get_data();
    $checks['rest_brut_et_mot_de_passe_expurges'] = !str_contains(wp_json_encode($safeResponse), $witness)
        && !isset($safeResponse['password']) && !isset($safeResponse['content']['raw']);
    $headers = \Imagine\Site\Paywall::cacheHeaders(['ETag' => 'test', 'Last-Modified' => 'test', 'Cache-Control' => 'public']);
    $checks['cache_valideurs_supprimes'] = !isset($headers['ETag'], $headers['Last-Modified']);
    $checks['cache_directives_privees'] = str_contains($headers['Cache-Control'], 'private') && str_contains($headers['Cache-Control'], 'no-store');
    wp_set_current_user($fixture['users']['actif']);
    $checks['cache_apres_anonyme_complet'] = str_contains(\Imagine\Site\Paywall::sanitizePosts([get_post($post->ID)])[0]->post_content, $witness);
    $checks['abonne_pas_de_mot_de_passe'] = !post_password_required($post);
    $invalidPlans = static fn () => 'configuration-invalide';
    add_filter('pre_option_imagine_acces_plans', $invalidPlans);
    $denied = \Imagine\Site\Paywall::decision($post);
    $checks['configuration_invalide_fermee'] = !$denied['complet'] && $denied['motif'] === 'adaptateur_indisponible';
    remove_filter('pre_option_imagine_acces_plans', $invalidPlans);
    $throwing = static function () { throw new \RuntimeException('Panne de lecture native simulée.'); };
    add_filter('pre_option_imagine_acces_plans', $throwing);
    $checks['exception_adaptateur_fermee'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    $checks['exception_adaptateur_filtre_corps_ferme'] = !str_contains(apply_filters('the_content', $original), $witness);
    remove_filter('pre_option_imagine_acces_plans', $throwing);
    $emptyPlans = static fn () => [];
    add_filter('pre_option_imagine_acces_plans', $emptyPlans);
    $checks['plan_non_designe_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    remove_filter('pre_option_imagine_acces_plans', $emptyPlans);
    $badRelease = static function ($value, $id, $key) use ($post) {
        return $key === 'imagine_sortie' ? ['date-incorrecte'] : $value;
    };
    add_filter('get_post_metadata', $badRelease, 10, 3);
    $checks['date_numero_invalide_fermee'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    remove_filter('get_post_metadata', $badRelease, 10);
    // Injection de lecture uniquement : aucune altération des données ni des abonnements.
    $hold = static function ($status, $subscription) use ($fixture) {
        return $subscription->get_id() === $fixture['subscriptions']['actif'] ? 'on-hold' : $status;
    };
    add_filter('woocommerce_subscription_get_status', $hold, 10, 2);
    $checks['onhold_sans_grace_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    remove_filter('woocommerce_subscription_get_status', $hold, 10);
    wp_set_current_user($fixture['users']['grace']);
    // Révocation de configuration sans mutation persistante.
    $closed = static fn () => [];
    add_filter('pre_option_imagine_acces_plans', $closed);
    $checks['grace_plan_revoque_fermee'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    remove_filter('pre_option_imagine_acces_plans', $closed);
    ob_start();
    get_template_part('parts/paywall', 'regularisation', ['complet' => false]);
    $blockedNotice = ob_get_clean();
    $checks['bloc_suspendu_ne_promet_pas_lecture'] = !str_contains($blockedNotice, 'la lecture reste disponible');
    $checks['xmlrpc_sans_methode_contenu'] = apply_filters('xmlrpc_methods', ['wp.getPost' => 'test', 'metaWeblog.getPost' => 'test']) === [];
    $checks['mail_reste_coupe'] = wp_mail('c08@example.org', 'Fictif', 'Fictif') === false;
    $checks['http_reste_coupe'] = is_wp_error(wp_remote_get('https://example.org'));
    $checks['passerelles_reste_coupees'] = WC()->payment_gateways()->get_available_payment_gateways() === [];
    wp_reset_postdata();
    wp_set_current_user(0);
}
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { \WP_CLI::halt(1); }
