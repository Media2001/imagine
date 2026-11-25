"""A12 dedicated replay on the read-only A02 bench; output must be external."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import uuid
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a02_runner', REPO/'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a12-content'
# Only immutable dependencies are invariance gates; A10/A11 have concurrent owners.
PROTECTED = ['wp/tests/a02-audit', 'wp/outils/bascule/audit', 'wp/outils/bascule/a11', 'wp/tests/a11']

def manifest(roots):
    files = []
    for key in roots:
        root = REPO/key
        files.extend([root] if root.is_file() else [p for p in root.rglob('*') if p.is_file()])
    return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if '__pycache__' not in p.parts}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=pathlib.Path, required=True)
    ap.add_argument('--unit-only', action='store_true')
    args = ap.parse_args()
    out = args.output.resolve()
    if out == REPO or REPO in out.parents:
        raise SystemExit('A12 evidence must be generated outside the repository')
    out.mkdir(parents=True, exist_ok=False)
    run_id = uuid.uuid4().hex[:12]
    name = 'imagine-a12-content-' + run_id
    owned = manifest(['wp/tests/a12', 'wp/outils/bascule/a12'])
    protected = manifest(PROTECTED)
    receipt = {'suite': 'A12-owned-runner', 'container': name, 'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'mode': 'unit' if args.unit_only else 'native', 'checks': [], 'exit_code': 1}
    created = False
    def record(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    try:
        image = json.loads(b.call(['image', 'inspect', b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create', '--name', name, '--label', b.LABEL+'='+name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none', '--pull', 'never', '--entrypoint', 'sleep', b.IMAGE, 'infinity'])
        created = True
        record('isolation_before', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
        b.call(['start', name])
        b.call(['exec', name, 'mkdir', '-p', '/subject/a12', '/opt/a12', '/opt/a02', '/report'])
        for root, dest in [(HERE, '/opt/a12'), (REPO/'wp/outils/bascule/a12', '/subject/a12')]:
            for p in sorted(root.glob('*')):
                if p.is_file(): b.call(['cp', b.local(p), name+':'+dest+'/'+p.name])
        b.call(['cp', b.local(REPO/'wp/outils/bascule/audit'), name+':/subject/audit'])
        b.call(['cp', b.local(REPO/'wp/outils/bascule/a11'), name+':/subject/a11'])
        unit = b.call(['exec', name, 'php', '/opt/a12/unit.php'], check=False)
        (out/'unit.log').write_text(unit.stdout+unit.stderr, encoding='utf8')
        b.call(['cp', name+':/report/unit.json', b.local(out/'unit.json')])
        record('unit_return', unit.returncode == 0, {'exit_code': unit.returncode})
        if not args.unit_only:
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(REPO/'wp/tests/a02-audit'/f), name+':/opt/a02/'+f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/'+f, name+':/opt/a02/'+f])
            p = b.call(['exec', name, 'python3', '/opt/a12/inside.py'], check=False, timeout=1500)
            (out/'native.log').write_text(p.stdout+p.stderr, encoding='utf8')
            b.call(['cp', name+':/report/.', b.local(out)])
            inner = json.loads((out/'result.json').read_text())
            record('native_return', p.returncode == 0 and inner['exit_code'] == 0, {'exit_code': p.returncode})
        record('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as exc:
        record('exception', False, {'class': type(exc).__name__, 'code': str(exc)[:180]})
    finally:
        if created:
            try:
                info = json.loads(b.call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/'+name and info['Config']['Labels'].get(b.LABEL) == name
                b.call(['rm', '-f', name])
                missing = b.call(['inspect', name], check=False)
                record('cleanup_exact_owned_runner', missing.returncode != 0 and bool(re.search(r'no such (object|container)', missing.stderr, re.I)))
            except Exception as exc:
                record('cleanup_exact_owned_runner', False, {'class': type(exc).__name__})
        record('owned_sources_stable', owned == manifest(['wp/tests/a12', 'wp/outils/bascule/a12']))
        record('protected_sources_unchanged', protected == manifest(PROTECTED))
        receipt['exit_code'] = int(any(x['status'] != 'PASS' for x in receipt['checks']))
        (out/'sources.json').write_text(json.dumps(owned, indent=2)+'\n', encoding='utf8')
        (out/'protected-sources.json').write_text(json.dumps(protected, indent=2)+'\n', encoding='utf8')
        (out/'runner.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
        print(json.dumps({'evidence': str(out), **receipt}, indent=2))
    return receipt['exit_code']

if __name__ == '__main__':
    sys.exit(main())
