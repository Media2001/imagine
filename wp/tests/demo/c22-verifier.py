"""C22 lecture de réception ; --seal crée les seuls sceaux de ce lot."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c22
ROOT,PROOF=c22.ROOT,c22.PROOF
BLOCK="require_once __DIR__ . '/NewslettersRegles.php';\nrequire_once __DIR__ . '/Newsletters.php';\nrequire_once __DIR__ . '/NewslettersReglages.php';\nNewsletters::register();\nNewslettersReglages::register();\n\n"
OWN=['wp/plugins/imagine-site/'+n for n in ['Newsletters.php','NewslettersRegles.php','NewslettersReglages.php','tests/NewslettersReglesTest.php']]
OWN+=['wp/outils/demo/'+n for n in ['c22.py','c22-unit.py','c22-quality.py']]
OWN+=['wp/tests/demo/'+n for n in ['c22-runtime.php','c22-observer.php','c22-http.py','c22-verifier.py']]
OWN+=['production/C-22/A-VOIR.md','production/C-22/inventaire-confidentialite.md']
RECEIPTS=['native-final-V2.json','http-final-V2.json','quality-final-V2.json','installation-final-V2.json','t01-final-V2.log','preparation.log','sources-officielles.json']
RECEIPTS+=['http-final-V2-'+n+'.png' for n in ['nos-newsletters','mes-newsletters','sans-email','reglages-newsletters']]

def load(name):return json.loads((PROOF/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check_receipts():
    for label,count in [('native-final-V2.json',19),('http-final-V2.json',33)]:
        r=load(label)
        assert r['scope']=='imagine-test-demo' and r['total']==len(r['checks'])==count
        assert not r['failures'] and all(v is True for v in r['checks'].values())
    n=load('native-final-V2.json');assert n['native_preserved'] and n['exit']==0 and n['stderr']==''
    h=load('http-final-V2.json');assert h['before']==h['after'] and h['mail_attempts']==0 and h['http_attempts']==h['http_blocked']
    assert load('quality-final-V2.json')['exit']==0
    text=(PROOF/'t01-final-V2.log').read_text(encoding='utf-8')
    r=json.loads(re.search(r'T01_RESULT (\{[^\r\n]+\})',text)[1])
    assert r=={'tests':1102,'assertions':34454,'failures':0,'errors':0,'skipped':0,'pass':True}
    assert 'NewslettersReglesTest' in text and 'testConfirmerUnDefautNInferePasUnConsentementAvantAction' in text
    assert 'T01 CLEANUP : absence verifiee' in text
    assert 'PREPARATION T01 : image verifiee' in (PROOF/'preparation.log').read_text(encoding='utf-8')
    return r

def shared():
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(BLOCK)==1
    for hook in ['MonCompte::register();','Renouvellement::register();','Confidentialite::register();','Partenaires::register();']:
        assert bootstrap.count(hook)==1
    privacy=(ROOT/'wp/plugins/imagine-site/Confidentialite.php').read_text(encoding='utf-8')
    assert privacy.count("'imagine_newsletters_preferences'")==1
    assert "private const META = ['imagine_sans_email', 'imagine_email_confirme', 'imagine_newsletters_preferences'];" in privacy
    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    assert readme.count('## C-22 — préférences locales des newsletters')==1
    assert 'imagine_newsletters_preferences_modifiees' in readme
    return {'bootstrap_C22_unique':True,'hooks_predecessors_preserved':True,'C21_inventory_extended':True,'README_C22_unique':True}

def live():
    c22.profils.guard('imagine-test-demo')
    remote=c22.hashes(c22.NAMES)
    assert remote=={n:sha(ROOT/'wp'/n) for n in c22.NAMES}
    assert c22.hashes(['mu-plugins/imagine-c22-observer.php'])['mu-plugins/imagine-c22-observer.php'] is None
    data=c22.wp(r'''global $wpdb;$page=get_page_by_path('nos-newsletters');
$rows=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID<>%d",$page->ID),ARRAY_A);
$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$rows);sort($hashes);
echo wp_json_encode(['catalogue'=>Imagine\Site\Newsletters::catalogue(),
'auto'=>get_option(Imagine\Site\Newsletters::CREATION,'non'),'page'=>[$page->post_name,$page->post_content,$page->post_status],
'preferences_count'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE meta_key='imagine_newsletters_preferences'"),
'posts_except_owned_page'=>['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))],
'observers'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_c22_observation_%'")]);''')
    assert len(data['catalogue'])==3 and sum(x['principale'] for x in data['catalogue'])==1
    assert data['catalogue']==load('catalogue-demo.json')['catalogue']
    assert data['auto']=='non' and data['preferences_count']==0 and data['observers']==0
    assert data['page']==['nos-newsletters','[imagine_newsletters]','publish']
    original=load('baseline.json')['state']
    current=c22.state()
    assert data['posts_except_owned_page']==original['native']['native_fingerprints']['posts']
    # The only new content row is the owned public page; all pre-existing rows stay exact.
    current['native']['native_fingerprints']['posts']=data['posts_except_owned_page']
    assert current==original, 'Unexpected drift outside the owned newsletter page'
    action=current['schedule_business']['action8793']
    assert action['status']=='pending' and action['action_id']=='8793' and json.loads(action['args'])=={'subscription_id':101}
    native=c22.wp('require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";')
    assert native['total']==len(native['checks'])==382 and not native['failures'] and all(native['checks'].values())
    return {'source_readback':remote,'C09':native,'action8793':action,'preexisting_state_exact':True,'public_page':data['page'],'catalogue':data['catalogue'],'creation':'non','preferences_count':0,'observer_absent':True}

def run(seal=False):
    result={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','T01':check_receipts(),'shared_contract':shared(),'site':live()}
    if seal:
        assert not (PROOF/'manifest-V2.json').exists() and not (PROOF/'final-V2.json').exists()
        # Initial additive proof only, not a permanent pin of the shared file.
        initial=load('baseline.json')['source_before']
        bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_bytes().replace(BLOCK.encode(),b'',1)
        assert hashlib.sha256(bootstrap).hexdigest()==initial['plugins/imagine-site/imagine-site.php']
        privacy=(ROOT/'wp/plugins/imagine-site/Confidentialite.php').read_bytes().replace(b", 'imagine_newsletters_preferences'",b'',1)
        assert hashlib.sha256(privacy).hexdigest()==initial['plugins/imagine-site/Confidentialite.php']
        result['initial_shared_predecessors_exact']=True
        (PROOF/'final-V2.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        paths=OWN+['production/C-22/'+n for n in RECEIPTS+['final-V2.json']]
        (PROOF/'manifest-V2.json').write_text(json.dumps({'scope':'C-22','exclusive_sha256':{n:sha(ROOT/n) for n in paths},'shared':'contract, not whole-file historical hash'},ensure_ascii=False,indent=2),encoding='utf-8')
    manifest=load('manifest-V2.json')
    for name,expected in manifest['exclusive_sha256'].items():
        assert name in OWN or name.startswith('production/C-22/'),name
        assert sha(ROOT/name)==expected,name
    assert load('final-V2.json')['site']['preexisting_state_exact']
    print('C22 VERIFIED: T01 1102/34454; native 19; HTTP/browser 33; C09 382; action 8793 pending / subscription 101; sources and reset exact')

if __name__=='__main__':
    assert sys.argv[1:] in ([],['--seal'])
    run('--seal' in sys.argv)
