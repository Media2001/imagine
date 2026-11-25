"""A08-owned offline runner. No sweep, no staging API, no host PHP."""
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
spec = importlib.util.spec_from_file_location('boundary', ROOT.parent / 'a02-audit/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
LABEL = 'org.imagine.a08-repetition'
bench.LABEL = LABEL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit-only', action='store_true')
    args = parser.parse_args()
    out = REPO / 'production/A-08/preuves' / uuid.uuid4().hex[:12]
    out.mkdir(parents=True)
    name = 'imagine-a08-' + uuid.uuid4().hex[:12]
    result = {'container': name, 'label': LABEL, 'checks': [], 'exit_code': 1}
    created = False

    def record(key, ok, detail=None):
        result['checks'].append({'check': key, 'ok': bool(ok), 'detail': detail})

    base = REPO / 'wp/outils/bascule'
    pairs = [(p, '/opt/a08/' + p.name) for p in ROOT.iterdir() if p.is_file()]
    pairs += [(p, '/subject/' + str(p.relative_to(base)).replace('\\', '/')) for p in base.rglob('*') if p.is_file()]
    for folder in ['a03-non-regression', 'a04', 'a05']:
        target = {'a03-non-regression': 'a03', 'a04': 'a04', 'a05': 'a05'}[folder]
        pairs += [(p, '/opt/' + target + '/' + p.name) for p in (ROOT.parent/folder).iterdir() if p.is_file()]
    pairs += [(p, '/plugins/imagine-non-regression/src/'+p.name) for p in (REPO/'wp/plugins/imagine-non-regression/src').glob('*.php')]
    pairs += [(ROOT.parent/'a02-audit/unit.php','/opt/a02/unit.php')]
    pairs += [(REPO/'wp/outils/staging/runtime-probe.php','/staging/runtime-probe.php'),
              (REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php','/staging/mu-plugins/000-imagine-staging-safety.php'),
              (REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php','/subject/000-imagine-staging-safety.php'),
              (ROOT.parent/'a02-audit/fingerprint.php','/opt/a03/fingerprint.php')]

    def hashes():
        return {str(p.relative_to(REPO)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p, _ in pairs}

    initial = hashes()
    (out/'sources.json').write_text(json.dumps(initial, indent=2)+'\n')
    try:
        info = json.loads(bench.call(['image', 'inspect', bench.IMAGE]).stdout)[0]
        assert not info['Config'].get('Volumes') and not info['Config'].get('ExposedPorts')
        bench.call(['create','--name',name,'--label',LABEL+'='+name,'--pull','never','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--no-healthcheck','--pids-limit','256','--memory','2g','--cpus','2','--log-driver','none','--entrypoint','/bin/sleep',bench.IMAGE,'infinity'])
        created = True
        inspected = json.loads(bench.call(['inspect', name]).stdout)[0]
        (out/'inspect-before.json').write_text(json.dumps(inspected, indent=2)+'\n')
        record('isolation_before', True, bench.validate(inspected, name))
        bench.call(['start',name])
        directories = sorted({str(pathlib.PurePosixPath(t).parent) for _, t in pairs} | {'/report','/opt/a04','/opt/a03'})
        bench.call(['exec',name,'mkdir','-p']+directories)
        for p, t in pairs:
            bench.call(['cp',bench.local(p),name+':'+t])
        unit = bench.call(['exec',name,'python3','-B','-m','unittest','discover','-s','/opt/a08','-p','test_*.py','-v'],check=False)
        (out/'unit.log').write_text(unit.stdout+unit.stderr)
        record('unit', unit.returncode == 0, {'exit': unit.returncode})
        if not args.unit_only and unit.returncode == 0:
            for suite, command in [
                ('a02',['php','/opt/a02/unit.php']),
                ('a03',['php','/opt/a03/unit.php']),
                ('a03-boundary',['php','/opt/a03/output-boundary.php']),
                ('a04',['python3','-B','-m','unittest','discover','-s','/opt/a04','-p','test_*.py','-v']),
                ('a05',['python3','-B','-m','unittest','discover','-s','/opt/a05','-p','test_*.py','-v'])]:
                regression=bench.call(['exec',name]+command,check=False)
                (out/(suite+'-regression.log')).write_text(regression.stdout+regression.stderr)
                record(suite+'_regression',regression.returncode==0,{'command':command,'exit':regression.returncode})
                if suite in ['a02','a03']:
                    bench.call(['exec',name,'mv','/report/unit.json','/report/'+suite+'-unit.json'])
            for f in bench.LICENSED:
                bench.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a03/'+f])
            lock = json.loads((ROOT.parent/'a04/public.lock.json').read_text())
            for f in ['wordpress-7.0.zip','woocommerce-11.0.1.zip']:
                p = REPO/'production/A-08/dependances'/f
                if not p.is_file():
                    p = REPO/'production/A-04/dependances'/f
                assert hashlib.sha256(p.read_bytes()).hexdigest() == lock[f]['sha256']
                bench.call(['cp',bench.local(p),name+':/opt/a04/'+f])
            execution = bench.call(['exec',name,'python3','-B','/opt/a08/inside.py'],check=False,timeout=1700)
            (out/'execution.log').write_text(execution.stdout+execution.stderr)
            bench.call(['cp',name+':/report/.',bench.local(out)])
            inner = json.loads((out/'result.json').read_text())
            record('integration', execution.returncode == 0 and inner['exit_code'] == 0, {'exit':execution.returncode})
        inspected = json.loads(bench.call(['inspect',name]).stdout)[0]
        (out/'inspect-after.json').write_text(json.dumps(inspected, indent=2)+'\n')
        record('isolation_after',True,bench.validate(inspected,name))
    except Exception as error:
        record('exception', False, {'class':type(error).__name__, 'code':str(error)[:300]})
    finally:
        if created:
            try:
                info = json.loads(bench.call(['inspect',name]).stdout)[0]
                assert info['Name']=='/'+name and info['Config']['Labels'].get(LABEL)==name
                bench.call(['rm','-f',name])
                missing=bench.call(['inspect',name],check=False)
                record('cleanup_exact_owned',missing.returncode!=0 and re.search(r'no such (object|container)',missing.stderr,re.I) is not None, {'exit':missing.returncode,'diagnostic':missing.stderr.strip()})
            except Exception as error:
                record('cleanup_exact_owned',False,type(error).__name__)
        record('sources_unchanged', initial == hashes())
        result['exit_code'] = int(any(not c['ok'] for c in result['checks']))
        (out/'runner.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'output':str(out),**result},indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
