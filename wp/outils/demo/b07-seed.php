<?php
declare(strict_types=1);
use Imagine\Site\Agenda;
if(wp_get_environment_type()!=='local'||get_option('imagine_demo_site')!=='imagine-test-demo'||home_url()!=='http://192.168.129.32:8085'){throw new RuntimeException('Cible refusée');}
$m=get_option('imagine_demo_manifest');$old=get_option('imagine_b07_fixture',[]);
$f=['rencontre'=>(int)$m['demo-events-1'],'sortie'=>(int)$m['demo-events-2']];
foreach(['partenaire'=>['b07-partenaire-fictif','Rencontre partenaire des Nuages — fictive'],'passe'=>['b07-rencontre-passee','Rencontre passée des Horizons — fictive']] as $key=>[$slug,$title]){
 $p=get_page_by_path($slug,OBJECT,'imagine_evenement');
 if($p && (int)get_post_meta($p->ID,'imagine_b07_fixture',true)!==1){throw new RuntimeException('Collision fixture');}
 $id=$p?$p->ID:wp_insert_post(['post_type'=>'imagine_evenement','post_status'=>'publish','post_name'=>$slug,'post_title'=>$title,'post_content'=>'<p>Événement entièrement inventé pour la démonstration Imagine. Aucun événement ni partenaire réel.</p>','meta_input'=>['imagine_b07_fixture'=>1]],true);
 if(is_wp_error($id)){throw new RuntimeException('Création refusée');}$f[$key]=$id;
}
foreach($f as $type=>$id){
 $fields=['imagine_type'=>$type==='passe'?'rencontre':$type,'imagine_heure'=>'18:30','imagine_lieu'=>'Maison fictive des Horizons'];
 if(in_array($type,['partenaire','passe'],true)){$fields['imagine_date']=$type==='passe'?'2026-11-01':'2026-12-15';}
 if($type==='partenaire'){$fields['imagine_url_partenaire']='https://example.org/evenement-fictif';}
 foreach($fields as $k=>$v){update_post_meta($id,$k,$v);}
}
update_option('imagine_b07_fixture',$f,false);
echo wp_json_encode($f);
