"""Readback final du seul site fictif ; aucune mutation applicative."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import os
from pathlib import Path
import b09
label=sys.argv[1]
identity=b09.b08.c25.b06.guard()
fixture=json.loads((b09.PROOF/'pages-reprise-finale.json').read_text(encoding='utf-8'))
old_fixture=json.loads((b09.PROOF/'pages-reprise.json').read_text(encoding='utf-8'))['fixture']
files=b09.NAMES+['plugins/imagine-site/imagine-site.php']
hashes=b09.b08.c25.b06.hashes(files)
checks={'fichiers_distants_relus':hashes=={n:hashlib.sha256((b09.ROOT/'wp'/n).read_bytes()).hexdigest() for n in files}}
state=b09.wp('''global $wpdb;$v=get_option('imagine_b09_pages');$out=['pages'=>[],'locations'=>get_nav_menu_locations(),'menu'=>get_option('imagine_b09_menu'),'privacy'=>(int)get_option('wp_page_for_privacy_policy'),'privacy_url'=>get_privacy_policy_url()];foreach($v as $k=>$id){$p=get_post($id);$out['pages'][$k]=['id'=>$id,'title'=>$p->post_title,'content'=>$p->post_content,'status'=>$p->post_status,'type'=>$p->post_type,'parent'=>$p->post_parent,'marker'=>get_post_meta($id,'imagine_b09_page',true),'url'=>get_permalink($id)];}$out['contact_posts']=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type=%s",'imagine_contact'));$out['contact_meta']=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE meta_key LIKE %s",$wpdb->esc_like('imagine_contact_').'%'));$out['temporary_files']=[];foreach(['mu-plugins/b09-observer.php','mu-plugins/b09-mutation-prive.php','imagine-demo-build/b09-seed.php','imagine-demo-build/b09-structure.php'] as $n){$out['temporary_files'][$n]=file_exists(WP_CONTENT_DIR.'/'.$n);}echo wp_json_encode($out);''')
checks['cinq_pages_attendues']=set(state['pages'])==set(fixture['readback']) and all({k:r[k] for k in ['id','title','content','url']}==fixture['readback'][key] and r['status']=='publish' and r['type']=='page' and r['parent']==0 and r['marker']==key for key,r in state['pages'].items())
checks['menu_footer_natif']=state['menu']=={'menu':fixture['fixture']['menu'],'items':fixture['fixture']['items']} and state['locations'].get('imagine-footer')==fixture['fixture']['menu']
checks['menu_principal_emplacement_preserve']=state['locations'].get('imagine-principal')==fixture['native']['principal']==22
checks['privacy_native']=state['privacy']==fixture['fixture']['pages']['confidentialite'] and state['privacy_url']==fixture['readback']['confidentialite']['url']
checks['contacts_et_metas_absents']=state['contact_posts']==state['contact_meta']==0
checks['fichiers_essai_absents']=all(v is False for v in state['temporary_files'].values())
old_ids=list(old_fixture['pages'].values())+list(old_fixture['items'].values())
checks['premiere_fixture_retiree']=b09.wp('$v=[];foreach('+b09.php(old_ids)+' as $id){$v[]=get_post($id)===null&&get_post_meta($id)===[];}echo wp_json_encode($v);')==[True]*len(old_ids)
# Comparaison indépendante avec la préimage persistée avant le premier déploiement B09.
dep=json.loads((b09.PROOF/'deploiement.json').read_text(encoding='utf-8'))
p=Path(os.environ['TMPDIR'])/dep['private_snapshot']['file'];raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()==dep['private_snapshot']['sha256']
before=json.loads(raw)['payload']['database'];after=b09.b08.snapshot()
owned=set(fixture['fixture']['pages'].values())|set(fixture['fixture']['items'].values())|set(old_ids)
foreign={k:before[k]==after[k] for k in ['users','usermeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta']}
for key,field in [('posts','ID'),('postmeta','post_id')]:
    foreign[key+'_hors_B09']=[r for r in before[key] if int(r[field]) not in owned]==[r for r in after[key] if int(r[field]) not in owned]
checks['etat_initial_hors_B09_preserve']=bool(foreign) and all(foreign.values())
b09.save(label,{'identity':identity,'checks':checks,'native':state,'remote_hashes':hashes,'foreign_preserved':foreign})
print(json.dumps({'checks':checks,'foreign_preserved':foreign,'privacy':state['privacy'],'pages':{k:r['id'] for k,r in state['pages'].items()}},ensure_ascii=False))
assert all(v is True for v in checks.values())
