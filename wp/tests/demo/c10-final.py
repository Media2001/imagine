"""C10 : recette finale, sans relancer B00/C08/C09 ni leurs seeds."""
from pathlib import Path
import hashlib
import io
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10
import construire as b00


def run():
    c10.guard()
    protected = c10.snapshot()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern='test_c10_scope.py')
    local = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    local_proof = {'total':local.testsRun,'failures':len(local.failures),'errors':len(local.errors),
        'skipped':len(local.skipped),'output':stream.getvalue()}
    (c10.PROOF / 'local-tests.json').write_text(json.dumps(local_proof,ensure_ascii=False,indent=2),encoding='utf-8')
    installed = json.loads((c10.PROOF / 'installation.json').read_text(encoding='utf-8'))
    http = json.loads((c10.PROOF / 'http-verification.json').read_text(encoding='utf-8'))
    unit = json.loads((c10.PROOF / 'correction-final-unit.json').read_text(encoding='utf-8'))
    junit = ET.parse(c10.PROOF / 'correction-final-phpunit.xml')
    cases = list(junit.iter('testcase'))
    facade = [case for case in cases if '\\Administration\\ReglagesTest' in case.attrib.get('class', '')]
    hashes = {name:hashlib.sha256((c10.ROOT / 'wp' / name).read_bytes()).hexdigest() for name in c10.FILES}
    hashes['imagine-demo-build/c10-runtime.php'] = hashlib.sha256((c10.ROOT / 'wp/tests/demo/c10-runtime.php').read_bytes()).hexdigest()
    hashes['imagine-demo-build/c10-fixture.php'] = hashlib.sha256((c10.ROOT / 'wp/tests/demo/c10-fixture.php').read_bytes()).hexdigest()
    code = '$names=json_decode(' + json.dumps(json.dumps(list(hashes))) + ',true);$out=[];foreach($names as $n){$p=WP_CONTENT_DIR . "/" . $n;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    deployed = json.loads(b00.wp('eval',code)['stdout'])
    runtime = b00.wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/c10-runtime.php";',check=False)
    runtime_data = json.loads(runtime['stdout'])
    c08 = b00.wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/c08-runtime.php";',check=False)
    c08_data = json.loads(c08['stdout'])
    code = '''$f=get_option('imagine_c09_fixture');$u=get_users(['meta_key'=>'_imagine_c09_fixture','fields'=>'ID']);$out=['fixture'=>$f,'counts'=>['users'=>count($u)]];foreach(['shop_order','shop_subscription'] as $t){$out['counts'][$t]=count(wc_get_orders(['type'=>$t,'status'=>array_keys($t==='shop_subscription'?wcs_get_subscription_statuses():wc_get_order_statuses()),'limit'=>-1,'meta_query'=>[['key'=>'_imagine_c09_fixture','compare'=>'EXISTS']]]));}$out['counts']['memberships']=count(get_posts(['post_type'=>'wc_user_membership','post_status'=>array_keys(get_post_stati()),'posts_per_page'=>-1,'meta_key'=>'_imagine_c09_fixture']));$out['active']=is_plugin_active('imagine-pilotage/imagine-reglages.php');$s=new Imagine\\Pilotage\\Administration\\Reglages();foreach($s->defauts() as $k=>$v){$out['settings'][$k]=get_option($k,$v);}$out['defaults']=$s->defauts();echo wp_json_encode($out);'''
    native = json.loads(b00.wp('eval',code)['stdout'])
    initial_c09 = json.loads((c10.ROOT / 'production/C-09/installation.json').read_text(encoding='utf-8'))['native']['fixture']
    checks = {
        'local_green':local.wasSuccessful() and not local.skipped,
        'composer_test_lint_green':unit['test_exit']==0 and unit['lint_exit']==0,
        'phpunit_facade_discovered':len(facade)==10 and not any(
            list(case) for case in cases),
        'runtime_green':runtime['code']==0 and not runtime_data['failures'],
        'http_green':http['status']=='VERIFIED' and not http['failures'],
        'deployed_sources_exact':hashes==deployed==installed['files_sha256'],
        'php_stderr_empty':not runtime['stderr'] and not c08['stderr'],
        'c08_runtime_green':c08['code']==0 and not c08_data['failures'],
        'c09_counts_27_13_12_14':native['counts']=={'users':27,'shop_order':13,'shop_subscription':12,'memberships':14},
        'c09_fixture_ids_originals':native['fixture']==initial_c09,
        'bootstrap_c10_active':native['active'] is True,
        'defaults_restored_exact':native['settings']==native['defaults'],
        'protected_snapshot_unchanged':protected==c10.snapshot(),
        'a_voir_present':(c10.PROOF / 'A-VOIR.md').is_file(),
    }
    # Contrôle des secrets par comparaison locale ; ne rien restituer des valeurs.
    tokens=[]
    def collect(value,key=''):
        if isinstance(value,dict):
            for k,v in value.items():collect(v,k)
        elif isinstance(value,list):
            for v in value:collect(v,key)
        elif isinstance(value,str) and 'password' in key and len(value)>=12:
            tokens.append(value.encode())
    for path in [Path.home()/'.imagine-demo/identifiants.json',Path.home()/'.imagine-demo/c08-identifiants.json']:
        collect(json.loads(path.read_text(encoding='utf-8')))
    sources = [c10.ROOT/'wp/plugins/imagine-pilotage/imagine-reglages.php',
        *list((c10.ROOT/'wp/plugins/imagine-pilotage/src/Administration').glob('*')),
        *list((c10.ROOT/'wp/outils/demo').glob('c10*')),
        *list((c10.ROOT/'wp/tests/demo').glob('*c10*')),*list(c10.PROOF.rglob('*'))]
    sources = sorted({p for p in sources if p.is_file() and p.suffix!='.pyc'})
    leaked = [p.relative_to(c10.ROOT).as_posix() for p in sources if any(t in p.read_bytes() for t in tokens)]
    checks['no_known_secret_leak'] = not leaked
    record={'scope':b00.SLUG,'at':datetime.now(timezone.utc).isoformat(),'checks':checks,
        'total':len(checks),'failures':[k for k,v in checks.items() if not v],
        'suites':{'phpunit':{'total':len(cases),'facade_tests':len(facade),'receipt':unit},'local':local_proof,'c10_runtime':runtime_data,'c10_http':{'total':http['total'],'failures':http['failures'],'invalid_cases':http['invalid_cases']},'c08_regression':c08_data},
        'c10_assertions':local.testsRun+runtime_data['total']+http['total'],
        'c09_inventory':native['counts'],'deployed_files_sha256':deployed,'file_count':len(deployed),
        'protected_sha256':protected,'secret_scan':{'files_checked':len(sources),'matches':leaked},
        'browser_admin':'Non ouvert : aucun login enregistré dans le coffre ; HTTP réel vérifié par sessions WP éphémères détruites.'}
    record['status']='VERIFIED' if not record['failures'] else 'FAILED'
    (c10.PROOF/'verification-finale.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:record[k] for k in ['scope','status','total','failures','c10_assertions','c09_inventory','file_count','secret_scan']},ensure_ascii=False,indent=2))
    if record['failures']:
        raise SystemExit(1)


if __name__=='__main__':
    run()
