"""A33 owned disconnected runner. No archive/site arguments, no host PHP."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a02runner', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a33-archives'
OWN = ['wp/outils/bascule/a33', 'wp/tests/a33', 'production/A-33/verify.py', 'production/A-33/rejeu.json', 'production/A-33/readme-ajout.txt', 'production/A-33/STANDARD.md', 'production/A-33/LIVRAISON.md']
SHARED = ['audit', 'a11', 'a12', 'a16', 'stream_guard.py', 'stream_refusals.json']
DEPS = ['wp/outils/bascule/' + f for f in SHARED] + ['wp/outils/staging', 'wp/outils/staging-court', 'wp/tests/t01', 'wp/tests/rejouer.ps1', 'wp/tests/preparer-image.ps1', 'wp/tests/a02-audit']


def manifest(roots):
    result = {}
    for r in roots:
        p = ROOT / r
        for f in ([p] if p.is_file() else p.rglob('*')):
            if f.is_file() and '__pycache__' not in f.parts:
                result[f.relative_to(ROOT).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    ap.add_argument('--parent-serialized', action='store_true', required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A33_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a33-archives-' + uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A33-owned-runner', 'container': name, 'checks': [], 'exit_code': 1}
    created = False

    def check(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
        if not ok:
            raise RuntimeError('A33_RUNNER_GATE')

    try:
        image = json.loads(b.call(['image', 'inspect', b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create', '--name', name, '--label', b.LABEL + '=' + name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none', '--pull', 'never', '--entrypoint', 'sleep', b.IMAGE, 'infinity'])
        created = True
        check('isolation_before', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
        b.call(['start', name])
        b.call(['exec', name, 'mkdir', '-p', '/subject/a33', '/opt/a33', '/opt/a02', '/report'])
        for source, dest in [(HERE, '/opt/a33'), (ROOT / 'wp/outils/bascule/a33', '/subject/a33')]:
            for p in sorted(source.iterdir()):
                if p.is_file():
                    b.call(['cp', b.local(p), name + ':' + dest + '/' + p.name])
        for key in SHARED:
            b.call(['cp', b.local(ROOT / 'wp/outils/bascule' / key), name + ':/subject/' + key])
        unit = b.call(['exec', name, 'php', '/opt/a33/unit.php'], check=False)
        (out / 'unit.log').write_text(unit.stdout + unit.stderr, encoding='utf-8')
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')])
        check('unit_green', unit.returncode == 0 and not unit.stderr and json.loads((out / 'unit.json').read_bytes())['exit_code'] == 0)
        if not a.unit_only:
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
            p = b.call(['exec', name, 'python3', '/opt/a33/inside.py'], check=False, timeout=1500)
            (out / 'native.log').write_text(p.stdout + p.stderr, encoding='utf-8')
            b.call(['cp', name + ':/report/.', b.local(out)])
            inner = json.loads((out / 'result.json').read_bytes())
            check('native_green', p.returncode == 0 and inner['exit_code'] == 0 and bool(inner['checks']))
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        receipt['checks'].append({'check': 'exception', 'status': 'FAIL', 'detail': {'class': type(error).__name__, 'code': str(error)}})
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            missing = b.call(['inspect', name], check=False)
            check('cleanup_exact_owned_container', missing.returncode != 0 and re.search('no such (object|container)', missing.stderr, re.I) is not None)
        for key, ok in [('owned_sources_stable', owned == manifest(OWN)), ('dependencies_stable', deps == manifest(DEPS))]:
            receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL'})
        receipt['exit_code'] = int(any(c['status'] != 'PASS' for c in receipt['checks']))
        for filename, data in [('runner.json', receipt), ('sources.json', owned), ('dependencies.json', deps)]:
            (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
