"""A-02: owned offline fixture, no site input, no downloads, no host PHP."""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SUBJECT = REPO / 'wp/outils/bascule/audit'
IMAGE = 'sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2'
LABEL = 'org.imagine.a02-audit'
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
LICENSED = {
    'woocommerce-subscriptions.zip': 'ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083',
    'woocommerce-memberships.zip': 'd3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285',
}

def local(path):
    text = str(path).replace('\\', '/')
    return '/mnt/' + text[0].lower() + text[2:] if re.match(r'^[A-Za-z]:/', text) else text

def call(args, check=True, timeout=180, input_text=None):
    p = subprocess.run(DOCKER + args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, input=input_text)
    if check and p.returncode:
        raise RuntimeError('DOCKER_' + args[0].upper() + '_FAILED:' + str(p.returncode))
    return p

def validate(info, name):
    assert info['Name'] == '/' + name
    assert info['Config']['Labels'].get(LABEL) == name
    h = info['HostConfig']
    assert h['NetworkMode'] == 'none' and not h['Privileged']
    assert not info['Mounts'] and not h.get('Binds')
    assert not h.get('PortBindings') and not info['Config'].get('ExposedPorts')
    assert not info['NetworkSettings'].get('Ports')
    assert not (set(info['NetworkSettings'].get('Networks', {})) - {'none'})
    assert 'ALL' in h['CapDrop'] and any(s.startswith('no-new-privileges') for s in h['SecurityOpt'])
    return {'network': 'none', 'mounts': [], 'ports': [], 'privileged': False, 'cap_drop': ['ALL'], 'no_new_privileges': True, 'image_id': info['Image']}

def manifest():
    files = [p for p in ROOT.iterdir() if p.is_file()] + ([SUBJECT] if SUBJECT.exists() else [])
    return {str(p.relative_to(REPO)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit-only', action='store_true')
    args = parser.parse_args()
    run_id = uuid.uuid4().hex[:12]
    name = 'imagine-a02-audit-' + run_id
    out = REPO / 'production/A-02/preuves' / run_id
    out.mkdir(parents=True, exist_ok=False)
    receipt = {'run_id': run_id, 'container': name, 'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'mode': 'unit' if args.unit_only else 'full', 'exit_code': 1, 'checks': []}
    created = False
    initial = manifest()
    (out / 'sources.json').write_text(json.dumps(initial, indent=2) + '\n', encoding='utf8')
    def record(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    try:
        image = json.loads(call(['image', 'inspect', IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        call(['create', '--name', name, '--label', LABEL + '=' + name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none', '--pull', 'never', '--entrypoint', '/bin/sleep', IMAGE, 'infinity'])
        created = True
        record('isolation_before_input', True, validate(json.loads(call(['inspect', name]).stdout)[0], name))
        call(['start', name]); call(['exec', name, 'mkdir', '-p', '/subject', '/opt/a02', '/report'])
        for file in ['unit.php'] + ([] if args.unit_only else ['inside.py', 'seed.php', 'fingerprint.php', 'readonly-probe.php']):
            call(['cp', local(ROOT / file), name + ':/opt/a02/' + file])
        if SUBJECT.exists():
            call(['cp', local(SUBJECT), name + ':/subject/audit'])
        if not args.unit_only:
            for file in LICENSED:
                call(['cp', '/home/ced/staging-wp/plugins/' + file, name + ':/opt/a02/' + file])
        record('sources_stable_at_copy', manifest() == initial)
        unit = call(['exec', name, 'php', '/opt/a02/unit.php'], check=False)
        (out / 'unit.log').write_text(unit.stdout + unit.stderr, encoding='utf8')
        call(['cp', name + ':/report/unit.json', local(out / 'unit.json')])
        record('unit_return', unit.returncode == 0, {'exit_code': unit.returncode})
        if not args.unit_only and unit.returncode == 0:
            p = call(['exec', name, 'python3', '/opt/a02/inside.py'], check=False, timeout=1500)
            (out / 'execution.log').write_text(p.stdout + p.stderr, encoding='utf8')
            call(['cp', name + ':/report/.', local(out)])
            inner = json.loads((out / 'result.json').read_text())
            record('inner_receipt', p.returncode == 0 and inner['exit_code'] == 0 and bool(inner['checks']), {'exit_code': p.returncode})
        record('isolation_after_execution', True, validate(json.loads(call(['inspect', name]).stdout)[0], name))
    except Exception as exc:
        record('exception', False, {'class': type(exc).__name__, 'code': str(exc)[:180]})
    finally:
        if created:
            try:
                info = json.loads(call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/' + name and info['Config']['Labels'].get(LABEL) == name
                call(['rm', '-f', name])
                missing = call(['inspect', name], check=False)
                record('cleanup', missing.returncode != 0 and re.search(r'no such (object|container)', missing.stderr, re.I) is not None, {'absent': missing.returncode != 0})
            except Exception as exc:
                record('cleanup', False, {'class': type(exc).__name__})
        record('sources_unchanged', initial == manifest())
        receipt['exit_code'] = int(any(c['status'] != 'PASS' for c in receipt['checks']))
        (out / 'runner.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
        actual = json.loads((out / 'runner.json').read_text())
        print(json.dumps({'evidence': str(out), 'exit_code': actual['exit_code'], 'checks': actual['checks']}, indent=2))
    return receipt['exit_code']

if __name__ == '__main__':
    sys.exit(main())
