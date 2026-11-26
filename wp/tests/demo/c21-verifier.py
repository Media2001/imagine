"""C21 receipt/source verifier. Default is read-only; --seal creates the immutable final receipt."""
from pathlib import Path
import copy, hashlib, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c21
ROOT, PROOF = c21.ROOT, c21.PROOF
REPORT = 'files/rapports/2026-11-26-07h32-V2.md'
OWNED = [
    'wp/plugins/imagine-site/Confidentialite.php', 'wp/plugins/imagine-site/ConfidentialiteRegles.php',
    'wp/plugins/imagine-site/tests/ConfidentialiteReglesTest.php',
    'wp/outils/demo/c21.py', 'wp/outils/demo/c21-unit.py',
    'wp/tests/demo/c21-runtime.php', 'wp/tests/demo/c21-security.php', 'wp/tests/demo/c21-failures.php',
    'wp/tests/demo/c21-http.py', 'wp/tests/demo/c21-verifier.py',
    'production/C-21/A-VOIR.md', 'production/C-21/natif.md', 'production/C-21/README-CONTRAT.md', REPORT,
]
RECEIPTS = ['http-complet.json', 'security-final.json', 'failures-final.json', 'regressions-final.json',
    'installation-psr.json', 'conservation-complete.json', 'unit-final.json', 'unit-root-final.json',
    'preparer-image.log', 'rejouer-final.log', 'phpcs-final.log']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((PROOF / name).read_text(encoding='utf-8'))


def normalized(state):
    value = copy.deepcopy(state)
    for key in ('actionscheduler_actions', 'actionscheduler_logs'):
        value['native_fingerprints'].pop(key, None)
    return value


