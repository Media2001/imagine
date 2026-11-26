<?php

declare(strict_types=1);

use Imagine\Site\Personnalisation as P;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new RuntimeException('Démo seule.'); }
if (!class_exists(P::class) && is_file(WP_PLUGIN_DIR . '/imagine-site/Personnalisation.php')) {
    require_once WP_PLUGIN_DIR . '/imagine-site/PersonnalisationRegles.php';
    require_once WP_PLUGIN_DIR . '/imagine-site/Personnalisation.php';
    P::register();
}
if (!class_exists(P::class)) {
    echo wp_json_encode(['total'=>1,'failures'=>['formulaire_natif_absent']]); WP_CLI::halt(1);
}
if (!class_exists(Imagine\Site\PersonnalisationReglages::class) && is_file(WP_PLUGIN_DIR . '/imagine-site/PersonnalisationReglages.php')) {
    require_once WP_PLUGIN_DIR . '/imagine-site/PersonnalisationReglages.php';
    Imagine\Site\PersonnalisationReglages::register();
}
$checks = [];
$mutation = $GLOBALS['imagine_c24_mutation'] ?? '';
global $wpdb;
$original = get_current_user_id();
$fixture = get_option('imagine_c09_fixture')['users'];
$id = (int)$fixture['A-PAPIER']; $other = (int)$fixture['A-SEPA4']; $sans = (int)$fixture['A-SANSMAIL'];
$mail = $http = 0;
$fm = static function ($r) use (&$mail) { $mail++; return false; };
$fh = static function ($r) use (&$http) { $http++; return new WP_Error('c24_offline'); };
add_filter('pre_wp_mail',$fm,1); add_filter('pre_http_request',$fh,1);
$wpdb->query('START TRANSACTION');
try {
    $rows = [['id'=>'situation-c24-fictive','titre'=>'Situation fictive C24','multiple'=>false,
        'choix'=>[['id'=>'reveur-c24-fictif','titre'=>'Rêveur fictif'],['id'=>'explorateur-c24-fictif','titre'=>'Explorateur fictif']]]];
    update_option(P::CATALOGUE,$rows,false);
    wp_set_current_user($id);
    delete_user_meta($id,P::META); delete_user_meta($id,P::CONSENTEMENT);
    ob_start(); do_action('woocommerce_account_dashboard'); $html=ob_get_clean();
    $checks['compte_formulaire_facultatif'] = str_contains($html,'id="ma-personnalisation"') && str_contains($html,'name="action" value="imagine_personnalisation"') && !str_contains(substr($html,strpos($html,'id="ma-personnalisation"')),' required');
    $checks['consentement_initial_non_coche'] = str_contains($html,'name="consentement" value="1">');
    P::enregistrer($id,['situation-c24-fictive'=>['reveur-c24-fictif']],null,P::version($id));
    $on=P::reponses($id);
    $checks['reponse_persistante_datee'] = $on['situation-c24-fictive']['choix']===['reveur-c24-fictif'] && strlen($on['situation-c24-fictive']['date_utc'])===20;
    $checks['reponse_ne_consente_pas'] = P::consentement($id)===[];
    P::enregistrer($id,[],true,P::version($id),'consentement');
    $checks['consentement_separe_date_sans_toucher_etiquette'] = P::consentement($id)['accord']===true && strlen(P::consentement($id)['date_utc'])===20 && P::reponses($id)===$on;
    $checks['sans_newsletter_aucun_attribut'] = P::attributsConnecteur($id)===[];
    $newsletter=Imagine\Site\Newsletters::catalogue();
    $checks['newsletter_catalogue_non_vide']=count($newsletter)>0;
    update_user_meta($id,Imagine\Site\Newsletters::META,[$newsletter[0]['id']=>['choix'=>true,'date_utc'=>gmdate('Y-m-d\TH:i:s\Z'),'origine'=>'lecteur']]);
    $checks['conjonction_ouvre_attributs'] = P::attributsConnecteur($id)===$on;
    P::enregistrer($id,[],false,P::version($id),'consentement');
    $checks['retrait_consentement_garde_reponses'] = P::consentement($id)['accord']===false && P::reponses($id)===$on && P::attributsConnecteur($id)===[];
    $beforeOther=P::reponses($other);
    try { P::enregistrer($other,[],null,P::version($other));$checks['tiers_refuse']=false; }
    catch (RuntimeException) { $checks['tiers_refuse']=true; }
    $checks['tiers_inchange']=P::reponses($other)===$beforeOther;
    try { P::enregistrer($id,[],null,'faux');$checks['perime_refuse']=false; }
    catch (RuntimeException) { $checks['perime_refuse']=true; }
    P::enregistrer($id,['situation-c24-fictive'=>['explorateur-c24-fictif']],null,P::version($id));
    $checks['modifier_etiquette']=P::reponses($id)['situation-c24-fictive']['choix']===['explorateur-c24-fictif'];
    P::enregistrer($id,[],null,P::version($id),'effacer');
    $checks['effacer_reponses_seules']=P::reponses($id)===[] && P::consentement($id)['accord']===false;
    wp_set_current_user($sans);
    ob_start(); P::compte();$html=ob_get_clean();
    if ($mutation==='sansmail') { $html.='<input name="consentement">'; }
    $checks['sansmail_rubrique_presente_sans_case']=str_contains($html,'id="ma-personnalisation"') && str_contains($html,'sans email') && !str_contains($html,'name="consentement"');
    try { P::enregistrer($sans,[],true,P::version($sans),'consentement');$checks['sansmail_consentement_refuse']=false; }
    catch (RuntimeException) { $checks['sansmail_consentement_refuse']=true; }
    $checks['reglages_additifs_presents']=class_exists(Imagine\Site\PersonnalisationReglages::class);
    if ($checks['reglages_additifs_presents']) {
        $settings=Imagine\Site\PersonnalisationReglages::class;
        $fifth=['id'=>'cinquieme-c24-fictive','titre'=>'Cinquième fictive','multiple'=>true,'choix'=>[['id'=>'cinquieme-choix-c24','titre'=>'Choix fictif']]];
        $next=[...$rows,$fifth];
        $clean=$settings::nettoyer($next); update_option(P::CATALOGUE,$clean,false);
        $checks['cinquieme_par_donnee']=P::catalogue()===$next;
        ob_start();P::compte();$html=ob_get_clean();
        $checks['cinquieme_dans_formulaire']=str_contains($html,'data-question="cinquieme-c24-fictive"');
        update_option(P::CATALOGUE,$settings::nettoyer($rows),false);
        $checks['identifiant_question_retire_reserve']=$settings::nettoyer($next)===$rows;
        $recycle=$rows;$recycle[0]['choix'][]=$fifth['choix'][0];
        $checks['identifiant_choix_retire_reserve']=$settings::nettoyer($recycle)===$rows;
        $historical=['historique-question-c24'=>['choix'=>['historique-choix-c24'],'date_utc'=>'2026-11-26T17:00:00Z']];
        update_user_meta($id,P::META,$historical);
        delete_user_meta($id,P::META);
        $reuse=[...$rows,['id'=>'historique-question-c24','titre'=>'Recyclage interdit','multiple'=>false,'choix'=>[['id'=>'historique-choix-c24','titre'=>'Interdit']]]];
        $checks['historique_efface_reserve']=$settings::nettoyer($reuse)===$rows;
        $choicesOnly=$rows;$choicesOnly[0]['choix'][]=['id'=>'historique-choix-c24','titre'=>'Autre interdit'];
        $checks['choix_historique_efface_reserve']=$settings::nettoyer($choicesOnly)===$rows;
        $checks['champ_C10_dans_formulaire']=str_contains($settings::champs(),'id="imagine-personnalisation-reglages"');
    }
    if ($mutation==='listener') { add_action(P::ACCROCHE,'__return_null'); }
    $checks['accroche_sans_ecouteur']=P::ACCROCHE==='imagine_personnalisation_attributs_modifies' && has_action(P::ACCROCHE)===false;
    if ($mutation==='mail') { wp_mail('c24-fictif@example.org','FICTIF','FICTIF'); }
    if ($mutation==='http') { wp_remote_get('https://example.org/c24-fictif'); }
} finally {
    $wpdb->query('ROLLBACK');wp_cache_flush();wp_set_current_user($original);
    remove_filter('pre_wp_mail',$fm,1);remove_filter('pre_http_request',$fh,1);
}
$checks['aucun_mail_tente']=$mail===0;$checks['aucun_http_tente']=$http===0;
$failures=array_keys(array_filter($checks,static fn($v)=>$v!==true));
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>$failures,'mutation'=>$mutation]);
if ($failures) { WP_CLI::halt(1); }
