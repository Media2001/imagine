"""A24 offline owned runner: only exact owned disposable containers."""
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
spec = importlib.util.spec_from_file_location('a24_a02_runner', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a24-addresses'
OWN = ['wp/outils/bascule/a24', 'wp/tests/a24']
DEPS = ['wp/outils/bascule/' + f for f in ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']] + [
    'wp/tests/a02-audit/' + f for f in ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
] + ['wp/outils/staging']


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--unit-only', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    if out == ROOT or out.is_relative_to(ROOT):
        raise RuntimeError('A24_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a24-addresses-' + uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A24-owned-runner', 'container': name, 'image': b.IMAGE,
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
        b.call(['exec', name, 'mkdir', '-p', '/subject/a24', '/opt/a24', '/opt/a02', '/report'])
        for source, target in [(HERE, '/opt/a24'), (ROOT / 'wp/outils/bascule/a24', '/subject/a24')]:
            for p in sorted(source.iterdir()):
                if p.is_file():
                    b.call(['cp', b.local(p), name + ':' + target + '/' + p.name])
        if not args.unit_only:
            for key in ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']:
                b.call(['cp', b.local(ROOT / 'wp/outils/bascule' / key), name + ':/subject/' + key])
            b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/staging'])
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
        lint_checks = []
        for source, target in [(HERE, '/opt/a24'), (ROOT / 'wp/outils/bascule/a24', '/subject/a24')]:
            for file in sorted(source.iterdir()):
                if file.is_file() and (file.suffix == '.php' or file.name == 'inventorier-expedition'):
                    lint = b.call(['exec', name, 'php', '-l', target + '/' + file.name], check=False)
                    lint_checks.append({'check': target + '/' + file.name,
                                        'status': 'PASS' if lint.returncode == 0 and not lint.stderr else 'FAIL'})
        lint_receipt = {'suite': 'A24-owned-PHP-lint', 'checks': lint_checks,
                        'exit_code': int(not lint_checks or any(c['status'] != 'PASS' for c in lint_checks))}
        (out / 'lint.json').write_text(json.dumps(lint_receipt, indent=2) + '\n', encoding='utf-8')
        check('lint_all_owned_php', lint_receipt['exit_code'] == 0)
        p = b.call(['exec', name, 'php', '/opt/a24/unit.php'], check=False)
        (out / 'unit.log').write_text(p.stdout + p.stderr, encoding='utf-8')
        check('unit_return', p.returncode == 0)
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')], check=False)
        pure = b.call(['exec', '-e', 'A24_PURE_PROBE=1', name, 'php', '-n', '-d',
                       'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                       '/opt/a24/unit.php'], check=False)
        (out / 'pure.log').write_text(pure.stdout + pure.stderr, encoding='utf-8')
        check('pure_no_extensions_no_writes', pure.returncode == 0 and pure.stderr == '' and pure.stdout == p.stdout)
        if not args.unit_only and p.returncode == 0:
            p = b.call(['exec', name, 'python3', '/opt/a24/inside.py'], check=False, timeout=1800)
            (out / 'native.log').write_text(p.stdout + p.stderr, encoding='utf-8')
            b.call(['cp', name + ':/report/.', b.local(out)])
            check('native_return', p.returncode == 0)
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        check('exception', False, {'class': type(error).__name__, 'code': str(error)[:100]})
    finally:
        if created:
            try:
                info = json.loads(b.call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
                b.call(['rm', '-f', name])
                missing = b.call(['inspect', name], check=False)
                check('cleanup_exact_owned_container', missing.returncode != 0 and re.search(
                    'no such (object|container)', missing.stderr, re.I) is not None)
            except Exception as error:
                check('cleanup_exact_owned_container', False, {'class': type(error).__name__})
        check('owned_sources_stable', owned == manifest(OWN))
        check('dependencies_stable', deps == manifest(DEPS))
        receipt['exit_code'] = int(any(x['status'] != 'PASS' for x in receipt['checks']))
        for filename, data in [('runner.json', receipt), ('sources.json', owned), ('dependencies.json', deps)]:
            (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
