<?php

declare(strict_types=1);

use Imagine\Site\Cookies;

if (!class_exists(Cookies::class)) { throw new RuntimeException('C32 inventaire absent'); }
$checks=[];
$check=static function(string $n,bool $ok) use (&$checks):void{$checks[$n]=$ok;if(!$ok){throw new RuntimeException($n);}};
$check('liste_fermee',count(Cookies::liste())===14);
$check('cookie_inconnu_refuse',Cookies::inconnus(['sonde_cookie_interdit'])===['sonde_cookie_interdit']);
$check('aucune_valeur',!str_contains(wp_json_encode(Cookies::liste()),'WP Cookie check'));
$pages=get_option('imagine_b09_pages');$p=get_post($pages['cookies']);
$check('page_native_publiee_vide',$p && $p->post_status==='publish' && $p->post_content==='');
$q=$GLOBALS['wp_query'];$oldpost=$GLOBALS['post']??null;
try{
    $GLOBALS['wp_query']=new WP_Query(['page_id'=>$p->ID]);$GLOBALS['wp_query']->the_post();
    $html=apply_filters('the_content','');
    $check('liste_auto_rendue',str_contains($html,'data-imagine-cookies') && substr_count($html,'<tr>')===15);
    foreach(Cookies::liste() as $row){$check('ligne_'.$row['nom'],str_contains($html,esc_html($row['nom'])));}
    $check('pas_script',!str_contains($html,'<script'));
    $check('texte_tiers_preserve',str_starts_with(apply_filters('the_content','<p>FICTIF</p>'),'<p>FICTIF</p>'));
}finally{$GLOBALS['wp_query']=$q;$GLOBALS['post']=$oldpost;wp_reset_postdata();}
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks)]);
