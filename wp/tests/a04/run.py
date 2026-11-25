"""Owned A04 offline runner: never invokes T01 or sweeps orphans."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import uuid
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
spec = importlib.util.spec_from_file_location('a02', ROOT.parent / 'a02-audit/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
LABEL = 'org.imagine.a04-update'
bench.LABEL = LABEL

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--unit-only', action='store_true')
    p.add_argument('--probe', action='store_true')
    args = p.parse_args()
    out = REPO / 'production/A-04/preuves' / uuid.uuid4().hex[:12]
    out.mkdir(parents=True)
    name = 'imagine-a04-' + uuid.uuid4().hex[:12]
    result = {'container': name, 'checks': [], 'exit_code': 1}
    created = False
    def record(key, ok, detail=None):
        result['checks'].append({'check': key, 'ok': bool(ok), 'detail': detail})
    source_files = [ROOT / 'public.lock.json'] + list(ROOT.glob('*.py')) + list(ROOT.glob('*.php')) + [REPO / 'wp/outils/bascule/mettre-a-jour'] + list((REPO / 'wp/outils/bascule/a04').glob('*.php')) + list((REPO / 'wp/outils/bascule/a04').glob('*.py'))
    initial = {str(p.relative_to(REPO)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files if p.is_file()}
    (out / 'sources.json').write_text(json.dumps(initial, indent=2)+'\n')
    try:
        info = json.loads(bench.call(['image', 'inspect', bench.IMAGE]).stdout)[0]
        assert not info['Config'].get('Volumes') and not info['Config'].get('ExposedPorts')
        bench.call(['create', '--name', name, '--label', LABEL+'='+name, '--pull', 'never', '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--no-healthcheck', '--pids-limit', '256', '--memory', '2g', '--cpus', '2', '--log-driver', 'none', '--entrypoint', '/bin/sleep', bench.IMAGE, 'infinity'])
        created = True
        inspected = json.loads(bench.call(['inspect', name]).stdout)[0]
        record('isolation_before', True, bench.validate(inspected, name))
        bench.call(['start', name])
        bench.call(['exec', name, 'mkdir', '-p', '/opt/a04', '/subject/a04', '/report', '/subject/a03', '/opt/a03', '/plugins/imagine-non-regression/src', '/staging/mu-plugins'])
        for source in source_files:
            if source.is_file():
                target = '/opt/a04/'+source.name if source.parent == ROOT else '/subject/a04/'+source.name if source.parent.name == 'a04' else '/subject/mettre-a-jour'
                bench.call(['cp', bench.local(source), name+':'+target])
        if args.probe:
            for file in bench.LICENSED:
                bench.call(['cp', '/home/ced/staging-wp/plugins/'+file, name+':/opt/a04/'+file])
            probe = bench.call(['exec', name, 'python3', '/opt/a04/probe.py'], check=False)
            (out/'probe.log').write_text(probe.stdout+probe.stderr)
            record('probe', probe.returncode == 0)
        else:
            lint = {p.name: bench.call(['exec', name, 'php', '-l', '/subject/a04/'+p.name if p.parent.name == 'a04' and p.parent.parent.name == 'bascule' else '/opt/a04/'+p.name], check=False).returncode for p in source_files if p.suffix == '.php'}
            record('lint', all(v == 0 for v in lint.values()), lint)
            unit = bench.call(['exec', name, 'python3', '-B', '-m', 'unittest', 'discover', '-s', '/opt/a04', '-p', 'test_*.py', '-v'], check=False)
            (out/'unit.log').write_text(unit.stdout+unit.stderr)
            record('unit', unit.returncode == 0)
            if not args.unit_only and unit.returncode == 0:
                # Read-only reuse; no baseline sources are changed.
                files = [(ROOT.parent/'a03-non-regression'/f, '/opt/a03/'+f) for f in ['seed.php', 'inside.py', 'http-rollback.php']]
                files += [(REPO/'wp/outils/bascule'/f, '/subject/'+f) for f in ['non-regression', 'comparer', 'audit']]
                files += [(p, '/subject/a03/'+p.name) for p in (REPO/'wp/outils/bascule/a03').glob('*.php')]
                files += [(p, '/plugins/imagine-non-regression/src/'+p.name) for p in (REPO/'wp/plugins/imagine-non-regression/src').glob('*.php')]
                files += [(REPO/'wp/outils/staging/runtime-probe.php', '/staging/runtime-probe.php'), (REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', '/staging/mu-plugins/000-imagine-staging-safety.php'), (REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', '/subject/000-imagine-staging-safety.php'), (ROOT.parent/'a02-audit/fingerprint.php', '/opt/a03/fingerprint.php')]
                deps = {str(s.relative_to(REPO)): hashlib.sha256(s.read_bytes()).hexdigest() for s,t in files}
                (out/'dependencies.json').write_text(json.dumps(deps,indent=2)+'\n')
                for s,t in files:
                    bench.call(['cp', bench.local(s), name+':'+t])
                for file in bench.LICENSED:
                    bench.call(['cp', '/home/ced/staging-wp/plugins/'+file, name+':/opt/a03/'+file])
                for public in ['wordpress-6.9.1.zip', 'wordpress-7.0.zip', 'woocommerce-11.0.1.zip']:
                    path = REPO / 'production/A-04/dependances' / public
                    assert path.is_file(), 'A04_PUBLIC_PREPARATION_REQUIRED'
                    assert hashlib.sha256(path.read_bytes()).hexdigest() == json.loads((ROOT/'public.lock.json').read_text())[public]['sha256'], 'A04_PUBLIC_SHA256'
                    bench.call(['cp', bench.local(path), name+':/opt/a04/'+public])
                execution = bench.call(['exec', name, 'python3', '-B', '/opt/a04/inside.py'], check=False, timeout=1500)
                (out/'execution.log').write_text(execution.stdout+execution.stderr)
                bench.call(['cp', name+':/report/.', bench.local(out)])
                inner = json.loads((out/'result.json').read_text())
                record('integration', execution.returncode == 0 and inner['exit_code'] == 0)
                record('dependencies_unchanged', deps == {str(s.relative_to(REPO)): hashlib.sha256(s.read_bytes()).hexdigest() for s,t in files})
        record('isolation_after', True, bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name))
    except Exception as e:
        record('exception', False, {'class': type(e).__name__, 'code': str(e)[:200]})
    finally:
        if created:
            try:
                v = json.loads(bench.call(['inspect', name]).stdout)[0]
                assert v['Name'] == '/'+name and v['Config']['Labels'].get(LABEL) == name
                bench.call(['rm', '-f', name])
                v = bench.call(['inspect', name], check=False)
                record('cleanup_exact_owned', v.returncode != 0 and 'no such' in v.stderr.lower())
            except Exception as e:
                record('cleanup_exact_owned', False, type(e).__name__)
        record('sources_unchanged', initial == {str(p.relative_to(REPO)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files if p.is_file()})
        result['exit_code'] = int(any(not c['ok'] for c in result['checks']))
        (out/'runner.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'output': str(out), **json.loads((out/'runner.json').read_text())},indent=2))
    return result['exit_code']
if __name__ == '__main__':
    sys.exit(main())
