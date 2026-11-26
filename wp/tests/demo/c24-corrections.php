<?php
/** C24 fusion : vraies Settings API, écritures refusées et projection. */
declare(strict_types=1);
use Imagine\Site\Personnalisation as P;
use Imagine\Site\PersonnalisationReglages as S;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new RuntimeException('Démo seule.'); }
$mode=$GLOBALS['imagine_c24_case'] ?? 'journal-question';
$mutation=$GLOBALS['imagine_c24_mutation'] ?? '';
$settings=S::class;$projection=P::class;$replaced=0;
if ($mutation!=='') {
    $file=$mutation==='origine'?'Personnalisation.php':'PersonnalisationReglages.php';
    $raw=file_get_contents(WP_PLUGIN_DIR.'/imagine-site/'.$file);
    $needles=[
        'restauration'=>['if (self::$restoring && self::$preimage !== null && $value === self::$preimage)', 'if (false)'],
        'readback'=>['if (get_option($key, null) !== $old)', 'if (false)'],
        'origine'=>["(\$preference['origine'] ?? null) === 'lecteur'",'true'],
    ];
    [$needle,$replacement]=$needles[$mutation];
    $raw=str_replace($needle,$replacement,$raw,$replaced);
    if ($replaced!==1) { throw new RuntimeException('Mutation divergente.'); }
    $class=$mutation==='origine'?'Personnalisation':'PersonnalisationReglages';
    $raw=str_replace('final class '.$class,'final class '.$class.'CorrectionMutation',$raw);
    eval(substr($raw,5));
    if ($mutation==='origine') { $projection='Imagine\\Site\\PersonnalisationCorrectionMutation'; }
    else {
        $settings='Imagine\\Site\\PersonnalisationReglagesCorrectionMutation';
        remove_all_actions('updated_option',25);remove_all_actions('added_option',25);
        $settings::register();
    }
}
global $wpdb;
$checks=[];$dies=[];$blocked=0;$mail=0;$http=0;
$fm=static function($r)use(&$mail){$mail++;return false;};
$fh=static function($r)use(&$http){$http++;return new WP_Error('c24_offline');};
$die=static function()use(&$dies){return static function($message,$title,$args)use(&$dies){$dies[]=$args['response']??500;throw new RuntimeException('wp_die intercepté');};};
$fail=static function($sql)use(&$blocked,$wpdb){
    if (preg_match('/^INSERT\s+INTO/i',$sql) && str_contains($sql,$wpdb->options)
        && str_contains($sql,'imagine_reglages_journal_')) {$blocked++;return '';}
    return $sql;
};
add_filter('pre_wp_mail',$fm,1);add_filter('pre_http_request',$fh,1);add_filter('wp_die_handler',$die);
$original=get_current_user_id();$wpdb->query('START TRANSACTION');
try {
    $id=(int)get_option('imagine_c09_fixture')['users']['A-PAPIER'];wp_set_current_user($id);
    // Exécuter le vrai callback C24, pas l'initialisation écran Woo sans admin.php.
    global $wp_filter;
    foreach (($wp_filter['admin_init']->callbacks[45] ?? []) as $callback) {
        $fn=$callback['function'];
        if ($fn instanceof Closure) {
            $file=(new ReflectionFunction($fn))->getFileName();
            if (str_contains($file,'PersonnalisationReglages.php') || str_contains($file,': eval()')) {$fn();}
        }
    }
    $old=[['id'=>'fusion-question-c24','titre'=>'Question fictive fusion','multiple'=>true,'choix'=>[
        ['id'=>'fusion-choix-c24-a','titre'=>'Choix fictif A'],['id'=>'fusion-choix-c24-b','titre'=>'Choix fictif B']]]];
    update_option(P::CATALOGUE,$old,false);
    $checks['preimage_reelle_presente']=get_option(P::CATALOGUE)===$old;
    $checks['sanitize_callback_reel']=has_filter('sanitize_option_'.P::CATALOGUE,[$settings,'nettoyer'])!==false;
    if (str_starts_with($mode,'journal-')) {
        $next=$mode==='journal-question'?[]:$old;
        if ($mode==='journal-choix') {array_pop($next[0]['choix']);}
        add_filter('query',$fail,PHP_INT_MAX);
        try {update_option(P::CATALOGUE,$next,false);} catch (RuntimeException $e) {if (!$dies)throw $e;}
        remove_filter('query',$fail,PHP_INT_MAX);
        wp_cache_delete(P::CATALOGUE,'options');wp_cache_delete('alloptions','options');
        $checks['echec_journal_reel_injecte']=$blocked===1;
        $checks['aucun_500_reel']=$dies===[];
        $checks['preimage_restauree_exacte']=get_option(P::CATALOGUE)===$old;
        $stored=maybe_unserialize($wpdb->get_var($wpdb->prepare("SELECT option_value FROM {$wpdb->options} WHERE option_name=%s",P::CATALOGUE)));
        $checks['readback_SQL_preimage_exacte']=$stored===$old;
        $checks['erreur_journal_signalee']=count(array_filter(get_settings_errors(P::CATALOGUE),static fn($e)=>$e['code']==='imagine_personnalisation_journal'))===1;
        // Le bypass interne ne doit jamais ouvrir une nouvelle saisie réservée.
        remove_all_filters('sanitize_option_'.P::CATALOGUE);add_filter('sanitize_option_'.P::CATALOGUE,[$settings,'nettoyer']);
        update_option(P::CATALOGUE,[],false);
        $checks['nouvelle_saisie_reservee_toujours_refusee']=$settings::nettoyer($old)===[];
    } elseif ($mode==='newsletter') {
        $now=gmdate('Y-m-d\TH:i:s\Z');$answers=[$old[0]['id']=>['choix'=>['fusion-choix-c24-a'],'date_utc'=>$now]];
        update_user_meta($id,P::META,$answers);update_user_meta($id,P::CONSENTEMENT,['accord'=>true,'date_utc'=>$now]);
        $nl=Imagine\Site\Newsletters::catalogue();$checks['newsletter_active_presente']=count($nl)>0;
        delete_user_meta($id,Imagine\Site\Newsletters::META);
        update_option('imagine_newsletters_creation','oui',false);
        Imagine\Site\Newsletters::creation($id);
        $created=Imagine\Site\Newsletters::preferences($id);
        $checks['vraie_creation_newsletter_defaut']=count(array_filter($created,static fn($p)=>($p['choix']??null)===true && ($p['origine']??null)==='defaut_creation'))===1;
        $checks['vraie_creation_defaut_projection_fermee']=$projection::attributsConnecteur($id)===[];
        foreach (['defaut_creation','inconnue','', 'lecteur'] as $origin) {
            update_user_meta($id,Imagine\Site\Newsletters::META,[$nl[0]['id']=>['choix'=>true,'date_utc'=>$now,'origine'=>$origin]]);
            $checks['origine_'.($origin?:'absente')]= $projection::attributsConnecteur($id)===($origin==='lecteur'?$answers:[]);
        }
        update_user_meta($id,P::CONSENTEMENT,['accord'=>false,'date_utc'=>$now]);
        $checks['lecteur_sans_consentement_ferme']=$projection::attributsConnecteur($id)===[];
    }
} finally {
    remove_filter('query',$fail,PHP_INT_MAX);$wpdb->query('ROLLBACK');wp_cache_flush();
    wp_set_current_user($original);remove_filter('wp_die_handler',$die);remove_filter('pre_wp_mail',$fm,1);remove_filter('pre_http_request',$fh,1);
}
$checks['aucun_mail']=$mail===0;$checks['aucun_http']=$http===0;
$failures=array_keys(array_filter($checks,static fn($v)=>$v!==true));
echo wp_json_encode(['case'=>$mode,'mutation'=>$mutation,'mutation_replacements'=>$replaced,'total'=>count($checks),'checks'=>$checks,'failures'=>$failures,'dies'=>$dies,'journal_inserts_refused'=>$blocked]);
if ($failures) {WP_CLI::halt(1);}
