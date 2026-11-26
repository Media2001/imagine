<?php
declare(strict_types=1);
use Imagine\Site\Agenda;
use Imagine\Site\AgendaConfidentialite;
$email='b07-privacy@example.org';$id=(int)get_option('imagine_b07_fixture')['rencontre'];
$checks=[];$error=null;
if(Agenda::inscriptions($email)!==[]){throw new RuntimeException('Fixture préexistante : refus');}
try {
 $checks['inscription_native']=Agenda::inscrire($id,'Personnage confidentialité B07',$email,false);
 $ids=Agenda::inscriptions($email);$checks['temoin_persistant']=count($ids)===1;
 $normal=AgendaConfidentialite::exporter($email);
 $filtered=Imagine\Site\Confidentialite::filtrerPage($normal,1,$email,1,0,false,'imagine-agenda');
 $checks['filtre_C21_preserve_export_B07']=$filtered===$normal&&count($normal['data'])===1;
 global $wpdb;$old=$wpdb->suppress_errors(true);
 $break=static function(string $sql)use($wpdb):string {
  return str_contains($sql,"m.meta_key='imagine_agenda_email'")?'SELECT imagine_b07_nonexistent_column FROM '.$wpdb->posts.' LIMIT 1':$sql;
 };
 add_filter('query',$break);
 try {
  $ex=AgendaConfidentialite::exporter($email);
  $er=AgendaConfidentialite::effacer($email);
  $checks['export_lecture_erreur_incomplet']=$ex['done']===false;
  $checks['effacement_lecture_erreur_incomplet']=$er['done']===false&&$er['items_retained']===true&&!$er['items_removed'];
 } finally {remove_filter('query',$break);$wpdb->suppress_errors($old);}
 $checks['erreur_preserve_inscription']=Agenda::inscriptions($email)===$ids;
 $er=AgendaConfidentialite::effacer($email);
 $checks['effacement_reel_apres_erreur']=$er['done']&&$er['items_removed']&&!$er['items_retained'];
} catch(Throwable $e){$error=get_class($e);} finally {
 foreach(Agenda::inscriptions($email)??[] as $owned){wp_delete_post($owned,true);}
 $checks['inscription_essai_retiree']=Agenda::inscriptions($email)===[];
}
$fail=array_keys(array_filter($checks,fn($v)=>!$v));
echo wp_json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>$fail,'error'=>$error]);exit($fail||$error?1:0);
