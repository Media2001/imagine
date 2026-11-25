"""Owned disconnected A09 runner; PHP only inside disposable Docker."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import uuid
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
spec = importlib.util.spec_from_file_location('a09_boundary', ROOT.parent/'a02-audit/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
LABEL = 'org.imagine.a09-redirections'
bench.LABEL = LABEL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filter')
    args = parser.parse_args()
    if args.filter and not re.fullmatch(r'[A-Za-z0-9_.]+', args.filter):
        parser.error('simple unittest identifier required')
    out = REPO/'production/A-09/preuves'/uuid.uuid4().hex[:12]
    out.mkdir(parents=True)
    name = 'imagine-a09-'+uuid.uuid4().hex[:12]
    result = {'container': name, 'label': LABEL, 'checks': [], 'exit_code': 1}
    created = False
    paths = [p for folder in ['wp/outils/bascule', 'wp/tests/a09'] for p in (REPO/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    safety = REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php'
    paths.append(safety)
    def hashes():
        return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    initial = hashes()
    (out/'sources.json').write_text(json.dumps(initial, indent=2)+'\n', encoding='utf8')
    def record(key, ok, detail=None):
        result['checks'].append({'check': key, 'ok': bool(ok), 'detail': detail})
    try:
        image = json.loads(bench.call(['image', 'inspect', bench.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        bench.call(['create', '--name', name, '--label', LABEL+'='+name, '--pull', 'never', '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--no-healthcheck', '--pids-limit', '128', '--memory', '512m', '--cpus', '2', '--log-driver', 'none', '--entrypoint', '/bin/sleep', bench.IMAGE, 'infinity'])
        created = True
        info = json.loads(bench.call(['inspect', name]).stdout)[0]
        (out/'inspect-before.json').write_text(json.dumps(info, indent=2)+'\n', encoding='utf8')
        record('isolation_before', True, bench.validate(info, name))
        bench.call(['start', name])
        bench.call(['exec', name, 'mkdir', '-p', '/repo/wp/outils', '/repo/wp/tests', '/repo/wp/outils/staging/mu-plugins', '/report'])
        for source, target in [(REPO/'wp/outils/bascule', '/repo/wp/outils/'), (ROOT, '/repo/wp/tests/'), (safety, '/repo/wp/outils/staging/mu-plugins/')]:
            bench.call(['cp', bench.local(source), name+':'+target])
        command = ['python3', '-B', '-m', 'unittest']
        if args.filter:
            command += ['-v', args.filter]
        else:
            command += ['discover', '-s', '/repo/wp/tests/a09', '-p', 'test_*.py', '-v']
        execution = bench.call(['exec', '-w', '/repo/wp/tests/a09', name]+command, check=False, timeout=300)
        (out/'tests.log').write_text(execution.stdout+execution.stderr, encoding='utf8')
        record('tests', execution.returncode == 0, {'command': command, 'exit': execution.returncode})
        bench.call(['cp', name+':/report/.', bench.local(out)])
        info = json.loads(bench.call(['inspect', name]).stdout)[0]
        (out/'inspect-after.json').write_text(json.dumps(info, indent=2)+'\n', encoding='utf8')
        record('isolation_after', True, bench.validate(info, name))
    except Exception as error:
        record('exception', False, {'type': type(error).__name__, 'message': str(error)[:300]})
    finally:
        if created:
            try:
                info = json.loads(bench.call(['inspect', name]).stdout)[0]
                assert info['Name'] == '/'+name and info['Config']['Labels'].get(LABEL) == name
                bench.call(['rm', '-f', name])
                missing = bench.call(['inspect', name], check=False)
                record('cleanup_exact_owned', missing.returncode != 0 and re.search(r'no such (object|container)', missing.stderr, re.I) is not None, {'exit': missing.returncode, 'diagnostic': missing.stderr.strip()})
            except Exception as error:
                record('cleanup_exact_owned', False, str(error))
        record('sources_unchanged', hashes() == initial)
        result['exit_code'] = int(any(not row['ok'] for row in result['checks']))
        (out/'runner.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
        print(json.dumps({'output': str(out), **result}, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
