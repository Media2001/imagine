"""C22 : contrat partagé comportemental, reçus historiques et nouveau sceau V2."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c22
ROOT,PROOF=c22.ROOT,c22.PROOF
BLOCK="require_once __DIR__ . '/NewslettersRegles.php';\nrequire_once __DIR__ . '/Newsletters.php';\nrequire_once __DIR__ . '/NewslettersReglages.php';\nNewsletters::register();\nNewslettersReglages::register();\n\n"
OWN=['wp/plugins/imagine-site/'+n for n in ['Newsletters.php','NewslettersRegles.php','NewslettersReglages.php','tests/NewslettersReglesTest.php']]
OWN+=['wp/outils/demo/'+n for n in ['c22.py','c22-unit.py','c22-quality.py','c22-corrections.py']]
OWN+=['wp/tests/demo/'+n for n in ['c22-runtime.php','c22-observer.php','c22-http.py','c22-verifier.py','c22-corrections.php']]
OWN+=['production/C-22/A-VOIR.md','production/C-22/inventaire-confidentialite.md']
FINAL,MANIFEST='correction-final-V2.json','correction-manifest-V2.json'
RECEIPTS=['correction-native-V2.json','correction-http-V2.json','correction-quality-V2.json','installation-correction-reserve-V2.json','correction-t01-V2.log','correction-preparation-V2.log','correction-baseline-V2.json']
RECEIPTS+=['correction-final-'+x+'-V2.json' for x in ['retired','history','utf8','privacy']]
RECEIPTS+=['correction-mutation-'+x+'-V2.json' for x in ['export','erase']]
RECEIPTS+=['correction-http-V2-'+n+'.png' for n in ['nos-newsletters','mes-newsletters','sans-email','reglages-newsletters']]

def load(name):return json.loads((PROOF/name).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check_receipts():
    for label,count in [('correction-native-V2.json',19),('correction-http-V2.json',40)]:
        r=load(label)
        assert r['scope']=='imagine-test-demo' and r['total']==len(r['checks'])==count
        assert not r['failures'] and all(v is True for v in r['checks'].values())
    n=load('correction-native-V2.json');assert n['native_preserved'] and n['exit']==0 and n['stderr']==''
    h=load('correction-http-V2.json');assert h['before']==h['after'] and h['mail_attempts']==0 and h['http_attempts']==h['http_blocked']
    assert all(h['checks'][k] for k in ['C10_champs_meme_formulaire','C10_section_sous_bouton_inchangee','C10_recyclage_refuse_erreur_visible','historique_retire_exact_HTTP','reserves_restaurees_lignes_exactes'])
    for case in ['retired','history','utf8','privacy']:
        n=load('correction-final-'+case+'-V2.json')
        assert n['total']==len(n['checks'])>0 and not n['failures'] and all(v is True for v in n['checks'].values())
        assert n['state_preserved'] and n['own_options_exact'] and n['exit']==0 and n['stderr']==''
        assert n['source_sha256']==sha(ROOT/'wp/tests/demo/c22-corrections.php')
    for case,key in [('export','export_callbacks_preferences_historiques_exactes'),('erase','effacement_callbacks_preferences_absentes')]:
        n=load('correction-mutation-'+case+'-V2.json')
        assert n['exit']==1 and n['failures']==[key] and n['checks'][key] is False
        assert n['state_preserved'] and n['own_options_exact'] and n['stderr']==''
        assert n['source_sha256']==sha(ROOT/'wp/tests/demo/c22-corrections.php')
    assert load('correction-quality-V2.json')['exit']==0
    text=(PROOF/'correction-t01-V2.log').read_text(encoding='utf-8')
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',text,re.M)
    assert len(markers)==1
    r=json.loads(markers[0])
    assert r['tests']>0 and r['assertions']>0 and r['pass'] is True
    assert r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0
    assert 'NewslettersReglesTest' in text and 'testConfirmerUnDefautNInferePasUnConsentementAvantAction' in text
    assert 'T01 CLEANUP : absence verifiee' in text
    assert re.search(r'REJEU : .*PASS',text)
    assert 'PREPARATION T01 : image verifiee' in (PROOF/'correction-preparation-V2.log').read_text(encoding='utf-8')
    for name,expected in load('correction-baseline-V2.json')['historical_receipts_sha256'].items():
        assert sha(PROOF/name)==expected, 'Historical receipt changed: '+name
    return r

def privacy():
    spec=importlib.util.spec_from_file_location('c22_corrections',ROOT/'wp/outils/demo/c22-corrections.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.runtime(None,'privacy')

def shared():
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(BLOCK)==1
    for hook in ['MonCompte::register();','Renouvellement::register();','Confidentialite::register();','Partenaires::register();']:
        assert bootstrap.count(hook)==1

    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    assert readme.count('## C-22 — préférences locales des newsletters')==1
    assert 'imagine_newsletters_preferences_modifiees' in readme
    return {'bootstrap_C22_unique':True,'hooks_predecessors_preserved':True,'C21_export_erase_result':privacy(),'README_C22_unique':True}

def live():
    c22.profils.guard('imagine-test-demo')
    remote=c22.hashes(c22.NAMES)
    assert remote=={n:sha(ROOT/'wp'/n) for n in c22.NAMES}
    assert c22.hashes(['mu-plugins/imagine-c22-observer.php'])['mu-plugins/imagine-c22-observer.php'] is None
    baseline=load('correction-baseline-V2.json')
    # Shared predecessors are verified above by their current runtime contract, not pinned.
    assert c22.wp(baseline['options_query'])==baseline['options']
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
    assert c22.state()==baseline['state']
    return {'source_readback':remote,'C09':native,'action8793':action,'preexisting_state_exact':True,'public_page':data['page'],'catalogue':data['catalogue'],'creation':'non','preferences_count':0,'observer_absent':True}

def run(seal=False):
    result={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','T01':check_receipts(),'shared_contract':shared(),'site':live()}
    if seal:
        assert not (PROOF/MANIFEST).exists() and not (PROOF/FINAL).exists()
        (PROOF/FINAL).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        paths=OWN+['production/C-22/'+n for n in RECEIPTS+[FINAL]]
        (PROOF/MANIFEST).write_text(json.dumps({'scope':'C-22 corrections','exclusive_sha256':{n:sha(ROOT/n) for n in paths},'shared':'native runtime contract, not syntax or whole-file historical hash'},ensure_ascii=False,indent=2),encoding='utf-8')
    manifest=load(MANIFEST)
    for name,expected in manifest['exclusive_sha256'].items():
        assert name in OWN or name.startswith('production/C-22/'),name
        assert sha(ROOT/name)==expected,name
    assert load(FINAL)['site']['preexisting_state_exact']
    print('C22 VERIFIED: T01 '+str(result['T01']['tests'])+'/'+str(result['T01']['assertions'])+'; native 19; HTTP/browser 40; C09 382; action 8793 pending / subscription 101; C21 export/erase behavior; sources and reset exact')

if __name__=='__main__':
    assert sys.argv[1:] in ([],['--seal'])
    run('--seal' in sys.argv)
