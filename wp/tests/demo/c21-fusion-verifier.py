"""C21 successeur : preuves historiques immuables, contrat C22, lecture native finale."""
from pathlib import Path
import hashlib, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c21
ROOT, PROOF = c21.ROOT, c21.PROOF
REPORT = 'files/rapports/2026-11-26-10h05-V2.md'
OWNED = [
    'wp/plugins/imagine-site/Confidentialite.php','wp/plugins/imagine-site/ConfidentialiteRegles.php',
    'wp/plugins/imagine-site/tests/ConfidentialiteReglesTest.php',
    'wp/outils/demo/c21.py','wp/outils/demo/c21-unit.py','wp/outils/demo/c21-fusion.py',
    'wp/tests/demo/c21-runtime.php','wp/tests/demo/c21-security.php','wp/tests/demo/c21-failures.php',
    'wp/tests/demo/c21-http.py','wp/tests/demo/c21-fusion-native.php','wp/tests/demo/c21-fusion-http.py',
    'wp/tests/demo/c21-verifier.py','wp/tests/demo/c21-fusion-verifier.py',
    'production/C-21/A-VOIR.md','production/C-21/fusion-contrat.md','production/C-21/PRET',REPORT,
]
RECEIPTS = ['fusion-native-final.json','fusion-http-green.json','fusion-http-complet.json',
    'fusion-security-final.json','fusion-failures-final.json','fusion-regressions-final.json',
    'fusion-unit-cible.json','fusion-unit-root.json','fusion-quality.json',
    'fusion-preparer-image.log','fusion-rejouer.log','installation-fusion-psr.json']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name): return json.loads((PROOF/name).read_text(encoding='utf-8'))
def normalized(value):
    value=json.loads(json.dumps(value))
    for key in ('actionscheduler_actions','actionscheduler_logs'): value['native_fingerprints'].pop(key,None)
    return value

