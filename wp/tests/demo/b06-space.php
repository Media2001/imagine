<?php

declare(strict_types=1);

use Imagine\Site\Cooperateurs as C;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new RuntimeException('Démo seule.'); }
$checks = [];
global $wpdb;
$original = get_current_user_id();
$wpdb->query('START TRANSACTION');
try {
    $marker = 'B06_TEMOIN_CONFIDENTIEL_ESPACE_2026';
    $id = wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_title'=>'B06 racine fictive',
        'post_name'=>'b06-test-espace','post_content'=>$marker,'post_excerpt'=>$marker]);
    update_option(C::PAGE, $id, false);
    $child = wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_title'=>'B06 enfant fictif',
        'post_name'=>'b06-test-enfant','post_parent'=>$id,'post_content'=>$marker,'post_excerpt'=>$marker]);
    $public = wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_title'=>'B06 public témoin','post_content'=>'B06_PUBLIC_PRESENT']);
    $checks['fixtures_presentes'] = get_post($id)->post_content === $marker && get_post($child)->post_content === $marker && get_post($public)->post_content === 'B06_PUBLIC_PRESENT';
    $coop = get_user_by('login', 'p-coop');
    $checks['profil_coop_reel'] = $coop instanceof WP_User;
    update_user_meta($coop->ID, C::META, ['cooperateur'=>true,'source'=>'administration','date_utc'=>'2026-11-26T15:00:00Z']);
    wp_set_current_user($coop->ID);
    $GLOBALS['post'] = get_post($child);
    $checks['controle_inverse_contenu'] = str_contains(apply_filters('the_content', get_post($child)->post_content), $marker);
    $r = rest_do_request(new WP_REST_Request('GET','/wp/v2/pages/'.$child));
    $checks['controle_inverse_rest'] = $r->get_status() === 200 && str_contains(wp_json_encode($r->get_data()), $marker);
    $mutation = $GLOBALS['imagine_b06_mutation'] ?? '';
    if ($mutation === 'page') {
        remove_filter('the_content', [C::class,'contenu'], -1000);
        remove_filter('get_the_excerpt', [C::class,'extrait'], -1000);
        remove_filter('the_posts', [C::class,'protegerObjets'], -1000);
    } elseif ($mutation === 'rest') {
        remove_filter('rest_pre_dispatch', [C::class,'rest'], -1000);
        remove_filter('map_meta_cap', [C::class,'capacites'], 20);
        remove_filter('the_content', [C::class,'contenu'], -1000);
        remove_filter('get_the_excerpt', [C::class,'extrait'], -1000);
        remove_filter('the_posts', [C::class,'protegerObjets'], -1000);
    } elseif ($mutation === 'edition') {
        remove_filter('map_meta_cap', [C::class,'capacites'], 20);
    } elseif (in_array($mutation, ['search','feed','collection'], true)) {
        remove_action('pre_get_posts', [C::class,'requete'], -1000);
        remove_filter('the_posts', [C::class,'protegerObjets'], -1000);
    } elseif ($mutation === 'sitemap') {
        remove_filter('wp_sitemaps_posts_query_args', [C::class,'sitemap'], 10);
        remove_action('pre_get_posts', [C::class,'requete'], -1000);
    }
    $editorId = wp_insert_user(['user_login'=>'b06-editeur-fictif','user_email'=>'b06-editeur@example.org','user_pass'=>wp_generate_password(40),'role'=>'editor']);
    if (is_wp_error($editorId)) { throw new RuntimeException('Éditeur fictif absent.'); }
    $editor = get_userdata($editorId);
    $editor->add_cap('manage_options');
    $editor->add_cap('edit_users');
    wp_set_current_user($editorId);
    $checks['capacites_larges_ne_valent_pas_role_admin'] = !C::administration() && !C::autorise();
    $checks['ecran_edition_non_coop_interdit'] = !current_user_can('edit_post', $child) && !current_user_can('read_post', $child);
    ob_start(); C::fiche($coop); $editorForm = ob_get_clean();
    $checks['fiche_attribut_absente_editeur'] = $editorForm === '';
    foreach (['anonyme'=>0,'abonne_non_coop'=>(int)get_user_by('login','a-carte')->ID,'editeur_non_coop'=>$editorId] as $publicName=>$userId) {
        wp_set_current_user($userId);
        $GLOBALS['post'] = get_post($child);
        $content = apply_filters('the_content', get_post($child)->post_content);
        $checks[$publicName.'_page_sans_contenu'] = str_contains($content, 'réservé aux coopérateurs') && !str_contains($content, $marker);
        $r = rest_do_request(new WP_REST_Request('GET','/wp/v2/pages/'.$child));
        $checks[$publicName.'_rest_sans_contenu'] = $r->get_status() === 403 && !str_contains(wp_json_encode($r->get_data()), $marker);
        foreach (['/wp/v2/pages'] as $route) {
            $request = new WP_REST_Request('GET', $route);
            $request->set_param('include', [$id, $child, $public]);
            $request->set_param('per_page', 100);
            $collection = rest_do_request($request);
            $data = $collection->get_data();
            $present = is_array($data) ? array_column($data, 'id') : [];
            $suffix = str_ends_with($route, '/') ? '_slash' : '';
            $checks[$publicName.'_collection_publique_presente'.$suffix] = $collection->get_status() === 200 && in_array($public, $present, true);
            $checks[$publicName.'_collection_exclut_espace'.$suffix] = $collection->get_status() === 200 && in_array($public, $present, true) && !in_array($id, $present, true) && !in_array($child, $present, true);
        }
        $q = new WP_Query(['post_type'=>'page','s'=>'B06','posts_per_page'=>-1]);
        $ids = wp_list_pluck($q->posts,'ID');
        $checks[$publicName.'_recherche_existe'] = in_array($public,$ids,true);
        $checks[$publicName.'_recherche_exclut_espace'] = !in_array($id,$ids,true) && !in_array($child,$ids,true);
        $q = new WP_Query(['post_type'=>'page','feed'=>'rss2','posts_per_page'=>-1]);
        $ids = wp_list_pluck($q->posts,'ID');
        $checks[$publicName.'_flux_existe'] = in_array($public,$ids,true);
        $checks[$publicName.'_flux_exclut_espace'] = !in_array($id,$ids,true) && !in_array($child,$ids,true);
    }
    $args = apply_filters('wp_sitemaps_posts_query_args', ['post_type'=>'page','posts_per_page'=>-1,'fields'=>'ids'], 'page');
    $ids = get_posts($args);
    $provider = new WP_Sitemaps_Posts();
    $urls = array_column($provider->get_url_list(1, 'page'), 'loc');
    $checks['sitemap_fournisseur_natif_public_present'] = in_array(get_permalink($public), $urls, true);
    $checks['sitemap_fournisseur_natif_espace_absent'] = !in_array(get_permalink($id), $urls, true) && !in_array(get_permalink($child), $urls, true);
    $checks['sitemap_public_existe'] = in_array($public,$ids,true);
    $checks['sitemap_exclut_espace'] = !in_array($id,$ids,true) && !in_array($child,$ids,true);
    wp_set_current_user(0);
    delete_user_meta($coop->ID, C::META);
    wp_set_current_user($coop->ID);
    $GLOBALS['post'] = get_post($child);
    $checks['retrait_referme_page'] = !str_contains(apply_filters('the_content', get_post($child)->post_content), $marker);
} finally {
    $wpdb->query('ROLLBACK'); wp_cache_flush(); wp_set_current_user($original);
}
$failures = array_keys(array_filter($checks, static fn ($v)=>$v!==true));
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>$failures]);
if ($failures) { WP_CLI::halt(1); }
