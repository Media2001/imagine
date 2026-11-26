"""C20 successor readback: exact scoped delta, closed libraries and raw RED preserved."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib, json, re, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
c20 = importlib.import_module('c20-second')
PROOF = ROOT / 'production/C-20'
FINAL = PROOF / 'final-second-V2.json'
BLOCKS = {
'wp/plugins/imagine-site/Paywall.php': "                } elseif ($subStatus === 'pending-cancel' && $status === 'pending'\n                    && $subscription->get_date('end', 'gmt') !== '') {\n                    // Memberships « pending cancellation », pas un premier virement.\n                    // Les bornes natives ci-dessus restent soumises au moteur C06.\n                    $state = 'actif';\n",
'wp/plugins/imagine-site/imagine-site.php': "require_once __DIR__ . '/Renouvellement.php';\nRenouvellement::register();\n\n",
'wp/themes/imagine/parts/mon-compte.php': "<?php if (function_exists('do_action')) { do_action('imagine_compte_renouvellement', $a); } ?>\n",
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def predecessor(name, data):
    # C21 is an additive, sealed successor; remove only its exact verified sections.
    c21seal = ROOT / 'production/C-21/final.json'
    if c21seal.exists():
        shared = json.loads(c21seal.read_text(encoding='utf-8'))['shared_contracts']
        key = {'wp/plugins/imagine-site/imagine-site.php': 'bootstrap_block',
               'wp/plugins/imagine-site/EnvoiNatif.php': 'envoi_block',
               'wp/plugins/imagine-site/README.md': 'readme_section'}.get(name)
        if key:
            block21 = shared[key].encode()
            assert data.count(block21) == 1, 'C21 successor section absent/repeated: ' + name
            data = data.replace(block21, b'', 1)
    if name in BLOCKS:
        block = BLOCKS[name].encode()
        assert data.count(block) == 1, 'C20 shared delta absent/repeated: ' + name
        if name.endswith('/Paywall.php'):
            return data.replace(block, b'', 1)
        return data.replace(block, b'', 1)
    if name == 'wp/plugins/imagine-site/README.md':
        marker = '\n## C-20 — deuxième passe partielle\n'.encode()
        assert data.count(marker) == 1
        return data.split(marker,1)[0]
    return data

def matches_predecessor(name, data, expected):
    """Read-only bridge for parent gates; bound to the exact sealed C20 successor."""
    if hashlib.sha256(data).hexdigest() == expected:
        return True
    seal = PROOF / 'final-closure-0730-V2.json'
    receipt = json.loads((seal if seal.exists() else FINAL).read_text(encoding='utf-8'))
    if hashlib.sha256(data).hexdigest() != receipt['source_sha256'].get(name):
        return False
    previous = predecessor(name,data)
    if hashlib.sha256(previous).hexdigest() == expected:
        return True
    if name in ('wp/plugins/imagine-site/imagine-site.php','wp/plugins/imagine-site/README.md'):
        import c19
        return c19.matches_predecessor(name,previous,expected)
    return False

def local_contracts():
    baseline = json.loads((PROOF/'protected-baseline-second-V2.json').read_text(encoding='utf-8'))
    out = {}
    for name, old in baseline.items():
        data = (ROOT/name).read_bytes()
        previous = predecessor(name,data) if name in BLOCKS or name == 'wp/plugins/imagine-site/EnvoiNatif.php' else data
        assert hashlib.sha256(previous).hexdigest() == old, 'Protected/source predecessor drift: ' + name
        out[name] = {'before':old,'after':hashlib.sha256(data).hexdigest(),'changed':old!=hashlib.sha256(data).hexdigest()}
    name = 'wp/plugins/imagine-site/README.md'
    old = digest(PROOF/'README-before-second-V2.md')
    assert hashlib.sha256(predecessor(name,(ROOT/name).read_bytes())).hexdigest() == old
    out[name] = {'before':old,'after':digest(ROOT/name),'changed':True}
    first = json.loads((PROOF/'first-proof-preservation-second-V2.json').read_text(encoding='utf-8'))
    assert all(digest(PROOF/n)==v for n,v in first.items()), 'First-pass raw evidence changed'
    oldseal = json.loads((PROOF/'files-final-V2.json').read_text(encoding='utf-8'))
    for name, expected in oldseal.items():
        if name.endswith('natif.md'):
            path = PROOF/'legacy-natif-before-second-V2.md'
        elif name.endswith('A-VOIR.md'):
            path = PROOF/'legacy-A-VOIR-before-second-V2.md'
        else:
            path = ROOT/Path(name)
        assert digest(path) == expected, 'Historical predecessor changed: ' + name
    return out

def historical_run(seal=False):
    contracts = local_contracts()
    names = list(BLOCKS) + ['wp/plugins/imagine-site/Renouvellement.php','wp/plugins/imagine-site/RenouvellementRegles.php']
    c20.c20.profils.guard('imagine-test-demo')
    remote = c20.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps([n.removeprefix('wp/') for n in names])) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$out["wp/".$n]=hash_file("sha256",$p);}echo wp_json_encode($out);')
    assert remote == {n:digest(ROOT/n) for n in names}
    before = json.loads((PROOF/'adapter-red-before-second-V2.json').read_text(encoding='utf-8'))
    current = c20.snapshot()
    assert before['profiles'] == current['profiles'], 'All four original profiles/actions must be exact'
    c09 = c20.wp('require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php";')
    assert c09['total'] == len(c09['checks']) == 382 and not c09['failures']
    action = [a for a in current['profiles']['A-PAPIER']['actions'] if str(a['action_id'])=='8793']
    assert len(action)==1 and action[0]['status']=='pending' and action[0]['scheduled_date_gmt']=='2026-11-26 02:13:28'
    assert current['profiles']['A-PAPIER']['id']==101
    assert not (PROOF/'PRET').exists(), 'C20 acceptance still blocked: PRET is not authorized'
    native = json.loads((PROOF/'native-final-blocked-second-V2.json').read_text(encoding='utf-8'))
    assert native['failures']==['pending_cancel_shipping_unchanged'] and not native['four']['result']['supported']
    http = json.loads((PROOF/'http-final-source-second-V2.json').read_text(encoding='utf-8'))
    assert http['total']==len(http['checks'])==27 and not http['failures'] and not http['confirmation_action_delivered']
    ui = json.loads((PROOF/'presentation-final-source-second-V2.json').read_text(encoding='utf-8'))
    assert ui['total']==len(ui['checks'])==18 and not ui['failures']
    reg = json.loads((PROOF/'non-regression-final-source-second-V2.json').read_text(encoding='utf-8'))
    assert all(not v['failures'] and v['all_tables_rollback_exact'] for v in reg['native'].values())
    t01 = (PROOF/'t01-second-final.log').read_text(encoding='utf-8')
    matches = re.findall(r'^T01_RESULT (\{.*\})$',t01,re.M)
    assert len(matches)==1
    t01_data = json.loads(matches[0])
    assert t01_data['pass'] and not any(t01_data[k] for k in ('failures','errors','skipped'))
    source_names = names + ['wp/plugins/imagine-site/README.md','wp/plugins/imagine-site/tests/RenouvellementReglesTest.php',
        'wp/outils/demo/c20-second.py','wp/outils/demo/c20-unit.py','wp/tests/demo/c20-second-native.php','wp/tests/demo/c20-ui.php',
        'wp/tests/demo/c20-regressions.php','wp/tests/demo/c20-http.py','wp/tests/demo/c20-verifier.py',
        'production/C-20/A-VOIR.md','production/C-20/natif.md']
    data = {'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'BLOCKED_PARTIAL_NO_PRET',
        'source_sha256':{n:digest(ROOT/n) for n in source_names},'successor_contracts':contracts,
        'deployed_source_sha256':remote,'native_acceptance_failures':native['failures'],
        'C05_end_probe':'NOT_EXECUTED_REQUIRED_MARGIN_ABSENT','C09_total':382,'action_8793_exact':True,
        'profiles_actions_exact':True,'first_pass_raw_evidence_preserved':True,'t01':t01_data,
        'http_total':http['total'],'native_UI_total':ui['total'],'visual_approval':False,'PRET':False}
    if seal:
        assert not FINAL.exists(), 'Never overwrite a historical C20 seal'
        FINAL.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    else:
        prior = json.loads(FINAL.read_text(encoding='utf-8'))
        assert data['source_sha256']==prior['source_sha256'] and data['successor_contracts']==prior['successor_contracts']
        assert data['deployed_source_sha256']==prior['deployed_source_sha256']
    print(json.dumps({k:v for k,v in data.items() if k not in ('source_sha256','successor_contracts','deployed_source_sha256')},ensure_ascii=False))
    return data

def run(seal=False):
    path = ROOT / 'wp/tests/demo/c20-closure-verifier.py'
    spec = importlib.util.spec_from_file_location('c20_closure', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from types import SimpleNamespace
    return module.run(SimpleNamespace(**globals()), seal)

if __name__=='__main__':
    run('--seal' in sys.argv)
