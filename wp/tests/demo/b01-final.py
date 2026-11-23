"""B01 final source/readback/evidence gate. Writes PRET only after every check."""
from pathlib import Path
import json,sys,hashlib,base64
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'production/B-01'
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
from construire import wp

def load(name):return json.loads((P/name).read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail=None):checks.append({'name':name,'ok':bool(ok),'detail':detail})
verification=load('verification.json'); runtime=load('runtime.json'); browser=load('browser.json'); installation=load('installation.json')
check('runtime and HTTP all green',verification['failed']==0 and verification['status']=='VERIFIED' and runtime['exit_code']==0)
check('all HTML current bytes match receipt',all(digest(P/p['html_file'])==p['sha256'] and not p['html_errors'] for p in verification['pages']))
check('current browser captures and interactions all green',browser['passed'] and all(x['ok'] for x in browser['records']+browser['checks']))
check('cardinality mutant killed',load('tests/oracle-cardinality-mutant.json')['killed'])
php=load('tests/runtime-final.json'); phpdata=json.loads(php['stdout'])
check('targeted PHP suite clean and temporary objects deleted',php['code']==0 and not php['stderr'] and all(c['ok'] for c in phpdata['checks']) and all(phpdata['temporary_objects_removed']))
isolated=load('tests/isolated-environment.json')
check('all commands in fresh offline environment succeed',all(x['code']==0 for x in isolated['commands']))
provenance=json.loads(isolated['commands'][-1]['stdout'])
check('isolated dependencies and HTML fully verified',not provenance['system_packages'] and len(provenance['packages'])==6 and provenance['html_pages']==verification['http_pages'] and provenance['html_errors']==0)
check('original four and two corrections tests verified',any('Ran 4 tests' in c['stderr'] for c in isolated['commands']) and any('Ran 2 tests' in c['stderr'] for c in isolated['commands']))
before=load('scope-before-local.json')
changed={p for p,h in before.items() if digest(ROOT/p)!=h}
allowed={'wp/plugins/imagine-site/imagine-site.php'}
check('protected local source delta only publication bootstrap',changed==allowed,sorted(changed))
bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
original=base64.b64decode(load('runtime-backup-before-deployment.json')['plugins/imagine-site/imagine-site.php']).decode()
check('bootstrap only requires/registers separate date guard',bootstrap.replace("\nrequire_once __DIR__ . '/NumeroPublication.php';\nNumeroPublication::register();\n",'')==original)
backup=load('runtime-backup-before-deployment.json')
originalfunctions=base64.b64decode(backup['themes/imagine/functions.php']).decode()
currentfunctions=(ROOT/'wp/themes/imagine/functions.php').read_text(encoding='utf-8')
seam=lambda text:text.split('function imagine_article_body(): void',1)[1].split('/** La date éditoriale',1)[0]
check('C08 body seam byte-identical',seam(originalfunctions)==seam(currentfunctions))
current=wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/b00-integre-snapshot.php";')
protected=json.loads(current['stdout'])
# C08 source map is read explicitly alongside B00's cross-lot projection.
c08code=json.loads(wp('eval',"$o=[];foreach([WP_PLUGIN_DIR.'/imagine-site/Paywall.php',...glob(get_template_directory().'/parts/paywall-*.php')] as $f){$o[basename($f)]=hash_file('sha256',$f);}echo wp_json_encode($o);")['stdout'])
protected['c08_code']=c08code
(P/'scope-after-runtime.json').write_text(json.dumps(protected,ensure_ascii=False,indent=2),encoding='utf-8')
check('C08/C09/C10 sources and semantic data exact',protected==load('scope-before-runtime.json'))
sourcefiles={f.relative_to(ROOT).as_posix():digest(f) for f in (ROOT/'wp/themes/imagine').rglob('*') if f.is_file()}
for name in ['imagine-site.php','NumeroPublication.php']:
 f=ROOT/'wp/plugins/imagine-site'/name;sourcefiles[f.relative_to(ROOT).as_posix()]=digest(f)
paths={key:key.removeprefix('wp/') for key in sourcefiles}
code='$paths=json_decode('+json.dumps(json.dumps(paths))+',true);$out=[];foreach($paths as $key=>$rel){$p=WP_CONTENT_DIR."/".$rel;$out[$key]=hash_file("sha256",$p);}echo wp_json_encode(["files"=>$out,"active"=>get_stylesheet(),"wp"=>get_bloginfo("version"),"locale"=>get_locale()]);'
readback=json.loads(wp('eval',code)['stdout'])
check('final exact remote source readback',readback['files']==sourcefiles and readback['active']=='imagine' and readback['wp']=='7.0.9' and readback['locale']=='fr_FR')
check('theme receipt matches final sources',all(sourcefiles['wp/themes/imagine/'+k]==v for k,v in installation['files_sha256'].items()))
check('guard deployment exact',load('plugin-installation.json')['exact'])
check('business traceability notes present',all(x in (P/'notes.md').read_text(encoding='utf-8') for x in ['§3.1','§3.2','§3.3','§3.12','§4.2','C08','J+30/+45']))
integrity={'runtime_exact':protected==load('scope-before-runtime.json'),'protected_local_delta':sorted(changed),'allowed_delta':sorted(allowed),'c08_body_seam_exact':seam(originalfunctions)==seam(currentfunctions),'readback_exact':sourcefiles==readback['files']}
(P/'scope-integrity.json').write_text(json.dumps(integrity,indent=2),encoding='utf-8')
for f in (ROOT/'wp/tests/demo').glob('b01*'):
 if f.is_file(): sourcefiles[f.relative_to(ROOT).as_posix()]=digest(f)
sourcefiles['wp/tests/demo/test_b01_theme.py']=digest(ROOT/'wp/tests/demo/test_b01_theme.py')
evidence={f.relative_to(P).as_posix():digest(f) for f in P.rglob('*') if f.is_file() and 'historique' not in f.parts and f.name not in ['PRET','b01-final-verification.json']}
failures=[x for x in checks if not x['ok']]
report={'checked_at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'VERIFIED_B01' if not failures else 'FAILED','checks':checks,'failed':len(failures),'python_tests':6,'php_checks':len(phpdata['checks']),'http_assertions':verification['assertions'],'runtime_checks_included':len(runtime['checks']),'http_pages':verification['http_pages'],'http_resources':verification['http_resources'],'captures':len(browser['records']),'browser_interactions':len(browser['checks']),'sources_sha256':sourcefiles,'evidence_sha256':evidence,'readback':readback,'limits':['B01 only; C08 search body filtering and Woo guard remain outside this lot','No C09 reseed or J+30/+45 oracle manipulation','No design GO, WCAG certification, payments, email or external WordPress HTTP']}
(P/'b01-final-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['sources_sha256','evidence_sha256','readback','checks']},ensure_ascii=False,indent=2))
if failures:
 print(json.dumps(failures,ensure_ascii=False,indent=2));raise SystemExit(1)
(P/'PRET').write_text('B01 prêt au second tour technique — '+report['checked_at']+'\nPreuve : b01-final-verification.json\nSHA256 : '+digest(P/'b01-final-verification.json')+'\nC08 recherche/paywall hors verdict B01 ; pas de GO visuel.\n',encoding='utf-8')
print('PRET redéposé avec empreinte de la preuve actuelle.')
