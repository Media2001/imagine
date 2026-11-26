<?php
/** Qualification ciblée : mutants de vraies sources évalués en mémoire, jamais installés. */
declare(strict_types=1);
use Imagine\Site\Personnalisation as P;
use Imagine\Site\PersonnalisationReglages as S;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new RuntimeException('Démo seule.'); }
$mutation=$GLOBALS['imagine_c24_mutation'] ?? '';
if (!in_array($mutation,['','id-question','id-choix','consentement','newsletter','email'],true)) { throw new RuntimeException('Mutation inconnue.'); }
$settings=S::class;$projection=P::class;$sourceDigest=null;$replaced=0;
if (str_starts_with($mutation,'id-')) {
    $raw=file_get_contents(WP_PLUGIN_DIR.'/imagine-site/PersonnalisationReglages.php');$sourceDigest=hash('sha256',$raw);
    $kind=$mutation==='id-question'?'q':'c';
    $needle="get_option(self::cle('$kind', ".($kind==='q'?"\$row['id']":"\$c['id']")."), false)";
    $raw=str_replace($needle,'false',$raw,$replaced);
    $raw=str_replace('final class PersonnalisationReglages','final class PersonnalisationReglagesMutation',$raw);
    if ($replaced!==1) { throw new RuntimeException('Fragment de garde divergent.'); }
    eval(substr($raw,5));$settings='Imagine\\Site\\PersonnalisationReglagesMutation';
} elseif ($mutation!=='') {
    $raw=file_get_contents(WP_PLUGIN_DIR.'/imagine-site/Personnalisation.php');$sourceDigest=hash('sha256',$raw);
    $needle='PersonnalisationRegles::transmissible(self::consentement($id), $newsletter, Newsletters::admissible($id))';
    $args=["self::consentement(\$id)",'$newsletter','Newsletters::admissible($id)'];
    $args[array_search($mutation,['consentement','newsletter','email'],true)]=$mutation==='consentement'?"['accord'=>true,'date_utc'=>gmdate('Y-m-d\\TH:i:s\\Z')]":'true';
    $raw=str_replace($needle,'PersonnalisationRegles::transmissible('.implode(', ',$args).')',$raw,$replaced);
    $raw=str_replace('final class Personnalisation','final class PersonnalisationMutation',$raw);
    if ($replaced!==1) { throw new RuntimeException('Fragment de conjonction divergent.'); }
    eval(substr($raw,5));$projection='Imagine\\Site\\PersonnalisationMutation';
}
global $wpdb;$checks=[];$wpdb->query('START TRANSACTION');
try {
    $fixture=get_option('imagine_c09_fixture')['users'];$id=(int)$fixture['A-PAPIER'];$sans=(int)$fixture['A-SANSMAIL'];
    $q=['id'=>'qualification-c24-v2','titre'=>'Qualification entièrement fictive','multiple'=>false,'choix'=>[['id'=>'qualification-choix-c24-v2','titre'=>'Choix fictif']]];
    update_option(P::CATALOGUE,[$q],false);
    $checks['temoin_catalogue_present']=P::catalogue()===[$q];
    $extra=['id'=>'reserve-question-c24-v2','titre'=>'Réserve fictive','multiple'=>false,'choix'=>[['id'=>'reserve-choix-c24-v2','titre'=>'Réserve fictive']]];
    add_option('imagine_personnalisation_reserve_q_'.$extra['id'],'1','',false);
    add_option('imagine_personnalisation_reserve_c_'.$extra['choix'][0]['id'],'1','',false);
    $reuse=[$q];$reuse[0]['choix'][]=$extra['choix'][0];
    $checks['question_reservee_refusee']=$settings::nettoyer([$q,$extra])===[$q];
    $checks['choix_reserve_refuse']=$settings::nettoyer($reuse)===[$q];
    $now=gmdate('Y-m-d\TH:i:s\Z');$answers=[$q['id']=>['choix'=>[$q['choix'][0]['id']],'date_utc'=>$now]];
    $nl=Imagine\Site\Newsletters::catalogue();$checks['temoin_newsletter_present']=count($nl)>0;
    $preference=[$nl[0]['id']=>['choix'=>true,'date_utc'=>$now,'origine'=>'lecteur']];
    foreach ([$id,$sans] as $uid) {
        update_user_meta($uid,P::META,$answers);update_user_meta($uid,P::CONSENTEMENT,['accord'=>true,'date_utc'=>$now]);
        update_user_meta($uid,Imagine\Site\Newsletters::META,$preference);
    }
    $checks['temoin_conjonction_ouvre']=$projection::attributsConnecteur($id)===$answers;
    update_user_meta($id,P::CONSENTEMENT,['accord'=>false,'date_utc'=>$now]);
    $checks['sans_consentement_ferme']=$projection::attributsConnecteur($id)===[];
    update_user_meta($id,P::CONSENTEMENT,['accord'=>true,'date_utc'=>$now]);delete_user_meta($id,Imagine\Site\Newsletters::META);
    $checks['sans_newsletter_ferme']=$projection::attributsConnecteur($id)===[];
    $checks['sans_email_ferme']=$projection::attributsConnecteur($sans)===[];
} finally {
    $wpdb->query('ROLLBACK');foreach ([$id,$sans] as $uid) { wp_cache_delete($uid,'user_meta'); }
}
$failures=array_keys(array_filter($checks,static fn($v)=>$v!==true));
echo wp_json_encode(['mutation'=>$mutation,'mutation_replacements'=>$replaced,'mutated_source_sha256'=>$sourceDigest,'total'=>count($checks),'checks'=>$checks,'failures'=>$failures]);
if ($failures) { WP_CLI::halt(1); }
