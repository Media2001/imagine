"""C18 focused final verification; optional preparation/deploy/canonical replay, no reset."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, json, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c18
import importlib
successor = importlib.import_module('c09-successor-gates')
ROOT, PROOF = c18.ROOT, c18.PROOF


def command(args, name):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (PROOF / name).write_text(p.stdout + p.stderr, encoding='utf-8')
    print(name + ': exit ' + str(p.returncode))
    if p.returncode:
        raise RuntimeError('Gate failed: ' + name)
    return p.stdout


def style():
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\','/')], capture_output=True, text=True, check=True).stdout.strip()
    paths = ['/repo/wp/' + name for name in c18.targets() if not name.endswith('/imagine-site.php')]
    raw = command(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none',
                   '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534',
                   '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777', '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly',
                   '--entrypoint', 'php', 'imagine-tests-t01:1', '/opt/t01/imagine-site/vendor/bin/phpcs',
                   '--standard=PSR12', '-n', '--report=json', *paths], 'psr12-final.log')
    result = json.loads(raw)
    assert result['totals']['errors'] == 0
    c18.save('psr12-final', result)
    return result['totals']


def run(args):
    c18.c17.profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1'], 'preparer-image-final.log')
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image-final.log').read_text(encoding='utf-8')
    if args.deploy:
        c18.deploy()
    before = c18.state()
    c18.save('verification-before', before)
    command([sys.executable, 'wp/outils/demo/c18-unit.py', 'unit-final'], 'unit-final.log')
    command([sys.executable, 'wp/outils/demo/c18-unit.py', 'unit-root-final', '--root'], 'unit-root-final.log')
    style_result = style()
    c18.runtime()
    command([sys.executable, 'wp/tests/demo/c18-http.py', 'http-final'], 'http-final.log')
    command([sys.executable, 'wp/tests/demo/c18-visuel.py'], 'visuel-final.log')
    canonical_sources = list(c18.targets().values()) + [ROOT / 'wp/plugins/imagine-site/tests/ExtractionsReglesTest.php']
    canonical_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in canonical_sources}
    if args.canonical:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], 'rejouer-t01-final.log')
        c18.save('canonical-inputs', canonical_hashes)
    else:
        assert json.loads((PROOF / 'canonical-inputs.json').read_text(encoding='utf-8')) == canonical_hashes, 'Run --canonical after changing C18 PHP inputs'
    marker = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', (PROOF / 'rejouer-t01-final.log').read_text(encoding='utf-8'), re.M)
    assert len(marker) == 1
    canonical = json.loads(marker[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    native = c18.c17.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";', check=False)
    assert not native['stderr']
    c09 = json.loads(native['stdout'])
    assert c09['total'] == len(c09['checks'])
    assert native['code'] == 0 and c09['total'] == 382 and c09['failures'] == []
    assert all(v is True for v in c09['checks'].values())
    c18.save('c09-native-final', {'exit': native['code'], 'total': c09['total'], 'failures': c09['failures']})
    after = c18.state()
    c18.save('verification-after', after)
    assert before == after, 'Native state changed'
    baseline = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))['baseline']
    bridge = successor.baseline_contract(baseline, after, successor.repair_receipt())
    hashes = c18.readback()
    c17_installation = json.loads((ROOT / 'production/C-17/installation.json').read_text(encoding='utf-8'))
    prior = c17_installation['sha256_readback']
    current = c18.wp('$o=[];foreach(json_decode(' + json.dumps(json.dumps(list(prior))) + ',true) as $n){$o[$n]=hash_file("sha256",WP_CONTENT_DIR."/".$n);}echo wp_json_encode($o);')
    nonshared = {n: value for n, value in prior.items() if n != 'plugins/imagine-site/imagine-site.php'}
    assert nonshared == {n: current[n] for n in nonshared}
    receipts = {}
    for name in ('unit-final', 'unit-root-final'):
        v = json.loads((PROOF / (name + '.json')).read_text(encoding='utf-8'))
        assert v['exit'] == 0 and v['removed']
        receipts[name] = {'tests': v['tests'], 'assertions': v['assertions'], 'container_removed': True}
    native_receipt = json.loads((PROOF / 'runtime-final.json').read_text(encoding='utf-8'))
    assert native_receipt['native_unchanged'] and all(v is True for v in native_receipt['checks'].values())
    receipts['runtime'] = {'checks': len(native_receipt['checks']), 'failures': []}
    http = json.loads((PROOF / 'http-final.json').read_text(encoding='utf-8'))
    assert http['total'] == len(http['checks']) and not http['failures'] and all(v is True for v in http['checks'].values())
    receipts['HTTP'] = {'checks': http['total'], 'failures': []}
    csvs = {}
    for entry in http['exports']:
        path = PROOF / entry['csv']
        with path.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == entry['rows']
        csvs[path.name] = {'rows': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'reopened': True}
    sources = list(c18.targets().values()) + [ROOT / 'wp/plugins/imagine-site/README.md', ROOT / 'wp/plugins/imagine-site/tests/ExtractionsReglesTest.php']
    sources += sorted((ROOT / 'wp/outils/demo').glob('c18*.py')) + sorted((ROOT / 'wp/tests/demo').glob('c18*.*'))
    shared_runtime = [ROOT / 'wp/tests/demo/c16-unit-runtime.php', ROOT / 'wp/tests/demo/b04-unit-bootstrap.php']
    shared = {'plugins/imagine-site/imagine-site.php': {'historical_C17': prior['plugins/imagine-site/imagine-site.php'],
                                                      'successor_C18': current['plugins/imagine-site/imagine-site.php']},
              'README_local_C18_sha256': hashlib.sha256((ROOT / 'wp/plugins/imagine-site/README.md').read_bytes()).hexdigest()}
    result = {'at': datetime.now(timezone.utc).isoformat(), 'status': 'PRET_TECHNIQUE_C18_C09_RESTAURE',
              'scope': 'imagine-test-demo', 'receipts': receipts, 'canonical_T01': canonical, 'PSR12_errors_only': style_result,
              'sha256_readback': hashes, 'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              'shared_runtime_readonly_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in shared_runtime},
              'shared_digest_successor_no_historical_rewrite': shared, 'C17_nonshared_sources_unchanged': nonshared,
              'CSV_reopened': csvs, 'native_state_preserved': before == after, 'authorized_baseline_successor': bridge,
              'native_C09': {'exit': native['code'], 'total': c09['total'], 'failures': c09['failures'], 'historical_action_unchanged': after['reserve_native_C09_action8103']},
              'global_C09_green': True, 'visual_approval': False, 'fixture_reset': False}
    c18.save('final-V2', result)
    print(json.dumps({'status': result['status'], 'receipts': receipts, 'canonical_T01': canonical,
                      'native_preserved': True, 'CSV_files_reopened': len(csvs), 'C09_reserved_failures': c09['failures']}, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--canonical', action='store_true')
    parser.add_argument('--readback-only', action='store_true')
    args = parser.parse_args()
    if args.readback_only:
        assert not (args.prepare or args.deploy or args.canonical)
        successor.run('C-18')
    else:
        run(args)