def shared_contracts():
    bootstrap = (ROOT / 'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(c21.BLOCK) == 1
    envoi = (ROOT / 'wp/plugins/imagine-site/EnvoiNatif.php').read_text(encoding='utf-8')
    start = envoi.index("        $data = apply_filters('imagine_envoi_donnees_observation'")
    end = envoi.index("        $events = self::releves($data['id']);", start)
    block = envoi[start:end]
    assert 'imagine_envoi_conserver_observation' in block
    prior = read('baseline-observer.json')['source_before']['plugins/imagine-site/EnvoiNatif.php']
    assert hashlib.sha256(envoi.replace(block, '', 1).encode()).hexdigest() == prior
    original_bootstrap = read('baseline.json')['source_before']['plugins/imagine-site/imagine-site.php']
    assert hashlib.sha256(bootstrap.replace(c21.BLOCK, '', 1).encode()).hexdigest() == original_bootstrap
    section = (PROOF / 'README-CONTRAT.md').read_text(encoding='utf-8')
    assert (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').count(section) == 1
    prerequisites = [line for line in bootstrap.replace(c21.BLOCK, '', 1).splitlines()
        if line.startswith('require_once __DIR__') or re.fullmatch(r'\w+::register\(\);', line)]
    return {'bootstrap_block': c21.BLOCK, 'bootstrap_prerequisites': prerequisites, 'envoi_block': block,
        'envoi_predecessor_sha256': prior, 'bootstrap_predecessor_sha256': original_bootstrap,
        'readme_section': section}


def validate_receipts():
    counts = {}
    for name in ['http-complet.json', 'security-final.json', 'failures-final.json']:
        value = read(name)
        assert value['scope'] == 'imagine-test-demo'
        assert value['total'] == len(value['checks']) and not value['failures'] and all(v is True for v in value['checks'].values())
        counts[name] = value['total']
    reg = read('regressions-final.json')
    for name, value in reg['native'].items():
        assert value['total'] == len(value['checks']) and not value['failures'] and value['all_tables_rollback_exact']
        counts[name] = value['total']
    assert reg['C09']['total'] == len(reg['C09']['checks']) == 382 and not reg['C09']['failures']
    assert all(v is True for v in reg['C09']['checks'].values())
    counts['C09'] = reg['C09']['total']
    action = reg['schedule_business']['action8793']
    assert action['action_id'] == '8793' and action['status'] == 'pending' and json.loads(action['args']) == {'subscription_id': 101}
    log = (PROOF / 'rejouer-final.log').read_text(encoding='utf-8-sig')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', log, re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0]); assert canonical['pass'] and not canonical['failures'] and not canonical['errors']
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image.log').read_text(encoding='utf-8-sig')
    assert not (PROOF / 'phpcs-final.log').read_text(encoding='utf-8-sig').strip()
    for name in ['unit-final.json', 'unit-root-final.json']:
        unit = read(name)
        assert unit['exit'] == 0 and unit['removed'] and not unit['stderr']
        counts[name] = {'tests': unit['tests'], 'assertions': unit['assertions']}
    assert len((PROOF / 'natif.md').read_text(encoding='utf-8').splitlines()) == 10
    return counts, canonical


def live(contracts):
    bootstrap = (ROOT / 'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(contracts['bootstrap_block']) == 1
    lines = iter(bootstrap.splitlines())
    for wanted in contracts['bootstrap_prerequisites']:
        assert any(line == wanted for line in lines), 'Missing predecessor bootstrap contract'
    assert (ROOT / 'wp/plugins/imagine-site/EnvoiNatif.php').read_text(encoding='utf-8').count(contracts['envoi_block']) == 1
    assert (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').count(contracts['readme_section']) == 1
    c21.c19.c18.c17.profils.guard('imagine-test-demo')
    names = list(c21.targets()) + ['imagine-demo-build/c21-' + suffix + '.php' for suffix in ('runtime', 'security', 'failures')]
    expected = {name: sha(path) for name, path in c21.targets().items()}
    expected.update({'imagine-demo-build/c21-' + suffix + '.php': sha(ROOT / ('wp/tests/demo/c21-' + suffix + '.php')) for suffix in ('runtime', 'security', 'failures')})
    actual = c21.hashes(names); assert actual == expected, 'Installed source readback differs'
    assert normalized(c21.c19.c18.state()) == normalized(read('http-complet.json')['native_after'])
    assert c21.schedule_business() == read('regressions-final.json')['schedule_business']
    settings = read('conservation-complete.json')['settings']
    stored = c21.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(list(settings))) + ',true) as $k)$out[$k]=get_option($k,null);echo wp_json_encode($out);')
    assert stored == {key: value['stored'] for key, value in settings.items()}, 'Retention setting drift'
    empty = c21.wp('echo wp_json_encode(get_option("imagine_c21_fixture",null)===null && !get_user_by("login","imagine-c21-fictif") && !get_user_by("login","imagine-c21-defaut-fictif"));')
    assert empty, 'Disposable fixture remains'
    return actual


def run(seal=False):
    counts, canonical = validate_receipts()
    if seal:
        contracts = shared_contracts()
        native = live(contracts)
        c21.save('final', {'status': 'PRET_TECHNIQUE_C21', 'failures': [], 'counts': counts, 'canonical': canonical,
            'source_sha256': {name: sha(ROOT / name) for name in OWNED},
            'receipt_sha256': {name: sha(PROOF / name) for name in RECEIPTS},
            'shared_contracts': contracts, 'installed_source_sha256_at_seal': native,
            'priority_readback': 'A-FAIRE-2 revision 26/11/2026 7h30 : C20 consigne 0 signalee au parent, non traitee',
            'native_request_retained_until_account_deletion': True, 'retention_settings_changed': False,
            'C09_profiles_preserved': True, 'visual_approval': False, 'real_deployment_authorized': False})
    else:
        final = read('final.json')
        assert final['status'] == 'PRET_TECHNIQUE_C21' and final['counts'] == counts and final['canonical'] == canonical
        for name, value in final['source_sha256'].items(): assert sha(ROOT / name) == value, name
        for name, value in final['receipt_sha256'].items(): assert sha(PROOF / name) == value, name
        live(final['shared_contracts'])
    print(json.dumps({'C21': 'VERIFIE', 'counts': counts, 'canonical': canonical, 'fixtures_absent': True, 'native_readback': True}, ensure_ascii=False))

if __name__ == '__main__':
    assert sys.argv[1:] in ([], ['--seal'])
    if not sys.argv[1:] and (PROOF / 'final-fusion.json').exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location('c21_fusion_successor', Path(__file__).with_name('c21-fusion-verifier.py'))
        successor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(successor)
        successor.run()
    else:
        run('--seal' in sys.argv)
