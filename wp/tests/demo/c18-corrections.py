"""Scoped C18 correction acceptance, C19 read-only seam; never seed/reset/other lots."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, importlib, json, re, subprocess, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c18
unit = importlib.import_module('c18-unit')
http = importlib.import_module('c18-http')
visual = importlib.import_module('c18-visuel')
PROOF = ROOT / 'production/C-18/corrections-V2'
CODE = ['plugins/imagine-site/' + n for n in ('MonCompte.php', 'ExtractionsNatives.php', 'ExtractionsAdmin.php', 'extractions/etat.php')]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, value):
    path = PROOF / (name + '.json')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    assert json.loads(path.read_text(encoding='utf-8')) == value


def command(args, label):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (PROOF / (label + '.log')).write_text(p.stdout + p.stderr, encoding='utf-8')
    print(label + ': exit ' + str(p.returncode), flush=True)
    assert p.returncode == 0, 'Gate failed: ' + label
    return p.stdout


def live_hashes(names):
    return c18.wp('$o=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$o[$n]=hash_file("sha256",$p);}echo wp_json_encode($o);')


def protected_sources():
    paths = list((ROOT / 'wp/plugins/imagine-site').glob('TableauBord*.php'))
    paths += list((ROOT / 'wp/plugins/imagine-site/indicateurs').glob('*.php'))
    paths += list((ROOT / 'wp/tests/demo').glob('c19*.*'))
    paths += list((ROOT / 'wp/outils/demo').glob('c19*.*'))
    paths += [ROOT / 'wp/plugins/imagine-site' / n for n in ('imagine-site.php', 'README.md', 'MonCompteRegles.php')]
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in paths if p.is_file()}


def historical():
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in (ROOT / 'production/C-18').iterdir()
            if p.is_file() and p.name not in {'A-VOIR.md', 'PRET'} and not p.name.startswith('corrections-')}


def action():
    return c18.wp(r'''global $wpdb;echo wp_json_encode(['action'=>$wpdb->get_row("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=8793",ARRAY_A), 'subscription'=>wcs_get_subscription(101)->get_data()]);''')


def deploy():
    expected = {n: digest(ROOT / 'wp' / n) for n in CODE}
    before = live_hashes(CODE)
    if before == expected and (PROOF / 'installation.json').is_file():
        assert json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))['after'] == expected
        return
    historical_install = json.loads((ROOT / 'production/C-18/installation.json').read_text(encoding='utf-8'))['sha256_readback']
    mon = (ROOT / 'wp/plugins/imagine-site/MonCompte.php').read_text(encoding='utf-8')
    old_mon = mon.replace("        return __(self::etatCle($sub), 'imagine-site');\n    }\n\n    /** Même projection B02, avant traduction : clé stable pour C18 et ses consommateurs. */\n    public static function etatCle(\\WC_Subscription $sub): string\n    {\n", '')
    old_mon = old_mon.replace('return MonCompteRegles::etat([', 'return __(MonCompteRegles::etat([').replace("], new DateTimeImmutable('now', new DateTimeZone('UTC')));", "], new DateTimeImmutable('now', new DateTimeZone('UTC'))), 'imagine-site');")
    for name in CODE:
        predecessor = hashlib.sha256(old_mon.encode()).hexdigest() if name.endswith('/MonCompte.php') else historical_install[name]
        assert before[name] in {predecessor, expected[name]}, 'Source drift, refusing overwrite: ' + name
    state = c18.state()
    for name in CODE:
        if before[name] != expected[name]:
            c18.c17.profils.b00.upload(name, (ROOT / 'wp' / name).read_bytes())
    after = live_hashes(CODE)
    assert after == expected and state == c18.state()
    save('installation', {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo',
        'before': before, 'after': after, 'native_preserved': True, 'allowlist': CODE, 'fixture_reset': False})


def run(args):
    c18.c17.profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    old = historical()
    protected = protected_sources()
    native_before = c18.state()
    paper_before = action()
    assert paper_before['action']['status'] == 'pending' and paper_before['subscription']['id'] == 101
    save('before', {'native': native_before, 'paper': paper_before, 'historical': old, 'protected': protected})
    if args.prepare:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1'], 'preparer-image')
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image.log').read_text(encoding='utf-8')
    if args.deploy:
        deploy()
    assert live_hashes(CODE) == {n: digest(ROOT / 'wp' / n) for n in CODE}
    unit.PROOF = PROOF
    assert unit.run('unit-c18', 'Extractions') == 0
    assert unit.run('unit-root', '') == 0
    source = command(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')], 'wslpath').strip()
    style = command(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777',
        '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly', '--entrypoint', 'php', 'imagine-tests-t01:1',
        '/opt/t01/imagine-site/vendor/bin/phpcs', '--standard=PSR12', '-n', '--report=json',
        *['/repo/wp/' + n for n in CODE if not n.endswith('/MonCompte.php')]], 'psr12')
    style = json.loads(style)
    assert style['totals']['errors'] == 0
    save('psr12', style)
    # Shared B02 formatting predates this seam. Compare real PHPCS stdin runs,
    # rather than rewriting unrelated methods or pretending the whole file is clean.
    mon = (ROOT / 'wp/plugins/imagine-site/MonCompte.php').read_text(encoding='utf-8')
    predecessor = mon.replace("        return __(self::etatCle($sub), 'imagine-site');\n    }\n\n    /** Même projection B02, avant traduction : clé stable pour C18 et ses consommateurs. */\n    public static function etatCle(\\WC_Subscription $sub): string\n    {\n", '')
    predecessor = predecessor.replace('return MonCompteRegles::etat([', 'return __(MonCompteRegles::etat([').replace("], new DateTimeImmutable('now', new DateTimeZone('UTC')));", "], new DateTimeImmutable('now', new DateTimeZone('UTC'))), 'imagine-site');")
    installation = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(predecessor.encode()).hexdigest() == installation['before']['plugins/imagine-site/MonCompte.php']
    shared_style = {}
    for name, text in [('before', predecessor), ('after', mon)]:
        p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '-i', '--pull', 'never', '--network', 'none', '--read-only',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777',
            '--entrypoint', 'php', 'imagine-tests-t01:1', '/opt/t01/imagine-site/vendor/bin/phpcs', '--standard=PSR12', '-n', '--report=json',
            '--stdin-path=MonCompte.php', '-'], input=text, capture_output=True, text=True, encoding='utf-8')
        assert p.returncode == 2 and not p.stderr
        shared_style[name] = json.loads(p.stdout)
    normalize = lambda report: [{k:v for k,v in m.items() if k not in {'line','column'}} for f in report['files'].values() for m in f['messages']]
    assert normalize(shared_style['before']) == normalize(shared_style['after'])
    shared_style['no_new_style_errors'] = True
    save('psr12-shared-preexisting', shared_style)
    # New C18 probe only. Existing native C18/C19 probes are byte-verified, not rewritten.
    existing = ['imagine-demo-build/c18-runtime.php', 'imagine-demo-build/c19-runtime.php']
    assert live_hashes(existing) == {n: digest(ROOT / 'wp/tests/demo' / Path(n).name) for n in existing}
    probe = ROOT / 'wp/tests/demo/c18-corrections-runtime.php'
    target = 'imagine-demo-build/' + probe.name
    c18.c17.profils.b00.upload(target, probe.read_bytes())
    assert live_hashes([target]) == {target: digest(probe)}
    runtime = c18.wp('require WP_CONTENT_DIR."/' + target + '";')
    save('runtime', runtime)
    assert runtime['total'] == len(runtime['checks']) and runtime['failures'] == []
    assert all(v is True for v in runtime['checks'].values())
    # Reuse real HTTP/browser gates, sending all NEW artifacts to this successor directory.
    c18.PROOF = PROOF
    http_result = http.run('http')
    visual_result = visual.run()
    canonical_paths = [ROOT / 'wp' / n for n in CODE] + [ROOT / 'wp/plugins/imagine-site/tests/ExtractionsNativesTest.php', ROOT / 'wp/plugins/imagine-site/tests/fixtures/c18-faux-natif.php']
    canonical_inputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in canonical_paths}
    if args.canonical:
        command(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], 'canonical')
        save('canonical-inputs', canonical_inputs)
    else:
        assert json.loads((PROOF / 'canonical-inputs.json').read_text(encoding='utf-8')) == canonical_inputs, 'Run --canonical after source changes'
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', (PROOF / 'canonical.log').read_text(encoding='utf-8'), re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    native = c18.c17.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";', check=False)
    assert not native['stderr']
    c09 = json.loads(native['stdout'])
    assert native['code'] == 0 and c09['total'] == len(c09['checks']) == 382 and c09['failures'] == []
    assert all(v is True for v in c09['checks'].values())
    native_after = c18.state()
    paper_after = action()
    assert native_before == native_after and paper_before == paper_after
    assert old == historical() and protected == protected_sources()
    readback = c18.readback()
    readback.update(live_hashes(CODE))
    csvs = {}
    for entry in http_result['exports']:
        path = PROOF / entry['csv']
        with path.open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == entry['rows']
        csvs[path.name] = {'rows': len(rows), 'sha256': digest(path), 'reopened': True}
    sources = [ROOT / 'wp' / n for n in CODE]
    sources += [ROOT / 'wp/plugins/imagine-site/tests/ExtractionsNativesTest.php', ROOT / 'wp/plugins/imagine-site/tests/fixtures/c18-faux-natif.php', Path(__file__), probe]
    result = {'at': datetime.now(timezone.utc).isoformat(), 'status': 'C18_CORRECTIONS_TECHNIQUES_VERIFIEES', 'scope': 'imagine-test-demo',
        'unit': {label: {k:v for k,v in json.loads((PROOF / (label + '.json')).read_text(encoding='utf-8')).items() if k in ['tests','assertions','exit','removed','image']} for label in ['unit-c18','unit-root']},
        'canonical': canonical, 'runtime_checks': runtime['total'], 'HTTP_checks': http_result['total'], 'CSV_reopened': csvs,
        'native_C09': {'exit': native['code'], 'total': c09['total'], 'failures': c09['failures']},
        'native_state_preserved': True, 'paper_8793_pending_subscription_101_preserved': True,
        'C19_read_only_sources_unchanged': protected, 'historical_receipts_unchanged': old,
        'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources}, 'sha256_readback': readback,
        'visual': visual_result, 'visual_approval': False, 'fixture_reset': False}
    save('final', result)
    print(json.dumps({k:result[k] for k in ['status','unit','canonical','runtime_checks','HTTP_checks','native_C09','native_state_preserved']}, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--canonical', action='store_true')
    run(parser.parse_args())