def historical():
    old=read('final.json')
    for name,digest in old['receipt_sha256'].items(): assert sha(PROOF/name)==digest, 'Historique modifié : '+name
    for name in ('production/C-21/natif.md','production/C-21/README-CONTRAT.md','files/rapports/2026-11-26-07h32-V2.md'):
        assert sha(ROOT/name)==old['source_sha256'][name], name
    c22path=ROOT/'production/C-22/installation-final-V2.json'
    c22=json.loads(c22path.read_text(encoding='utf-8'))
    assert c22['scope']=='imagine-test-demo' and c22['native_preserved'] is True
    source=(ROOT/'wp/plugins/imagine-site/Confidentialite.php').read_text(encoding='utf-8')
    assert "private const META = [SansEmail::META, 'imagine_email_confirme', Newsletters::META];" in source
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(c21.BLOCK)==1
    lines=iter(bootstrap.splitlines())
    for wanted in old['shared_contracts']['bootstrap_prerequisites']:
        assert any(line==wanted for line in lines), wanted
    assert (ROOT/'wp/plugins/imagine-site/EnvoiNatif.php').read_text(encoding='utf-8').count(old['shared_contracts']['envoi_block'])==1
    assert (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').count(old['shared_contracts']['readme_section'])==1
    return {'C21_historical_seal_sha256':sha(PROOF/'final.json'),
        'C21_Confidentialite_historical_sha256':old['source_sha256']['wp/plugins/imagine-site/Confidentialite.php'],
        'C22_installation_receipt_sha256':sha(c22path),
        'C22_Confidentialite_installed_sha256':c22['source_readback']['plugins/imagine-site/Confidentialite.php'],
        'authorized_delta':'C22 ajoute imagine_newsletters_preferences ; fusion C21 remplace les littéraux par SansEmail::META et Newsletters::META, valeurs identiques',
        'historical_receipts_unchanged':True}

def evidence():
    counts={}
    for name in RECEIPTS[:5]:
        d=read(name); assert d['scope']=='imagine-test-demo'
        assert d['total']==len(d['checks']) and not d['failures'] and all(v is True for v in d['checks'].values()), name
        counts[name]=d['total']
    for name in ('fusion-unit-cible.json','fusion-unit-root.json'):
        d=read(name);assert d['exit']==0 and d['removed'] and not d['stderr'];counts[name]={k:d[k] for k in ('tests','assertions')}
    q=read('fusion-quality.json');assert q['exit']==0 and not q['stderr'] and q['report']['totals']['errors']==0
    reg=read('fusion-regressions-final.json')
    for name,d in reg['native'].items():
        assert d['total']==len(d['checks']) and not d['failures'] and all(d['checks'].values()) and d['all_tables_rollback_exact'];counts[name]=d['total']
    assert reg['C09']['total']==len(reg['C09']['checks'])==382 and not reg['C09']['failures'] and all(reg['C09']['checks'].values());counts['C09']=382
    action=reg['schedule_business']['action8793']
    assert action['action_id']=='8793' and action['status']=='pending' and json.loads(action['args'])=={'subscription_id':101}
    markers=re.findall(r'^T01_RESULT (.+)$',(PROOF/'fusion-rejouer.log').read_text(encoding='utf-8-sig'),re.M)
    assert len(markers)==1;canonical=json.loads(markers[0]);assert canonical['pass'] and canonical['failures']==canonical['errors']==canonical['skipped']==0
    assert 'T01 IMAGE READY' in (PROOF/'fusion-preparer-image.log').read_text(encoding='utf-8-sig')
    return counts,canonical

def live():
    c21.c19.c18.c17.profils.guard('imagine-test-demo')
    names=list(c21.targets())+['imagine-demo-build/c21-'+s+'.php' for s in ('runtime','security','failures','fusion-native')]
    expected={n:sha(p) for n,p in c21.targets().items()}
    expected.update({'imagine-demo-build/c21-'+s+'.php':sha(ROOT/('wp/tests/demo/c21-'+s+'.php')) for s in ('runtime','security','failures','fusion-native')})
    assert c21.hashes(names)==expected, 'Source installée différente'
    assert normalized(c21.c19.c18.state())==normalized(read('fusion-http-complet.json')['native_after']), 'État natif changé'
    assert c21.schedule_business()==read('fusion-regressions-final.json')['schedule_business']
    settings=read('conservation-complete.json')['settings']
    result=c21.wp('$out=[];foreach(json_decode('+json.dumps(json.dumps(list(settings)))+',true) as $k)$out[$k]=get_option($k,null);$meta=(new ReflectionClass(Imagine\\Site\\Confidentialite::class))->getConstant("META");echo wp_json_encode(["settings"=>$out,"meta"=>$meta,"fixture_absent"=>get_option("imagine_c21_fixture",null)===null&&!get_user_by("login","imagine-c21-http-operateur")&&!get_user_by("login","imagine-c21-fictif")&&!get_user_by("login","imagine-c21-defaut-fictif")]);')
    assert result['settings']=={k:v['stored'] for k,v in settings.items()}
    assert result['meta']==['imagine_sans_email','imagine_email_confirme','imagine_newsletters_preferences'] and result['fixture_absent'] is True
    return expected

def run(seal=False):
    chain=historical();counts,canonical=evidence();installed=live()
    if seal:
        c21.save('final-fusion',{'status':'PRET_TECHNIQUE_C21_FUSION','failures':[], 'historical_chain':chain,
            'counts':counts,'canonical':canonical,'source_sha256':{n:sha(ROOT/n) for n in OWNED},
            'receipt_sha256':{n:sha(PROOF/n) for n in RECEIPTS},'installed_source_sha256':installed,
            'retention_settings_changed':False,'C09_profiles_preserved':True,'real_authorization':False})
    else:
        final=read('final-fusion.json')
        assert final['status']=='PRET_TECHNIQUE_C21_FUSION' and not final['failures']
        assert final['historical_chain']==chain and final['counts']==counts and final['canonical']==canonical and final['installed_source_sha256']==installed
        for n,d in final['source_sha256'].items(): assert sha(ROOT/n)==d,n
        for n,d in final['receipt_sha256'].items(): assert sha(PROOF/n)==d,n
    print(json.dumps({'C21':'VERIFIE_FUSION','counts':counts,'canonical':canonical,'historical_receipts_unchanged':True,'native_readback':True,'fixtures_absent':True},ensure_ascii=False))

if __name__=='__main__':
    assert sys.argv[1:] in ([],['--seal'])
    run('--seal' in sys.argv)
