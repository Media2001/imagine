"""Parent-only A30 offline runner. No host PHP; never invokes on import."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a30_a02_transport', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a30-dry-run'
OWN = ['wp/outils/bascule/a30', 'wp/tests/a30']
BASCULE_DEPS = ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json', 'controler-export', 'a13']
A02_FILES = ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
FIXTURES = ['a13-export-propre-fictif.csv', 'a13-export-defauts-fictif.csv', 'a13-export-iban-fictif.csv']
DEPS = ['wp/outils/bascule/' + f for f in BASCULE_DEPS] + ['wp/outils/staging'] + [
    'wp/tests/a02-audit/' + f for f in A02_FILES] + ['wp/tests/fixtures/' + f for f in FIXTURES]


def manifest(roots):
    files = []
    for key in roots:
        path = ROOT / key
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    args = ap.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT / 'production/A-30/preuves'):
        raise RuntimeError('A30_OUTPUT_UNSAFE')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a30-dry-run-' + uuid.uuid4().hex[:12]
    own, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A30-owned-runner', 'container': name, 'mode': 'unit' if args.unit_only else 'full',
               'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': [], 'exit_code': 1}
    created = False

    def check(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

    try:
        image = json.loads(b.call(['image', 'inspect', b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create', '--name', name, '--label', b.LABEL + '=' + name, '--network', 'none',
                '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none',
                '--pull', 'never', '--entrypoint', 'sleep', b.IMAGE, 'infinity'])
        created = True
        check('isolation_before', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
        b.call(['start', name])
        b.call(['exec', name, 'mkdir', '-p', '/subject/a30', '/opt/a30/fixtures', '/opt/a02', '/report'])
        for source, dest in [(HERE, '/opt/a30'), (ROOT / 'wp/outils/bascule/a30', '/subject/a30')]:
            for path in sorted(source.iterdir()):
                if path.is_file():
                    b.call(['cp', b.local(path), name + ':' + dest + '/' + path.name])
        if not args.unit_only:
            for key in BASCULE_DEPS:
                b.call(['cp', b.local(ROOT / 'wp/outils/bascule' / key), name + ':/subject/' + key])
            b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/staging'])
            for filename in A02_FILES:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / filename), name + ':/opt/a02/' + filename])
            for filename in FIXTURES:
                b.call(['cp', b.local(ROOT / 'wp/tests/fixtures' / filename), name + ':/opt/a30/fixtures/' + filename])
            for filename in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + filename, name + ':/opt/a02/' + filename])
        # Syntax and pure tests are prepared; these execute only on the parent's GO.
        for path in sorted((ROOT / 'wp/outils/bascule/a30').glob('*.php')):
            p = b.call(['exec', name, 'php', '-l', '/subject/a30/' + path.name], check=False)
            check('lint:' + path.name, p.returncode == 0)
        unit = b.call(['exec', name, 'php', '/opt/a30/unit.php'], check=False)
        check('unit_return', unit.returncode == 0 and unit.stdout == unit.stderr == '')
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')], check=False)
        pure = b.call(['exec', '-e', 'A30_PURE=1', name, 'php', '-n', '-d',
                       'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                       '/opt/a30/unit.php'], check=False)
        check('pure_no_extensions_no_writes', (pure.returncode, pure.stdout, pure.stderr) == (0, 'A30_PURE_OK 7\n', ''))
        if not args.unit_only and unit.returncode == 0:
            native = b.call(['exec', name, 'python3', '/opt/a30/inside.py'], check=False, timeout=1500)
            check('native_return', native.returncode == 0)
            b.call(['cp', name + ':/report/.', b.local(out)])
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        check('exception', False, {'class': type(error).__name__})
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            missing = b.call(['inspect', name], check=False)
            check('cleanup_exact_owned_container', missing.returncode != 0 and re.search('no such (object|container)', missing.stderr, re.I) is not None)
        check('owned_sources_stable', own == manifest(OWN))
        check('dependencies_stable', deps == manifest(DEPS))
        receipt['exit_code'] = int(any(row['status'] != 'PASS' for row in receipt['checks']))
        for filename, data in [('runner.json', receipt), ('sources.json', own), ('dependencies.json', deps)]:
            (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'exit_code': receipt['exit_code'], 'checks': receipt['checks']}, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
