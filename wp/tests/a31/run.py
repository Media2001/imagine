"""PARENT ONLY: disposable disconnected A31 fixture, no host PHP or downloads."""
import argparse
import datetime
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
spec = importlib.util.spec_from_file_location('a02_runner', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a31-history'
OWN = ['wp/outils/bascule/a31', 'wp/tests/a31', 'production/A-31/verify.py',
       'production/A-31/rejeu.json', 'production/A-31/readme-ajout.txt']
SHARED = ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']
DEPS = ['wp/outils/bascule/' + f for f in SHARED] + [
    'wp/tests/a02-audit/' + f for f in ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
] + ['wp/outils/staging', 'wp/outils/staging-court', 'wp/outils/bascule/a19/Analysis.php',
     'production/A-28/preuves/final/dependency-invalidations.json']


def manifest(roots):
    files = []
    for key in roots:
        p = ROOT / key
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            entries = [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts]
            if not entries:
                raise RuntimeError('A31_EMPTY_SOURCE_ROOT')
            files.extend(entries)
        else:
            raise RuntimeError('A31_MISSING_SOURCE_ROOT')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    ap.add_argument('--parent-serialized', action='store_true', required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A31_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a31-history-' + uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPS)
    receipt = {'suite': 'A31-owned-runner', 'container': name,
               'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': [], 'exit_code': 1}
    created = False

    def check(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
        if not ok:
            raise RuntimeError('A31_PARENT_GATE_FAILED')

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
        b.call(['exec', name, 'mkdir', '-p', '/subject/a31', '/opt/a31', '/opt/a02', '/report'])
        for source, dest in [(HERE, '/opt/a31'), (ROOT / 'wp/outils/bascule/a31', '/subject/a31')]:
            for p in sorted(source.iterdir()):
                if p.is_file():
                    b.call(['cp', b.local(p), name + ':' + dest + '/' + p.name])
        if not a.unit_only:
            for key in SHARED:
                b.call(['cp', b.local(ROOT / 'wp/outils/bascule' / key), name + ':/subject/' + key])
            b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/staging'])
            for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
                b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
            for f in b.LICENSED:
                b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
        for f in ['Analysis.php', 'Inventory.php', 'Command.php', 'inventorier-commandes']:
            p = b.call(['exec', name, 'php', '-l', '/subject/a31/' + f], check=False)
            check('lint_' + f, p.returncode == 0)
        # Red witness is deliberately confined to the disposable copied PHP source.
        mutation = "from pathlib import Path;p=Path('/subject/a31/Analysis.php');s=p.read_text(encoding='utf-8');p.with_suffix('.original').write_text(s,encoding='utf-8');assert s.count(\"$row['count'] < 5\")==1;p.write_text(s.replace(\"$row['count'] < 5\",\"$row['count'] < 6\"),encoding='utf-8')"
        b.call(['exec', name, 'python3', '-c', mutation])
        red = b.call(['exec', name, 'php', '/opt/a31/unit.php'], check=False)
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'red-unit.json')])
        b.call(['exec', name, 'python3', '-c', "from pathlib import Path;p=Path('/subject/a31/Analysis.php');q=p.with_suffix('.original');p.write_bytes(q.read_bytes());q.unlink()"])
        red_data = json.loads((out / 'red-unit.json').read_text(encoding='utf-8'))
        check('red_mutation_k5_caught', red.returncode == 1 and any(
            x['check'] == 'renewal_five' and x['status'] == 'FAIL' for x in red_data['checks']))
        adapter = b.call(['exec', name, 'php', '/opt/a31/adapter-unit.php'], check=False)
        (out / 'adapter-unit.log').write_text(adapter.stdout + adapter.stderr, encoding='utf-8')
        b.call(['cp', name + ':/report/adapter-unit.json', b.local(out / 'adapter-unit.json')])
        adapter_data = json.loads((out / 'adapter-unit.json').read_text(encoding='utf-8'))
        check('adapter_native_relation_boundary_green', adapter.returncode == 0 and not adapter.stderr
              and adapter_data['exit_code'] == 0 and bool(adapter_data['checks']))
        p = b.call(['exec', name, 'php', '/opt/a31/unit.php'], check=False)
        (out / 'unit.log').write_text(p.stdout + p.stderr, encoding='utf-8')
        b.call(['cp', name + ':/report/unit.json', b.local(out / 'unit.json')])
        unit = json.loads((out / 'unit.json').read_text(encoding='utf-8'))
        check('unit_green', p.returncode == 0 and unit['exit_code'] == 0 and bool(unit['checks']))
        pure = b.call(['exec', name, 'php', '-n', '-d',
                       'disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open',
                       '/opt/a31/pure-probe.php'], check=False)
        (out / 'pure.log').write_text(pure.stdout + pure.stderr, encoding='utf-8')
        check('pure_no_extensions_no_writes', (pure.returncode, pure.stdout, pure.stderr)
              == (0, 'A31_PURE_OK ' + str(len(unit['checks'])) + '\n', ''))
        if not a.unit_only:
            p = b.call(['exec', name, 'python3', '/opt/a31/inside.py'], check=False, timeout=1500)
            (out / 'native.log').write_text(p.stdout + p.stderr, encoding='utf-8')
            b.call(['cp', name + ':/report/.', b.local(out)])
            inner = json.loads((out / 'result.json').read_text(encoding='utf-8'))
            check('native_green', p.returncode == 0 and inner['exit_code'] == 0 and bool(inner['checks']))
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        receipt['checks'].append({'check': 'exception', 'status': 'FAIL', 'detail': {'class': type(error).__name__}})
    finally:
        if created:
            try:
                info = json.loads(b.call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
                b.call(['rm', '-f', name])
                missing = b.call(['inspect', name], check=False)
                check('cleanup_exact_owned_container', missing.returncode != 0 and re.search('no such (object|container)', missing.stderr, re.I) is not None)
            except Exception as error:
                receipt['checks'].append({'check': 'cleanup', 'status': 'FAIL', 'detail': {'class': type(error).__name__}})
        for key, ok in [('owned_sources_stable', owned == manifest(OWN)), ('dependencies_stable', deps == manifest(DEPS))]:
            receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': None})
        receipt['exit_code'] = int(any(x['status'] != 'PASS' for x in receipt['checks']))
        for filename, data in [('runner.json', receipt), ('sources.json', owned), ('dependencies.json', deps)]:
            (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
