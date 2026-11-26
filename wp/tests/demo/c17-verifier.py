"""C17 final gates; only the documented unchanged C09 historical action is reserved."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c17
ROOT=c17.ROOT
PROOF=c17.PROOF

def command(args,log):
    p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (PROOF/log).write_text(p.stdout+p.stderr,encoding='utf-8')
    print(log+': exit '+str(p.returncode))
    if p.returncode:raise RuntimeError('Gate failed: '+log)

def run():
    c17.profils.guard('imagine-test-demo')
    if '--prepare' in sys.argv:command(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/preparer-image.ps1'],'preparer-image-final.log')
    if '--deploy' in sys.argv:c17.deploy()
    before=c17.state();c17.save('verification-before',before)
    command([sys.executable,'wp/outils/demo/c17-unit.py','unit-final'],'unit-final.log')
    command([sys.executable,'wp/outils/demo/c17-unit.py','unit-root-final','--root'],'unit-root-final.log')
    command([sys.executable,'wp/tests/demo/c17-http.py','http-final'],'http-final.log')
    command([sys.executable,'wp/tests/demo/c17-reglages.py','reglages-final'],'reglages-final.log')
    command([sys.executable,'wp/tests/demo/c17-faults.py'],'faults-final.log')
    command(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/rejouer.ps1'],'rejouer-t01-final.log')
    hashes=c17.readback()
    after=c17.state();c17.save('verification-after',after)
    assert before==after,'Native state differs'
    original=json.loads(sorted(PROOF.glob('installation-*.json'))[0].read_text(encoding='utf-8'))['before']
    assert original==after,'Native state differs from first C17 installation'
    r=c17.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";',check=False)
    assert not r['stderr'];native=json.loads(r['stdout']);c17.save('c09-native-final',native)
    assert native['total']==len(native['checks'])
    reserve=['A-PAPIER:action_native_planifiee_ou_absente_selon_statut']
    assert native['failures']==reserve and before['reserve_native_C09_action8103']['status']=='canceled'
    assert before['reserve_native_C09_action8103']==after['reserve_native_C09_action8103']
    receipts={}
    for name in ['http-final','reglages-final','faults-final']:
        v=json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert v['total']==len(v['checks']) and not v['failures'] and all(x is True for x in v['checks'].values())
        receipts[name]={'checks':v['total'],'failures':[]}
    for name in ['unit-final','unit-root-final']:
        v=json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert v['exit']==0 and v['removed']
        counts=re.search(r'OK \((\d+) tests?, (\d+) assertions?\)',v['stdout'])
        assert counts
        receipts[name]={'tests':int(counts[1]),'assertions':int(counts[2]),'container_removed':v['removed']}
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',(PROOF/'rejouer-t01-final.log').read_text(encoding='utf-8'),re.M)
    assert len(markers)==1;canonical=json.loads(markers[0]);assert canonical['pass']
    prep=PROOF/('preparer-image-final.log' if (PROOF/'preparer-image-final.log').is_file() else 'preparer-image.log')
    assert 'T01 IMAGE READY' in prep.read_text(encoding='utf-8')
    c16=json.loads((ROOT/'production/C-16/installation.json').read_text(encoding='utf-8'))
    preserved={};shared={}
    for name,old in c16['sha256_readback'].items():
        target=('imagine-demo-build/' if name in ['c09-seed.php','c16-reset.php'] else 'plugins/imagine-site/')+name
        actual=c17.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.'+json.dumps('/'+target)+'));')
        if name in ['imagine-site.php','c09-seed.php']:shared[name]={'historical_C16_sha256':old,'current_C17_sha256':actual}
        else:assert actual==old;preserved[name]=actual
    sources=list(c17.targets().values())+[ROOT/'wp/outils/demo/profils.py',ROOT/'wp/outils/demo/c17.py',ROOT/'wp/outils/demo/c17-unit.py',ROOT/'wp/plugins/imagine-site/tests/JustificatifReglesTest.php']
    sources+=sorted((ROOT/'wp/tests/demo').glob('c17*.py'))
    source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'at':datetime.now(timezone.utc).isoformat(),'status':'PRET_TECHNIQUE_C17_AVEC_RESERVE_HISTORIQUE_C09',
        'scope':'imagine-test-demo','receipts':receipts,'canonical_T01':canonical,'sha256_readback':hashes,
        'source_sha256':source_hashes,'native_state_exactly_preserved':before==after==original,
        'C16_nonshared_sources_unchanged':preserved,'shared_digest_successor_not_historical_rewrite':shared,
        'native_C09':{'exit':r['code'],'total':native['total'],'failures':native['failures'],'historical_action_unchanged':after['reserve_native_C09_action8103']},
        'global_C09_green':False,'visual_approval':False,'C18_treated':False}
    c17.save('final',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':sys.exit(run())
