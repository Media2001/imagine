"""A03 synthetic proof only; dependencies from the accepted A02 offline bench."""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import uuid
import hashlib

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
spec = importlib.util.spec_from_file_location('a02_bench', ROOT.parent / 'a02-audit/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
LABEL = 'org.imagine.a03-non-regression'
bench.LABEL = LABEL

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit-only', action='store_true')
    parser.add_argument('--name', default='proof')
    args = parser.parse_args()
    assert args.name.replace('-', '').isalnum()
    out = REPO / 'production/A-03' / args.name
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a03-' + uuid.uuid4().hex[:12]
    result = {'container': name, 'checks': [], 'exit_code': 1}
    protected = [REPO / 'wp/outils/bascule/audit', ROOT.parent / 'a02-audit', REPO / 'wp/outils/staging']
    def inventory():
        return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for root in protected for p in ([root] if root.is_file() else root.rglob('*')) if p.is_file()}
    before = inventory()
    created = False
    def record(key, ok):
        result['checks'].append({'check': key, 'ok': bool(ok)})
    try:
        image = json.loads(bench.call(['image', 'inspect', bench.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        bench.call(['create', '--name', name, '--label', LABEL + '=' + name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none', '--pull', 'never', '--entrypoint', '/bin/sleep', bench.IMAGE, 'infinity'])
        created = True
        bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name)
        record('isolated_before', True)
        bench.call(['start', name])
        bench.call(['exec', name, 'mkdir', '-p', '/subject', '/opt/a03', '/report', '/opt/a02', '/staging/mu-plugins'])
        files = [(ROOT / 'unit.php', '/opt/a03/unit.php'), (REPO / 'wp/outils/bascule/audit', '/subject/audit')]
        for file in ['non-regression', 'comparer']:
            p = REPO / 'wp/outils/bascule' / file
            if p.exists():
                files.append((p, '/subject/' + file))
        if not args.unit_only:
            files += [(p, '/opt/a03/' + p.name) for p in ROOT.iterdir() if p.suffix in ('.php', '.py') and p.name not in ('run.py', 'unit.php')]
            files += [(REPO / 'wp/outils/staging/runtime-probe.php', '/staging/runtime-probe.php'), (REPO / 'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', '/staging/mu-plugins/000-imagine-staging-safety.php'), (REPO / 'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', '/subject/000-imagine-staging-safety.php'), (ROOT.parent / 'a02-audit/fingerprint.php', '/opt/a03/fingerprint.php')]
        for source, destination in files:
            bench.call(['cp', bench.local(source), name + ':' + destination])
        if not args.unit_only:
            for file in bench.LICENSED:
                bench.call(['cp', '/home/ced/staging-wp/plugins/' + file, name + ':/opt/a03/' + file])
        unit = bench.call(['exec', name, 'php', '/opt/a03/unit.php'], check=False)
        (out / 'unit.log').write_text(unit.stdout + unit.stderr, encoding='utf8')
        bench.call(['cp', name + ':/report/unit.json', bench.local(out / 'unit.json')])
        record('unit', unit.returncode == 0)
        if not args.unit_only and unit.returncode == 0:
            execution = bench.call(['exec', name, 'python3', '/opt/a03/inside.py'], check=False, timeout=1500)
            (out / 'execution.log').write_text(execution.stdout + execution.stderr, encoding='utf8')
            bench.call(['cp', name + ':/report/.', bench.local(out)])
            inner = json.loads((out / 'result.json').read_text())
            record('classic_hpos', execution.returncode == 0 and inner['exit_code'] == 0)
        bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name)
        record('isolated_after', True)
    except Exception as error:
        result['error'] = {'class': type(error).__name__, 'code': str(error)[:160]}
        record('execution', False)
    finally:
        if created:
            try:
                info = json.loads(bench.call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/' + name and info['Config']['Labels'].get(LABEL) == name
                bench.call(['rm', '-f', name])
                absent = bench.call(['inspect', name], check=False)
                record('owned_cleanup', absent.returncode != 0 and 'no such' in absent.stderr.lower())
            except Exception:
                record('owned_cleanup', False)
        record('accepted_sources_unchanged', before == inventory())
        result['exit_code'] = int(any(not item['ok'] for item in result['checks']))
        (out / 'runner.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        print(json.dumps({'output': str(out), **json.loads((out / 'runner.json').read_text())}, indent=2))
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
