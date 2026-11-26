"""Read-only parent gate for C20 fusion; --seal creates a new receipt only."""
from pathlib import Path
import hashlib, importlib, importlib.util, json, re, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
c20 = importlib.import_module('c20-second')
fusion = importlib.import_module('c20-fusion')
PROOF = ROOT / 'production/C-20/fusion-V2'
OWN = ['wp/plugins/imagine-site/' + n for n in ('Renouvellement.php', 'RenouvellementRegles.php',
    'tests/RenouvellementReglesTest.php', 'tests/C20PaywallAdapterTest.php',
    'tests/C20RenouvellementI18nTest.php', 'tests/fixtures/c20-native-doubles.php')]
OWN += ['wp/outils/demo/c20-fusion.py', 'wp/tests/demo/c20-fusion-verifier.py', 'wp/tests/demo/c20-verifier.py',
    'production/C-20/A-VOIR.md', 'production/C-20/natif.md', 'production/C-20/PRET']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name):
    return json.loads((ROOT / 'production/C-20' / name).read_text(encoding='utf-8'))

def section(text):
    return text.split('\n## C-20 — ', 1)[1].split('\n## C-21 — ', 1)[0]

def contracts():
    preserved = json.loads((PROOF / 'preservation.json').read_text(encoding='utf-8'))
    for name, expected in preserved.items():
        assert sha(ROOT / name) == expected, 'Protected/historical artifact changed: ' + name
    old = (PROOF / 'README.md.before').read_text(encoding='utf-8')
    now = (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    # Only C20 is allowed to change; never pin the whole shared README for future lots.
    strip = lambda s: s.split('\n## C-20 — ', 1)[0] + '\n## C-21 — ' + s.split('\n## C-21 — ', 1)[1]
    assert strip(old) == strip(now), 'A different lot README section changed'
    current = section(now)
    assert all(s in current for s in ('PRET technique', '7 h 30', 'Historique daté', 'arret_a_terme',
        'quatre_fois', 'A-PAPIER', 'reste inconnu', 'aucune fin native essayée', 'sans bouton'))
    assert current.index('Historique daté') < current.index('Pas PRET : le point 2 reste bloqué')
    # Current C21/B05/C22 shared sections remain literal contracts, not whole-file hashes.
    for lot, filename in [('C-21', 'README-CONTRAT.md'), ('B-05', 'README-CONTRAT.md')]:
        assert now.count((ROOT / 'production' / lot / filename).read_text(encoding='utf-8')) == 1
    for lot, seal in [('C-21', 'final.json'), ('B-05', 'final.json')]:
        data = json.loads((ROOT / 'production' / lot / seal).read_text(encoding='utf-8'))
        for name, expected in data['source_sha256'].items():
            if name == 'wp/plugins/imagine-site/Confidentialite.php':
                # Inventory successor already accepted by C22: verified live below.
                assert "'imagine_newsletters_preferences'" in (ROOT / name).read_text(encoding='utf-8')
            else:
                assert sha(ROOT / name) == expected, name
    return current

def receipts():
    t01 = (PROOF / 't01-final.log').read_text(encoding='utf-8-sig')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', t01, re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    assert 'C20PaywallAdapterTest' in t01 and 'C20RenouvellementI18nTest' in t01
    assert 'T01 CLEANUP : absence verifiee' in t01
    assert 'PREPARATION T01 : image verifiee' in (PROOF / 'preparer-image.log').read_text(encoding='utf-8-sig')
    native = load('fusion-native-second-V2.json')
    assert len(native['checks']) == 11 and all(v is True for v in native['checks'].values()) and not native['failures']
    assert native['checks']['pending_cancel_paid_term_before_cutoff_excludes_only_this_subscription']
    assert native['effects'] == [] and native['fresh_profiles_actions_exact']
    assert not native['four']['result']['supported'] and native['four']['result']['C05_block_end'] is None
    assert native['four']['result']['before'] == native['four']['result']['after']
    assert not native['carte']['result']['resumption']['can_resume'] and native['carte']['result']['resumption']['products_unavailable']
    ui = load('fusion-ui-second-V2.json')
    assert ui['total'] == len(ui['checks']) == 18 and not ui['failures'] and all(ui['checks'].values())
    assert ui['profiles_actions_unchanged']
    http = load('fusion-http-second-V2.json')
    assert http['total'] == len(http['checks']) == 27 and not http['failures'] and all(http['checks'].values())
    assert not http['confirmation_action_delivered']
    reg = load('fusion-regressions-second-V2.json')
    for name, total in [('C08', 30), ('C13', 24)]:
        r = reg['native'][name]
        assert r['total'] == len(r['checks']) == total and all(r['checks'].values()) and not r['failures'] and r['all_tables_rollback_exact']
    assert reg['C09']['total'] == len(reg['C09']['checks']) == 382 and all(reg['C09']['checks'].values()) and not reg['C09']['failures']
    assert reg['fresh_profiles_actions_exact']
    mutations = json.loads((PROOF / 'mutations.json').read_text(encoding='utf-8'))
    assert len(mutations['cases']) == 3 and mutations['live_source_unchanged']
    assert all(v['exit'] == 1 and v['removed'] and 'FAILURES!' in v['stdout'] for v in mutations['cases'].values())
    assert mutations['Paywall_sha256'] == sha(ROOT / 'wp/plugins/imagine-site/Paywall.php')
    return canonical

def live():
    c20.c20.profils.guard('imagine-test-demo')
    names = fusion.NAMES + ['plugins/imagine-site/Paywall.php']
    remote = fusion.wp_hashes(names)
    assert remote == {n: sha(ROOT / 'wp' / n) for n in names}
    snapshot = c20.snapshot()
    assert snapshot['profiles'] == load('adapter-red-before-second-V2.json')['profiles']
    assert snapshot['profiles'] == load('fusion-native-after-second-V2.json')['profiles']
    action = [a for a in snapshot['profiles']['A-PAPIER']['actions'] if str(a['action_id']) == '8793']
    assert len(action) == 1 and snapshot['profiles']['A-PAPIER']['id'] == 101
    assert action[0]['status'] == 'pending' and action[0]['scheduled_date_gmt'] == '2026-11-26 02:13:28'
    assert fusion.wp_hashes(['imagine-demo-build/c20-second-native.php'])['imagine-demo-build/c20-second-native.php'] == sha(ROOT / 'wp/tests/demo/c20-second-native.php') == load('fusion-native-second-V2.json')['source_sha256']
    spec = importlib.util.spec_from_file_location('c22_fusion_readonly', ROOT / 'wp/tests/demo/c22-verifier.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.run()
    return remote

def run(seal=False):
    readme = contracts()
    canonical = receipts()
    remote = live()
    pret = (ROOT / 'production/C-20/PRET').read_text(encoding='utf-8')
    assert 'PERIMETRE_REDUIT_0730' in pret and 'imagine_non_renouvellement_confirme' in pret
    owned = OWN + ['files/rapports/2026-11-26-09h22-V2.md']
    data = {'status': 'PRET_TECHNIQUE_C20_FUSION_PERIMETRE_REDUIT_0730', 'scope': 'imagine-test-demo',
        'source_sha256': {n: sha(ROOT / n) for n in owned}, 'README_C20_contract': readme,
        'deployed_source_readback': remote, 'canonical': canonical,
        'native': 11, 'ui': 18, 'HTTP': 27, 'C08': 30, 'C13': 24, 'C09': 382,
        'C22_successor_readback': True, 'C21_B05_sections_preserved': True,
        'profiles_actions_exact': True, 'Paywall_C06_C13_unchanged': True,
        'historical_receipts_preserved': True, 'visual_approval': False, 'real_deployment_authorized': False,
        'deferred': ['nonrenew_button', 'confirmation', 'imagine_non_renouvellement_confirme', 'four_native_end_proof', 'presentation_priority_at_branch', 'real_paper_method_at_branch']}
    paths = [p for p in PROOF.rglob('*') if p.is_file() and p.name != 'final.json']
    paths += [ROOT / 'production/C-20' / n for n in ['fusion-native-second-V2.json', 'fusion-native-before-second-V2.json',
        'fusion-native-after-second-V2.json', 'fusion-ui-second-V2.json', 'fusion-regressions-second-V2.json',
        'fusion-http-second-V2.json', 'fusion-http-before-second-V2.json', 'fusion-http-after-second-V2.json']]
    paths += [ROOT / 'production/C-20' / n for n in load('fusion-http-second-V2.json')['captures']]
    path = PROOF / 'final.json'
    if not seal:
        paths = [ROOT / n for n in json.loads(path.read_text(encoding='utf-8'))['receipt_sha256']]
    data['receipt_sha256'] = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    if seal:
        assert not path.exists(), 'Historical seals are immutable'
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        assert json.loads(path.read_text(encoding='utf-8')) == data, 'Receipt differs from current sources/receipts'
    print('C20 FUSION VERIFIED: T01 ' + str(canonical['tests']) + '/' + str(canonical['assertions']) + '; native 11; UI 18; HTTP 27; C08 30; C13 24; C09 382; C22 preserved; action 8793 exact. PRET technical/reduced only.')
    return data

if __name__ == '__main__':
    assert sys.argv[1:] in ([], ['--seal'])
    run('--seal' in sys.argv)
