"""Owned offline A23 fixture. PHP runs only in disposable containers."""
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
spec = importlib.util.spec_from_file_location('a02_runner', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a23-readers'
OWN = ['wp/outils/bascule/a23', 'wp/tests/a23']
DEPS = ['wp/outils/bascule/' + f for f in ['audit', 'a11', 'a12', 'a17/Inventory.php', 'stream_guard.py', 'stream_refusals.json']] + [
    'wp/tests/a02-audit/' + f for f in ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
] + ['wp/outils/staging']


def manifest(roots):
    files = []
    for key in roots:
        p = ROOT / key
        if p.is_file():
            files.append(p)
        elif p.exists():
            files.extend(f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT):
        raise RuntimeError('A23_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a23-readers-' + uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A23-owned-runner', 'container': name,
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
        b.call(['exec', name, 'mkdir', '-p', '/subject/a23', '/opt/a23', '/opt/a02', '/report'])
        for source, dest in [(HERE, '/opt/a23'), (ROOT / 'wp/outils/bascule/a23', '/subject/a23')]:
            if source.exists():
                for p in sorted(source.iterdir()):
                    if p.is_file():
                        b.call(['cp', b.local(p), name + ':' + dest + '/' + p.name])
        b.call(['exec', name, 'mkdir', '-p', '/subject/a17'])
        b.call(['cp', b.local(ROOT / 'wp/outils/bascule/a17/Inventory.php'), name + ':/subject/a17/Inventory.php'])
        if not a.unit_only:
            for key in ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']:
                p = ROOT / 'wp/outils/bascule' / key
                if p.exists():
                    b.call(['cp', b.local(p), name + ':/subject/' + key])
            b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/staging'])
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
        p = b.call(['exec', name, 'php', '/opt/a23/unit.php'], check=False)
        (out / 'unit.log').write_text(p.stdout + p.stderr, encoding='utf-8')
        check('unit_return', p.returncode == 0)
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')], check=False)
        pure = b.call(['exec', name, 'php', '-n', '-d',
                       'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                       '/opt/a23/pure-probe.php'], check=False)
        (out / 'pure.log').write_text(pure.stdout + pure.stderr, encoding='utf-8')
        unit_count = len(json.loads((out / 'unit.json').read_text(encoding='utf-8'))['checks'])
        check('pure_inclusion_no_extensions_no_writes', pure.returncode == 0 and pure.stderr == ''
              and pure.stdout == 'A23_PURE_OK ' + str(unit_count) + '\n')
        roles = b.call(['exec', name, 'php', '-d',
                        'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                        '/opt/a23/role-probe.php'], check=False)
        (out / 'role-definitions.log').write_text(roles.stdout + roles.stderr, encoding='utf-8')
        role_receipt = json.loads(roles.stdout)
        (out / 'role-definitions.json').write_text(json.dumps(role_receipt, indent=2) + '\n', encoding='utf-8')
        check('role_definitions_pure', roles.returncode == 0 and roles.stderr == ''
              and role_receipt['exit_code'] == 0 and bool(role_receipt['checks'])
              and all(row['status'] == 'PASS' for row in role_receipt['checks']))
        if not a.unit_only and p.returncode == 0:
            standard = b.call(['exec', name, 'php', '/opt/a23/standard.php'], check=False)
            (out / 'standard.log').write_text(standard.stdout + standard.stderr, encoding='utf-8')
            check('installed_standard', standard.returncode == 0 and standard.stdout == standard.stderr == '')
            b.call(['cp', name + ':/report/standard.json', b.local(out / 'standard.json')])
            p = b.call(['exec', name, 'python3', '/opt/a23/inside.py'], check=False, timeout=1500)
            (out / 'native.log').write_text(p.stdout + p.stderr, encoding='utf-8')
            b.call(['cp', name + ':/report/.', b.local(out)])
            check('native_return', p.returncode == 0)
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        check('exception', False, {'class': type(error).__name__, 'code': str(error)[:100]})
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            missing = b.call(['inspect', name], check=False)
            check('cleanup_exact_owned_container', missing.returncode != 0 and re.search('no such (object|container)', missing.stderr, re.I) is not None)
        check('owned_sources_stable', owned == manifest(OWN))
        check('dependencies_stable', deps == manifest(DEPS))
        receipt['exit_code'] = int(any(x['status'] != 'PASS' for x in receipt['checks']))
        for filename, data in [('runner.json', receipt), ('sources.json', owned), ('dependencies.json', deps)]:
            (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
