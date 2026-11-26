"""C19 bounded successor: immutable old evidence; demo-only code; no fixture/role writes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c19
unit = importlib.import_module('c18-unit')
http = importlib.import_module('c19-http')
PROOF = ROOT / 'production/C-19/corrections-V2'
CODE = sorted(n for n in c19.targets() if not n.endswith('/imagine-site.php')) + ['plugins/imagine-site/EcheancesNatives.php']
PREDECESSORS = ['production/C-17/instruction5-20261126/verification-readback-final-V2.json', 'production/C-18/corrections-V2/final.json']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    (PROOF / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def load(name):
    return json.loads((PROOF / (name + '.json')).read_text(encoding='utf-8'))


def command(args, label, timeout=600):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, timeout=timeout)
    (PROOF / (label + '.log')).write_text(p.stdout + p.stderr, encoding='utf-8')
    print(label + ': exit ' + str(p.returncode), flush=True)
    assert p.returncode == 0, label
    return p.stdout


def live_hashes(names):
    return c19.wp('$o=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$o[$n]=hash_file("sha256",$p);}echo wp_json_encode($o);')


def action():
    return c19.wp('global $wpdb;echo wp_json_encode(["action"=>$wpdb->get_row("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=8793",ARRAY_A),"subscription"=>wcs_get_subscription(101)->get_data()]);')


def contracts():
    baseline = load('baseline-sources')
    assert all(digest(ROOT / n) == sha for n, sha in baseline['historical'].items()), 'Historical C19 evidence changed'
    receipts = {}
    for name in PREDECESSORS:
        receipt = json.loads((ROOT / name).read_text(encoding='utf-8'))
        assert all(digest(ROOT / n) == sha for n, sha in receipt['source_sha256'].items()), name
        runtime_names = [n.removeprefix('wp/') for n in receipt['source_sha256'] if n.startswith('wp/plugins/') and '/tests/' not in n]
        assert live_hashes(runtime_names) == {n: digest(ROOT / 'wp' / n) for n in runtime_names}
        receipts[name] = digest(ROOT / name)
    old = json.loads((ROOT / 'production/C-19/final-V2.json').read_text(encoding='utf-8'))
    bootstrap = 'wp/plugins/imagine-site/imagine-site.php'
    assert digest(ROOT / bootstrap) == old['source_sha256'][bootstrap]
    text = (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    section = text.split('## C-19 — tableau de bord\n', 1)[1].split('\n## ', 1)[0]
    required = ['libelles', 'Catalogue mémoïsé', 'Un instant unique', 'Par moyen de paiement', 'Q-1 reste en attente',
                'c19-corrections.py --readback-only', 'reçus historiques', 'contrat de section']
    assert all(term in section for term in required), 'Shared README C19 contract'
    return {'latest_C17_C18_receipts': receipts, 'README_contract': required,
            'historical_C19_unchanged': True,
            'historical_README_sha256': old['source_sha256']['wp/plugins/imagine-site/README.md'],

            'shared_README_gate': 'section contract, not frozen whole-file digest'}


def sources():
    paths = [ROOT / 'wp' / n for n in CODE]
    paths += list((ROOT / 'wp/plugins/imagine-site/tests').glob('TableauBord*Test.php'))
    paths += [ROOT / 'wp/plugins/imagine-site/tests/fixtures/c19-horloge.php', ROOT / 'wp/tests/demo/c19-runtime.php',
              ROOT / 'wp/tests/demo/c19-http.py', Path(__file__)]
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}


def deploy():
    expected = {n: digest(ROOT / 'wp' / n) for n in CODE}
    before = live_hashes(CODE)
    baseline = load('baseline-sources')['prior_sources']
    for name in CODE:
        assert before[name] in {baseline['wp/' + name], expected[name]}, 'Refuse live drift: ' + name
    native = c19.state()
    for name in CODE:
        if before[name] != expected[name]:
            c19.c18.c17.profils.b00.upload(name, (ROOT / 'wp' / name).read_bytes())
    after = live_hashes(CODE)
    assert after == expected and native == c19.state()
    save('installation', {'before': before, 'after': after, 'scope': 'imagine-test-demo', 'native_preserved': True, 'role_write': False, 'fixture_reset': False})


def run(args):
    c19.c18.c17.profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    prior_contracts = contracts()
    native = c19.state()
    paper = action()
    assert paper['action']['status'] == 'pending' and paper['subscription']['id'] == 101
    save('before', {'native': native, 'paper': paper})
    if args.prepare:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1'], 'preparer-image')
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image.log').read_text(encoding='utf-8')
    unit.PROOF = PROOF
    assert unit.run('unit-c19', 'TableauBord') == 0
    assert unit.run('unit-root', '') == 0
    command([sys.executable, 'wp/tests/demo/test_c19_contract.py'], 'shared-contract')
    source = command(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')], 'wslpath').strip()
    style = command(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777',
        '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly', '--entrypoint', 'php', 'imagine-tests-t01:1',
        '/opt/t01/imagine-site/vendor/bin/phpcs', '--standard=PSR12', '-n', '--report=json', *['/repo/wp/' + n for n in CODE if not n.endswith('/EcheancesNatives.php')]], 'psr12')
    save('psr12', json.loads(style))
    # Shared C15 formatting is not rewritten: prove the seam adds no style error.
    current = (ROOT / 'wp/plugins/imagine-site/EcheancesNatives.php').read_text(encoding='utf-8')
    previous = current.replace('int $days, ?int $maintenant = null', 'int $days')
    previous = previous.replace('        $maintenant ??= time();\n', '')
    previous = previous.replace('mandats($rows, $maintenant, $days)', 'mandats($rows, time(), $days)').replace('echeances($rows, $maintenant, $days)', 'echeances($rows, time(), $days)')
    assert hashlib.sha256(previous.encode()).hexdigest() == load('baseline-sources')['prior_sources']['wp/plugins/imagine-site/EcheancesNatives.php']
    shared_style = {}
    for label, content in [('before', previous), ('after', current)]:
        p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '-i', '--pull', 'never', '--network', 'none', '--read-only',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777',
            '--entrypoint', 'php', 'imagine-tests-t01:1', '/opt/t01/imagine-site/vendor/bin/phpcs', '--standard=PSR12', '-n', '--report=json',
            '--stdin-path=EcheancesNatives.php', '-'], input=content, capture_output=True, text=True, encoding='utf-8', timeout=60)
        assert p.returncode == 2 and not p.stderr
        shared_style[label] = json.loads(p.stdout)
    normalize = lambda r: [{k:v for k,v in m.items() if k not in ['line','column']} for f in r['files'].values() for m in f['messages']]
    assert normalize(shared_style['before']) == normalize(shared_style['after'])
    shared_style['no_new_errors'] = True
    save('psr12-shared-existing', shared_style)
    if args.deploy:
        deploy()
    assert live_hashes(CODE) == {n: digest(ROOT / 'wp' / n) for n in CODE}
    # All new artifacts go under the successor; never rewrite final-V2.json or old runtime receipts.
    c19.PROOF = PROOF
    runtime = c19.runtime('runtime')
    http_result = http.run('http', browser=True)
    if args.canonical:
        raw = command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], 'canonical')
        save('canonical-inputs', sources())
    else:
        assert load('canonical-inputs') == sources(), 'Rerun --canonical after source changes'
        raw = (PROOF / 'canonical.log').read_text(encoding='utf-8')
    matches = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', raw, re.M)
    assert len(matches) == 1
    canonical = json.loads(matches[0])
    assert canonical['pass'] and canonical['errors'] == canonical['failures'] == canonical['skipped'] == 0
    c09 = c19.c18.c17.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";', check=False)
    result_c09 = json.loads(c09['stdout'])
    assert c09['code'] == 0 and result_c09['total'] == len(result_c09['checks']) == 382 and not result_c09['failures']
    assert all(v is True for v in result_c09['checks'].values())
    save('native-c09', result_c09)
    # Native C18 checks are read-only, no CSV export or journal mutation.
    c18_native = c19.wp('require WP_CONTENT_DIR."/imagine-demo-build/c18-corrections-runtime.php";')
    assert c18_native['total'] == len(c18_native['checks']) and not c18_native['failures'] and all(c18_native['checks'].values())
    save('native-c18', c18_native)
    after = c19.state()
    paper_after = action()
    save('after', {'native': after, 'paper': paper_after})
    assert native == after and paper == paper_after
    assert prior_contracts == contracts()
    readback = live_hashes(CODE)
    assert readback == {n: digest(ROOT / 'wp' / n) for n in CODE}
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'status': 'C19_PRET_TECHNIQUE_CORRIGE',
        'unit': {n: {k:v for k,v in load(n).items() if k in ['tests','assertions','exit','removed','image']} for n in ['unit-c19','unit-root']},
        'canonical': canonical, 'runtime_checks': len(runtime['checks']), 'HTTP_browser_checks': http_result['total'],
        'native_C09': {'total': result_c09['total'], 'failures': result_c09['failures'], 'exit': c09['code']},
        'native_C18_checks': c18_native['total'], 'PSR12_errors': json.loads(style)['totals']['errors'],
        'PSR12_shared_existing_errors_unchanged': shared_style['after']['totals']['errors'],
        'sha256_readback': readback, 'source_sha256': sources(), 'shared_contracts': prior_contracts,
        'README_at_receipt_observation_sha256': digest(ROOT / 'wp/plugins/imagine-site/README.md'),
        'native_preserved': True, 'action8793_pending_subscription101_preserved': True, 'fixture_reset': False, 'role_write': False,
        'Q1': 'awaiting explicit access-rights decision; existing composition unchanged',
        'Q2': 'default: seventh grey row, no value or formula', 'visual_approval': False, 'values': http_result['valeurs']}
    save('final', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k in ['status','unit','canonical','runtime_checks','HTTP_browser_checks','native_C09','native_C18_checks','native_preserved']}, ensure_ascii=False))


def readback_only():
    c19.c18.c17.profils.guard('imagine-test-demo')
    final = load('final')
    assert sources() == final['source_sha256']
    assert live_hashes(CODE) == final['sha256_readback']
    assert contracts() == final['shared_contracts']
    assert c19.state() == load('before')['native'] and action() == load('before')['paper']
    target = 'imagine-demo-build/c19-runtime.php'
    assert live_hashes([target]) == {target: digest(ROOT / 'wp/tests/demo/c19-runtime.php')}
    native = c19.wp('require WP_CONTENT_DIR."/' + target + '";')
    assert len(native['checks']) == final['runtime_checks'] and all(v is True for v in native['checks'].values())
    docs = [ROOT / 'production/C-19' / n for n in ['A-VOIR.md', 'PRET', 'QUESTIONS.md']]
    for path in docs:
        text = path.read_text(encoding='utf-8')
        assert 'Q-1' in text and 'Q-2' in text and 'technique' in text
    save('readback', {'at': datetime.now(timezone.utc).isoformat(), 'final_sha256': digest(PROOF / 'final.json'),
        'documents': {p.relative_to(ROOT).as_posix(): digest(p) for p in docs}, 'source_readback_exact': True,
        'native_preserved': True, 'role_write': False, 'historical_proofs_preserved': True, 'visual_approval': False})
    print('C19 successor readback verified; native state and action8793 preserved; Q1 pending; no role write')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--canonical', action='store_true')
    parser.add_argument('--readback-only', action='store_true')
    args = parser.parse_args()
    if args.readback_only:
        assert not (args.prepare or args.deploy or args.canonical)
        readback_only()
    else:
        run(args)
