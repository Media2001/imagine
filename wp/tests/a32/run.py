"""A32 owned synthetic bench; imported A02 source is never edited."""
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
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources():
    roots = json.loads((ROOT / 'production/A-32/source-roots.json').read_bytes())['matrix']
    assert 'wp/outils/bascule' not in roots
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for key in roots for base in [ROOT / key] for p in ([base] if base.is_file() else sorted(base.rglob('*')))
            if p.is_file() and '__pycache__' not in p.parts}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out)
    out.mkdir(parents=True, exist_ok=False)
    baseline = sources()
    b = load('a32_bench', ROOT / 'wp/tests/a02-audit/run.py')
    b.LABEL = 'org.imagine.a32-tournee'
    original_call = b.call
    ledger = []
    def traced(args, **kw):
        p = original_call(args, **{**kw, 'check': False})
        ledger.append({'command': args, 'exit_code': p.returncode, 'stderr': p.stderr if p.returncode else ''})
        if kw.get('check', True) and p.returncode:
            raise RuntimeError('A32_BENCH_COMMAND_' + str(len(ledger)))
        return p
    b.call = traced
    name = 'imagine-a32-tournee-' + uuid.uuid4().hex[:12]
    checks = []
    created = False
    def check(key, ok, detail=None):
        checks.append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    try:
        image = json.loads(b.call(['image', 'inspect', b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create', '--name', name, '--label', b.LABEL + '=' + name, '--network', 'none',
                '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                '--pids-limit', '256', '--memory', '2048m', '--cpus', '2', '--log-driver', 'none',
                '--pull', 'never', '--entrypoint', 'sleep', b.IMAGE, 'infinity'])
        created = True
        check('isolation_before', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
        b.call(['start', name])
        b.call(['exec', name, 'mkdir', '-p', '/subject/wp/outils', '/opt/a02', '/opt/a32', '/report'])
        b.call(['cp', b.local(ROOT / 'wp/outils/bascule'), name + ':/subject/wp/outils/bascule'])
        # The frozen audit runtime's canonical relative staging dependency.
        b.call(['cp', b.local(ROOT / 'wp/outils/staging'), name + ':/subject/wp/outils/staging'])
        b.call(['cp', b.local(ROOT / 'wp/outils/bascule/audit'), name + ':/subject/audit'])
        for f in ['inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']:
            b.call(['cp', b.local(ROOT / 'wp/tests/a02-audit' / f), name + ':/opt/a02/' + f])
        b.call(['cp', b.local(ROOT / 'wp/tests/a16/seed.php'), name + ':/opt/a32/seed16.php'])
        for f in ['inside.py', 'clock_seed.php']:
            b.call(['cp', b.local(HERE / f), name + ':/opt/a32/' + f])
        for f in b.LICENSED:
            b.call(['cp', '/home/ced/staging-wp/plugins/' + f, name + ':/opt/a02/' + f])
        b.call(['exec', '--user', '1000:1000', name, 'chmod', '-R', 'a-w', '/subject/wp/outils/bascule', '/subject/wp/outils/staging', '/subject/audit'])
        check('sources_stable_at_copy', baseline == sources())
        p = b.call(['exec', name, 'python3', '/opt/a32/inside.py'], check=False, timeout=4500)
        (out / 'native.log').write_text(p.stdout + p.stderr, encoding='utf-8', newline='\n')
        b.call(['cp', name + ':/report/.', b.local(out)])
        check('native_exit', p.returncode == 0)
        check('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as error:
        check('exception', False, {'class': type(error).__name__, 'code': str(error)[:150]})
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            absent = b.call(['inspect', name], check=False)
            check('cleanup_exact_owned', absent.returncode != 0 and re.search(r'no such (object|container)', absent.stderr, re.I) is not None)
        check('sources_stable', baseline == sources())
        receipt = {'suite': 'A32-native-owned', 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'checks': checks, 'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
        (out / 'bench-commands.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
        for f, data in [('runner.json', receipt), ('sources.json', baseline)]:
            (out / f).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
