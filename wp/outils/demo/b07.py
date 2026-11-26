"""B07 : garde cible unique, préimages privées durables, commandes rejouables."""
import sys
sys.dont_write_bytecode=True
import os,json,hashlib,tempfile,subprocess
from pathlib import Path
from datetime import datetime,timezone
import b06
ROOT=b06.ROOT
wp=b06.wp
php=b06.b05.php_json
PROOF=ROOT/'production/B-07'
FILES=['plugins/imagine-site/'+n for n in ['AgendaRegles.php','Agenda.php','AgendaConfidentialite.php','imagine-site.php']]+['themes/imagine/'+n for n in ['archive-imagine_evenement.php','single-imagine_evenement.php']]
BLOCK="// B07 — raccord agenda additif.\nrequire_once __DIR__ . '/AgendaRegles.php';\nrequire_once __DIR__ . '/Agenda.php';\nrequire_once __DIR__ . '/AgendaConfidentialite.php';\nAgenda::register();\nAgendaConfidentialite::register();\n\n"
def save(label,data):
 p=PROOF/(label+'.json');assert not p.exists(),p
 p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(dict(scope='imagine-test-demo',at=datetime.now(timezone.utc).isoformat(),**data),ensure_ascii=False,indent=2),encoding='utf-8')
 return data
def private(label,payload):
 folder=Path(tempfile.mkdtemp(prefix='b07-private-',dir=os.environ['TMPDIR']))
 path=folder/'snapshot.json';raw=json.dumps({'scope':'imagine-test-demo','label':label,'payload':payload},ensure_ascii=False).encode()
 with path.open('xb') as s:s.write(raw);s.flush();os.fsync(s.fileno())
 os.chmod(path,0o600);assert path.read_bytes()==raw
 return {'file':folder.name+'/snapshot.json','sha256':hashlib.sha256(raw).hexdigest(),'private':True}
def remove_observer(expected):
 code='import pathlib,hashlib,json; p=pathlib.Path("/app/sites/imagine-test-demo/wp-content/mu-plugins/b07-observer.php"); assert not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()=="'+expected+'"; p.unlink(missing_ok=True); print(json.dumps({"absent":not p.exists()}))'
 p=subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',code],capture_output=True,text=True,encoding='utf-8')
 assert not p.returncode,p.stderr
 return json.loads(p.stdout)['absent']

def snapshot():
 return wp('''global $wpdb; $ids=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type IN ('imagine_evenement','imagine_inscription')");$in=implode(',',array_map('intval',$ids))?:'0';echo wp_json_encode(['posts'=>$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN ($in) ORDER BY ID",ARRAY_A),'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ($in) ORDER BY meta_id",ARRAY_A),'users'=>$wpdb->get_results("SELECT * FROM {$wpdb->users} ORDER BY ID",ARRAY_A),'usermeta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} ORDER BY umeta_id",ARRAY_A),'options'=>$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name LIKE 'imagine_%' OR option_name='cron' ORDER BY option_id",ARRAY_A)]);''')
def deploy(label):
 identity=b06.guard();before=b06.state();old=wp('$out=[];foreach('+php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$out[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($out);')
 local=(ROOT/'wp'/FILES[3]).read_text(encoding='utf-8')
 assert old[FILES[3]] in [local,local.replace(BLOCK,'')],'Bootstrap partagé divergent : arrêt'
 durable=private(label,{'files':old,'database':snapshot(),'business':before})
 # Les nouvelles classes seules avant le raccord partagé ; canari de parsing avant activation.
 for n in FILES[:3]:b06.profils.b00.upload(n,(ROOT/'wp'/n).read_bytes())
 parsed=wp('$out=[];foreach('+php(FILES[:3])+' as $n){token_get_all(file_get_contents(WP_CONTENT_DIR."/".$n),TOKEN_PARSE);$out[$n]=true;}echo wp_json_encode($out);')
 assert all(parsed.values())
 # CAS frais du bootstrap, aucune réécriture d'un autre lot.
 assert wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+FILES[3]+'"));')==old[FILES[3]]
 for n in FILES[3:]:b06.profils.b00.upload(n,(ROOT/'wp'/n).read_bytes())
 actual=b06.hashes(FILES);assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
 assert before==b06.state()
 save(label,{'identity':identity,'sources':actual,'private_snapshot':durable,'canary_parse':parsed,'business_preserved':True})
def seed(label):
 b06.guard();durable=private(label,{'database':snapshot(),'business':b06.state()})
 src=ROOT/'wp/outils/demo/b07-seed.php';target='imagine-demo-build/b07-seed.php'
 b06.profils.b00.upload(target,src.read_bytes());out=wp('require WP_CONTENT_DIR."/'+target+'";')
 back=wp('$out=[];foreach(get_option("imagine_b07_fixture") as $k=>$id){$out[$k]=Imagine\\Site\\Agenda::evenement((int)$id);$out[$k]["path"]=wp_parse_url(get_permalink($id),PHP_URL_PATH);}echo wp_json_encode($out);')
 assert set(back)==set(['sortie','rencontre','partenaire','passe']) and all(e and e['lieu'] for e in back.values())
 save(label,{'fixture':out,'readback':back,'private_snapshot':durable})
def runtime(label):
 b06.guard();src=ROOT/'wp/tests/demo/b07-runtime.php';target='imagine-demo-build/b07-runtime.php'
 b06.profils.b00.upload(target,src.read_bytes());p=b06.profils.b00.wp('eval','require WP_CONTENT_DIR."/'+target+'";',check=False)
 d=json.loads(p['stdout']);d.update(exit=p['code'],stderr=p['stderr']);save(label,d);print(json.dumps(d));assert not p['code'] and not d['failures']
def rules(label):
 cmd=['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/b07-rules.php']
 p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');d=json.loads(p.stdout);d.update(exit=p.returncode,stderr=p.stderr);save(label,d);print(json.dumps(d));assert p.returncode==0
if __name__=='__main__':
 assert sys.argv[1] in ['deploy','seed','runtime','rules']
 globals()[sys.argv[1]](*sys.argv[2:])
