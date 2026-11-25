"""Owned A05 offline runner; imports A02 boundary read-only, no sweeps."""
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
bench = importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
LABEL = 'org.imagine.a05-clean'
bench.LABEL = LABEL

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--unit-only', action='store_true'); args = parser.parse_args()
    out = REPO / 'production/A-05/preuves' / uuid.uuid4().hex[:12]; out.mkdir(parents=True)
    name = 'imagine-a05-' + uuid.uuid4().hex[:12]
    result = {'container': name, 'checks': [], 'exit_code': 1}; created = False
    def record(key, ok, detail=None):
        result['checks'].append({'check': key, 'ok': bool(ok), 'detail': detail})
    pairs = [(p, '/opt/a05/' + p.name) for p in ROOT.glob('*') if p.is_file()]
    base = REPO / 'wp/outils/bascule'
    pairs += [(p, '/subject/a05/' + p.name) for p in (base / 'a05').glob('*') if p.is_file()]
    pairs += [(base/'plan-imagine.exemple.json','/subject/plan-imagine.exemple.json'),(base/'nettoyer.md','/subject/nettoyer.md')]
    pairs += [(base / 'nettoyer', '/subject/nettoyer')] if (base / 'nettoyer').exists() else []
    pairs += [(p, '/subject/a04/' + p.name) for p in (base / 'a04').glob('*') if p.is_file()]
    pairs += [(ROOT.parent/'a03-non-regression'/f, '/opt/a03/'+f) for f in ['seed.php', 'inside.py', 'http-rollback.php']]
    pairs += [(base/f, '/subject/'+f) for f in ['audit','non-regression','comparer']]
    pairs += [(p, '/subject/a03/'+p.name) for p in (base/'a03').glob('*.php')]
    pairs += [(p, '/plugins/imagine-non-regression/src/'+p.name) for p in (REPO/'wp/plugins/imagine-non-regression/src').glob('*.php')]
    pairs += [(REPO/'wp/outils/staging/runtime-probe.php','/staging/runtime-probe.php'),(REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php','/staging/mu-plugins/000-imagine-staging-safety.php'),(REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php','/subject/000-imagine-staging-safety.php'),(ROOT.parent/'a02-audit/fingerprint.php','/opt/a03/fingerprint.php')]
    def hashes():
        return {str(p.relative_to(REPO)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p,t in pairs}
    initial = hashes(); (out/'sources.json').write_text(json.dumps(initial,indent=2)+'\n')
    try:
        info = json.loads(bench.call(['image','inspect',bench.IMAGE]).stdout)[0]
        assert not info['Config'].get('Volumes') and not info['Config'].get('ExposedPorts')
        bench.call(['create','--name',name,'--label',LABEL+'='+name,'--pull','never','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--no-healthcheck','--pids-limit','256','--memory','2g','--cpus','2','--log-driver','none','--entrypoint','/bin/sleep',bench.IMAGE,'infinity']); created=True
        record('isolation_before',True,bench.validate(json.loads(bench.call(['inspect',name]).stdout)[0],name))
        bench.call(['start',name]); bench.call(['exec',name,'mkdir','-p','/opt/a05','/subject/a05','/subject/a04','/subject/a03','/opt/a03','/report','/staging/mu-plugins','/plugins/imagine-non-regression/src'])
        for p,t in pairs: bench.call(['cp',bench.local(p),name+':'+t])
        lint = {t: bench.call(['exec',name,'php','-l',t],check=False).returncode for p,t in pairs if p.suffix=='.php' and '/a05/' in t}
        record('lint',all(v==0 for v in lint.values()),lint)
        unit=bench.call(['exec',name,'python3','-B','-m','unittest','discover','-s','/opt/a05','-p','test_*.py','-v'],check=False)
        (out/'unit.log').write_text(unit.stdout+unit.stderr); record('unit',unit.returncode==0)
        if not args.unit_only and unit.returncode==0:
            for f in bench.LICENSED: bench.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a03/'+f])
            execution=bench.call(['exec',name,'python3','-B','/opt/a05/inside.py'],check=False,timeout=1500)
            (out/'execution.log').write_text(execution.stdout+execution.stderr)
            bench.call(['cp',name+':/report/.',bench.local(out)])
            inner=json.loads((out/'result.json').read_text());record('integration',execution.returncode==0 and inner['exit_code']==0,{'exit':execution.returncode})
        record('isolation_after',True,bench.validate(json.loads(bench.call(['inspect',name]).stdout)[0],name))
    except Exception as error: record('exception',False,{'class':type(error).__name__,'code':str(error)[:300]})
    finally:
        if created:
            try:
                v=json.loads(bench.call(['inspect',name]).stdout)[0]
                assert v['Name']=='/'+name and v['Config']['Labels'].get(LABEL)==name
                bench.call(['rm','-f',name]); missing=bench.call(['inspect',name],check=False)
                record('cleanup_exact_owned',missing.returncode!=0 and re.search(r'no such (object|container)',missing.stderr,re.I) is not None)
            except Exception as error: record('cleanup_exact_owned',False,type(error).__name__)
        record('sources_unchanged',initial==hashes())
        result['exit_code']=int(any(not c['ok'] for c in result['checks']))
        (out/'runner.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'output':str(out),**result},indent=2))
    return result['exit_code']
if __name__=='__main__':sys.exit(main())
