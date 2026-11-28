<?php
// Sonde C33: mutations en mémoire de requête uniquement, retirée après recette.
if (defined('WP_CLI') && WP_CLI) { return; }
add_action('init', static function ():void {
    if(wp_get_environment_type()!=='local' || get_option('imagine_demo_site')!=='imagine-test-demo'){return;}
    add_filter('pre_http_request', static fn()=>new WP_Error('c33_offline','FICTIF'),PHP_INT_MAX);
    add_filter('pre_wp_mail','__return_false',PHP_INT_MAX);
    $class=\Imagine\Site\ComptesPublics::class;
    switch($_GET['c33_mutate']??''){
        case 'author':remove_action('template_redirect',[$class,'auteur'],0);break;
        case 'rest':remove_filter('rest_pre_dispatch',[$class,'rest'],100);break;
        case 'sitemap':remove_filter('wp_sitemaps_add_provider',[$class,'sitemap'],100);break;
        case 'feed':remove_filter('the_author',[$class,'auteurFlux'],100);remove_filter('get_the_author_user_url',[$class,'adresseFlux'],100);break;
        case 'oembed':remove_filter('oembed_response_data',[$class,'oembed'],100);break;
    }
},0);
