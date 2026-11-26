"""B07 : readback final indépendant, périmètre strict, état métier et B00 préservés."""
import sys
sys.dont_write_bytecode=True
import json,os,hashlib
from pathlib import Path
import b07

def run(label):
 identity=b07.b06.guard();checks={}
 install=json.loads((b07.PROOF/'installation-V2.json').read_text(encoding='utf-8'))
 path=Path(os.environ['TMPDIR'])/install['private_snapshot']['file'];raw=path.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==install['private_snapshot']['sha256']
 old=json.loads(raw)['payload']
 local=(b07.ROOT/'wp'/b07.FILES[3]).read_text(encoding='utf-8')
 checks['bootstrap_ajout_B07_seul']=local.count(b07.BLOCK)==1 and local.replace(b07.BLOCK,'')==old['files'][b07.FILES[3]]
 actual=b07.b06.hashes(b07.FILES)
 checks['sources_distantes_exactes']=actual=={n:hashlib.sha256((b07.ROOT/'wp'/n).read_bytes()).hexdigest() for n in b07.FILES}
 now=b07.snapshot();byid={int(p['ID']):p for p in now['posts']}
 checks['B00_deux_evenements_octets_preserves']=len(old['database']['posts'])==2 and all(byid[int(p['ID'])]==p for p in old['database']['posts'])
 current_meta={int(r['meta_id']):r for r in now['meta']}
 checks['B00_metadonnees_preexistantes_preservees']=all(current_meta.get(int(r['meta_id']))==r for r in old['database']['meta'])
 prior_recipe=[p for p in Path(os.environ['TMPDIR']).glob('b07-private-*/snapshot.json') if json.loads(p.read_text(encoding='utf-8'))['label']=='recette-V2']
 assert len(prior_recipe)==1
 checks['etat_metier_depuis_premiere_recette_exact']=b07.b06.state()==json.loads(prior_recipe[0].read_text(encoding='utf-8'))['payload']['business']
 inventory=b07.wp('''$f=get_option('imagine_b07_fixture');$out=['events'=>[],'inscriptions'=>get_posts(['post_type'=>'imagine_inscription','post_status'=>'any','numberposts'=>-1,'fields'=>'ids']),'observer'=>file_exists(WP_CONTENT_DIR.'/mu-plugins/b07-observer.php'),'observer_option'=>get_option('imagine_b07_observer',null),'plugins'=>get_option('active_plugins')];foreach($f as $key=>$id){$out['events'][$key]=Imagine\\Site\\Agenda::evenement((int)$id);$out['events'][$key]['path']=wp_parse_url(get_permalink($id),PHP_URL_PATH);$out['events'][$key]['fixture_b07']=get_post_meta($id,'imagine_b07_fixture',true);}echo wp_json_encode($out);''')
 checks['quatre_evenements_trois_types']=len(inventory['events'])==len(now['posts'])==4 and {e['type'] for e in inventory['events'].values()}=={'rencontre','sortie','partenaire'}
 checks['deux_nouvelles_fixtures_B07_seules']=all(inventory['events'][k]['fixture_b07']=='1' for k in ['partenaire','passe'])
 checks['aucune_inscription_essai']=inventory['inscriptions']==[]
 checks['observateur_et_option_absents']=not inventory['observer'] and inventory['observer_option'] is None
 checks['aucune_extension_billetterie_active']=all(not any(x in n for x in ['event-tickets','the-events-calendar']) for n in inventory['plugins'])
 d={'identity':identity,'total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],'sources':actual,'readback':inventory}
 b07.save(label,d);print(json.dumps(d,ensure_ascii=False));assert not d['failures']
if __name__=='__main__':run(sys.argv[1])
