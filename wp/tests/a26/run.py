"""Owned offline A26 fixture. PHP runs only in disposable containers."""
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
b.LABEL = 'org.imagine.a26-tiers'
OWN = ['wp/outils/bascule/a26', 'wp/tests/a26']
DEPS = ['wp/outils/bascule/' + f for f in ['audit', 'a11', 'a12', 'a16/Mapping.php', 'stream_guard.py', 'stream_refusals.json']] + [
    'wp/tests/a02-audit/' + f for f in ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
] + ['wp/outils/staging', 'wp/outils/staging/form-policy.json', 'production/A-26/readme-ajout.txt',
     'production/A-26/standard/html-tag-processor-sources.json',
     'production/A-26/standard/sources.json', 'production/A-26/standard/sitekit_settings.txt']


def manifest(roots):
    files = []
    for key in roots:
        p = ROOT / key
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            entries = [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
            if not entries:
                raise RuntimeError('A26_EMPTY_SOURCE_ROOT')
            files.extend(entries)
        else:
            raise RuntimeError('A26_MISSING_SOURCE_ROOT')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT):
        raise RuntimeError('A26_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a26-tiers-' + uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A26-owned-runner', 'container': name,
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
        b.call(['exec', name, 'mkdir', '-p', '/subject/a26', '/opt/a26', '/opt/a02', '/report'])
        for source, dest in [(HERE, '/opt/a26'), (ROOT / 'wp/outils/bascule/a26', '/subject/a26')]:
            if source.exists():
                for p in sorted(source.iterdir()):
                    if p.is_file():
                        b.call(['cp', b.local(p), name + ':' + dest + '/' + p.name])
        if not a.unit_only:
            for key in ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']:
                p = ROOT / 'wp/outils/bascule' / key
                if p.exists():
                    b.call(['cp', b.local(p), name + ':/subject/' + key])
            b.call(['exec', name, 'mkdir', '-p', '/subject/a16'])
            b.call(['cp', b.local(ROOT / 'wp/outils/bascule/a16/Mapping.php'), name + ':/subject/a16/Mapping.php'])
            b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/staging'])
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
        lint_files = sorted((ROOT / 'wp/outils/bascule/a26').glob('*.php')) + sorted(HERE.glob('*.php'))
        lint_targets = ['/subject/a26/' + p.name for p in lint_files if p.parent != HERE] + ['/opt/a26/' + p.name for p in lint_files if p.parent == HERE] + ['/subject/a26/inventorier-tiers']
        for target in lint_targets:
            lint = b.call(['exec', name, 'php', '-l', target], check=False)
            check('lint:' + Path(target).name, lint.returncode == 0 and lint.stderr == '')
        rg = b.call(['exec', name, 'python3', '/opt/a26/red_green.py'], check=False)
        (out / 'red-green.log').write_text(rg.stdout + rg.stderr, encoding='utf-8')
        check('php_red_green_return', rg.returncode == 0)
        b.call(['cp', name + ':/report/red-green.json', b.local(out / 'red-green.json')], check=False)
        b.call(['cp', name + ':/report/red-unit.json', b.local(out / 'red-unit.json')], check=False)
        p = b.call(['exec', name, 'php', '/opt/a26/unit.php'], check=False)
        (out / 'unit.log').write_text(p.stdout + p.stderr, encoding='utf-8')
        check('unit_return', p.returncode == 0)
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')], check=False)
        pure = b.call(['exec', name, 'php', '-n', '-d',
                       'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                       '/opt/a26/pure-probe.php'], check=False)
        (out / 'pure.log').write_text(pure.stdout + pure.stderr, encoding='utf-8')
        unit_count = len(json.loads((out / 'unit.json').read_text(encoding='utf-8'))['checks'])
        check('pure_inclusion_no_extensions_no_writes', pure.returncode == 0 and pure.stderr == ''
              and pure.stdout == 'A26_PURE_OK ' + str(unit_count) + '\n')
        if not a.unit_only and p.returncode == 0:
            standard = b.call(['exec', name, 'php', '/opt/a26/standard.php'], check=False)
            (out / 'standard.log').write_text(standard.stdout + standard.stderr, encoding='utf-8')
            check('installed_standard', standard.returncode == 0 and standard.stdout == standard.stderr == '')
            b.call(['cp', name + ':/report/standard.json', b.local(out / 'standard.json')])
            p = b.call(['exec', name, 'python3', '/opt/a26/inside.py'], check=False, timeout=1500)
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
