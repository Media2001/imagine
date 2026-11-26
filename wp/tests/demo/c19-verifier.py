"""C19 final gates; no fixture reset or rights mutation, optional code installation."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib, json, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c19
ROOT, PROOF = c19.ROOT, c19.PROOF
successor = importlib.import_module('c09-successor-gates')


def command(args, name):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (PROOF / name).write_text(p.stdout + p.stderr, encoding='utf-8')
    print(name + ': exit ' + str(p.returncode))
    if p.returncode:
        raise RuntimeError('Gate failed: ' + name)
    return p.stdout


def style():
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')], capture_output=True, text=True, check=True).stdout.strip()
    paths = ['/repo/wp/' + name for name in c19.targets() if not name.endswith('/imagine-site.php')]
    paths += ['/repo/wp/plugins/imagine-site/tests/TableauBordReglesTest.php']
    raw = command(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none',
        '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534',
        '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777', '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly',
        '--entrypoint', 'php', 'imagine-tests-t01:1', '/opt/t01/imagine-site/vendor/bin/phpcs',
        '--standard=PSR12', '-n', '--report=json', *paths], 'psr12-final.log')
    result = json.loads(raw)
    assert result['totals']['errors'] == 0
    c19.save('psr12-final', result)
    return result['totals']


def run(args):
    c19.c18.c17.profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1'], 'preparer-image-final.log')
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image-final.log').read_text(encoding='utf-8')
    if args.deploy:
        c19.deploy()
    before = c19.state()
    c19.save('verification-before', before)
    command([sys.executable, 'wp/outils/demo/c19-unit.py', 'unit-final'], 'unit-final.log')
    command([sys.executable, 'wp/outils/demo/c19-unit.py', 'unit-root-final', '--root'], 'unit-root-final.log')
    command([sys.executable, 'wp/tests/demo/test_c19_contract.py'], 'shared-contract-final.log')
    style_result = style()
    native_c19 = c19.runtime()
    command([sys.executable, 'wp/tests/demo/c19-http.py', 'http-final', '--browser'], 'http-final.log')
    canonical_sources = list(c19.targets().values()) + [ROOT / 'wp/plugins/imagine-site/tests/TableauBordReglesTest.php']
    canonical_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in canonical_sources}
    if args.canonical:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], 'rejouer-t01-final.log')
        c19.save('canonical-inputs', canonical_hashes)
    else:
        assert json.loads((PROOF / 'canonical-inputs.json').read_text(encoding='utf-8')) == canonical_hashes, 'Re-run --canonical after PHP changes'
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', (PROOF / 'rejouer-t01-final.log').read_text(encoding='utf-8'), re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    c09 = successor.repair.native()
    assert c09['exit'] == 0 and c09['total'] == len(c09['checks']) == 382
    assert not c09['failures'] and all(v is True for v in c09['checks'].values())
    c19.save('c09-native-final', c09)
    # Reuse deployed C18 probe without re-upload, export or journal write.
    c18runtime = c19.wp('require WP_CONTENT_DIR."/imagine-demo-build/c18-runtime.php";')
    assert c18runtime['checks'] and all(v is True for v in c18runtime['checks'].values())
    c19.save('c18-native-final', c18runtime)
    after = c19.state()
    c19.save('verification-after', after)
    assert before == after
    repaired = successor.repair_receipt()['after']
    assert {k:after[k] for k in repaired} == repaired, 'C09 restored baseline drift'
    hashes = c19.readback()
    shared = {}
    for lot in ('C-17', 'C-18'):
        historical = json.loads((ROOT / 'production' / lot / 'final.json').read_text(encoding='utf-8'))
        for name, expected in historical['source_sha256'].items():
            if name in {'wp/tests/demo/c17-verifier.py', 'wp/tests/demo/c18-verifier.py'}:
                continue
            data = (ROOT / name).read_bytes()
            if lot == 'C-17' and name == 'wp/plugins/imagine-site/imagine-site.php':
                expected = json.loads((ROOT / 'production/C-18/final.json').read_text(encoding='utf-8'))['source_sha256'][name]
            assert c19.matches_predecessor(name, data, expected), 'Predecessor drift: ' + name
            if name.endswith('imagine-site.php') or name.endswith('README.md'):
                shared[lot + ':' + name] = {'historical': expected, 'current': hashlib.sha256(data).hexdigest(), 'predecessor_exact_after_C19_section_removal': True}
    http = json.loads((PROOF / 'http-final.json').read_text(encoding='utf-8'))
    assert http['total'] == len(http['checks']) and not http['failures']
    receipts = {}
    for name in ('unit-final', 'unit-root-final'):
        unit = json.loads((PROOF / (name + '.json')).read_text(encoding='utf-8'))
        assert unit['exit'] == 0 and unit['removed']
        receipts[name] = {'tests': unit['tests'], 'assertions': unit['assertions'], 'container_removed': True}
    receipts['native'] = {'checks': len(native_c19['checks']), 'failures': []}
    receipts['HTTP_browser'] = {'checks': http['total'], 'failures': []}
    sources = canonical_sources + [ROOT / 'wp/plugins/imagine-site/README.md']
    sources += sorted((ROOT / 'wp/outils/demo').glob('c19*.py')) + sorted((ROOT / 'wp/tests/demo').glob('c19*.*'))
    sources += [ROOT / 'wp/tests/demo/test_c19_contract.py', ROOT / 'wp/tests/demo/c09-successor-gates.py']
    result = {'at': datetime.now(timezone.utc).isoformat(), 'status': 'PRET_TECHNIQUE_C19', 'scope': 'imagine-test-demo',
        'receipts': receipts, 'canonical_T01': canonical, 'PSR12_errors_only': style_result, 'valeurs': http['valeurs'],
        'sha256_readback': hashes, 'source_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'shared_successors_no_historical_rewrite': shared, 'native_C09': {'exit': c09['exit'], 'checks': c09['total'], 'failures': []},
        'C09_repaired_baseline_exact': True, 'C18_native_checks': len(c18runtime['checks']), 'native_state_preserved': before == after,
        'volatile_bootstrap_options_excluded': ['_transient_timeout_wcs_woocommerce_active_version', '_transient_timeout_novamira-pro_update_checker', 'action_scheduler_lock_async-request-runner'],
        'screen_SQL_writes': 0, 'screen_outgoing_calls': 0, 'fixture_reset': False, 'role_write': False,
        'capture': http['capture'], 'visual_approval': False}
    c19.save('final-V2', result)
    print(json.dumps({'status': result['status'], 'receipts': receipts, 'canonical_T01': canonical, 'C09': '382/382', 'native_preserved': True}, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--canonical', action='store_true')
    args = parser.parse_args()
    run(args)
