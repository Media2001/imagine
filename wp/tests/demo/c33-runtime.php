<?php

declare(strict_types=1);

use Imagine\Site\ComptesPublics;
use Imagine\Site\PageArticle;

if(!class_exists(ComptesPublics::class)){throw new RuntimeException('C33 fermeture absente');}
$checks=[];$check=static function(string $name,bool $ok) use(&$checks):void{$checks[$name]=$ok;if(!$ok){throw new RuntimeException($name);}};
$uid=wp_insert_user(['user_login'=>'fictif-c33-native','user_email'=>'fictif-c33-native@example.org','user_pass'=>wp_generate_password(48),'display_name'=>'NOM_COMPTE_C33_NATIF','role'=>'administrator']);
$post=wp_insert_post(['post_type'=>'post','post_status'=>'publish','post_title'=>'FICTIF C33 natif','post_author'=>$uid,'post_content'=>'Article fictif C33 public.']);
update_post_meta($post,PageArticle::SIGNATURE,'SIGNATURE_C33_NATIVE');
$check('temoin_publie',get_post($post)->post_status==='publish' && (int)get_post($post)->post_author===(int)$uid);
wp_set_current_user(0);
$server=rest_get_server();
foreach(['/wp/v2/users','/wp/v2/users/'.$uid,'/WP/V2/USERS/'.$uid] as $route){$r=$server->dispatch(new WP_REST_Request('GET',$route));$check('rest_refuse_'.count($checks),$r->get_status()===404 && !str_contains(wp_json_encode($r->get_data()),'NOM_COMPTE_C33_NATIF'));}
$check('provider_utilisateurs_retire',apply_filters('wp_sitemaps_add_provider',new WP_Sitemaps_Users(),'users')===false);
$check('provider_contenus_garde',apply_filters('wp_sitemaps_add_provider',new WP_Sitemaps_Posts(),'posts') instanceof WP_Sitemaps_Posts);
$q=$GLOBALS['wp_query'];$originalPost=$GLOBALS['post']??null;
try{
    $GLOBALS['wp_query']=new WP_Query();$GLOBALS['wp_query']->is_feed=true;$GLOBALS['post']=get_post($post);
    update_post_meta($post,PageArticle::SIGNATURE,'Signé & FICTIF ]]>');
    set_query_var('feed','rss2');$check('rss2_cdata_protegee',apply_filters('the_author','NOM_COMPTE_C33_NATIF')==='Signé & FICTIF ]]]]><![CDATA[>');
    set_query_var('feed','atom');$check('atom_xml_echappe',apply_filters('the_author','NOM_COMPTE_C33_NATIF')==='Signé &amp; FICTIF ]]&gt;');
    $check('atom_url_compte_absente',apply_filters('get_the_author_user_url','https://example.org/compte/')==='');
}finally{$GLOBALS['wp_query']=$q;$GLOBALS['post']=$originalPost;}
update_post_meta($post,PageArticle::SIGNATURE,'SIGNATURE_C33_NATIVE');
$data=get_oembed_response_data(get_post($post),600);
$check('oembed_signature',$data['author_name']==='SIGNATURE_C33_NATIVE' && !isset($data['author_url']));
delete_post_meta($post,PageArticle::SIGNATURE);
$data=get_oembed_response_data(get_post($post),600);$check('oembed_repli_site',$data['author_name']===get_bloginfo('name') && !isset($data['author_url']));
wp_set_current_user($uid);
$r=$server->dispatch(new WP_REST_Request('GET','/wp/v2/users'));$check('admin_liste_native',$r->get_status()===200 && !is_wp_error($r->get_data()));
$check('admin_provider_inchange',apply_filters('wp_sitemaps_add_provider',new WP_Sitemaps_Users(),'users') instanceof WP_Sitemaps_Users);
$data=get_oembed_response_data(get_post($post),600);$check('admin_oembed_inchange',$data['author_name']==='NOM_COMPTE_C33_NATIF' && isset($data['author_url']));
wp_set_current_user(0);
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks)]);
