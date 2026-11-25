"""A10 runner: reuse A02 native fixture, distinct ownership, no site arguments."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import uuid
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a02bench', REPO / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a10-coupons'

def manifest():
    roots = [HERE, REPO/'wp/outils/bascule/a10', REPO/'wp/outils/bascule/inventorier-codes', REPO/'wp/outils/bascule/audit']
    return {p.relative_to(REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in roots for p in ([root] if root.is_file() else root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}

def a02_manifest():
    baseline = json.loads((REPO/'production/A-10/a02-baseline.json').read_text())
    root = REPO/'wp/tests/a02-audit'
    files = [p for p in root.rglob('*') if p.is_file()] + [REPO/'wp/outils/bascule/audit']
    actual = {p.relative_to(REPO).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    return baseline, actual

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--unit-only',action='store_true')
    ap.add_argument('--phase',choices=['red','green','final'],default='final')
    args=ap.parse_args()
    run_id=uuid.uuid4().hex[:12]
    name='imagine-a10-coupons-'+run_id
    out=REPO/'production/A-10/preuves'/run_id
    out.mkdir(parents=True,exist_ok=False)
    source=manifest()
    base0=a02_manifest()[1]
    (out/'sources.json').write_text(json.dumps(source,indent=2)+'\n')
    receipt={'run_id':run_id,'phase':args.phase,'mode':'unit' if args.unit_only else 'native','container':name,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'exit_code':1}
    created=False
    def record(key,ok,detail=None):
        receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL','detail':detail})
    try:
        image=json.loads(b.call(['image','inspect',b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity'])
        created=True
        record('isolation_before',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name]); b.call(['exec',name,'mkdir','-p','/subject/a10','/opt/a10','/opt/a02','/report'])
        for p in HERE.iterdir():
            if p.is_file(): b.call(['cp',b.local(p),name+':/opt/a10/'+p.name])
        for p in (REPO/'wp/outils/bascule/a10').glob('*'):
            if p.is_file(): b.call(['cp',b.local(p),name+':/subject/a10/'+p.name])
        for f in ['audit','inventorier-codes']:
            p=REPO/'wp/outils/bascule'/f
            if p.exists(): b.call(['cp',b.local(p),name+':/subject/'+f])
        unit=b.call(['exec',name,'php','/opt/a10/unit.php'],check=False)
        (out/'unit.log').write_text(unit.stdout+unit.stderr)
        b.call(['cp',name+':/report/unit.json',b.local(out/'unit.json')])
        record('unit_return',unit.returncode==0,{'exit_code':unit.returncode})
        if not args.unit_only:
            for p in (REPO/'wp/tests/a02-audit').iterdir():
                if p.is_file(): b.call(['cp',b.local(p),name+':/opt/a02/'+p.name])
            for f in b.LICENSED: b.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a02/'+f])
            native=b.call(['exec',name,'python3','/opt/a10/inside.py'],check=False,timeout=1500)
            (out/'native.log').write_text(native.stdout+native.stderr)
            b.call(['cp',name+':/report/.',b.local(out)])
            inner=json.loads((out/'result.json').read_text())
            record('native_return',native.returncode==0 and inner['exit_code']==0,{'exit_code':native.returncode})
        record('isolation_after',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
    except Exception as exc:
        record('exception',False,{'class':type(exc).__name__,'code':str(exc)[:180]})
    finally:
        if created:
            try:
                info=json.loads(b.call(['inspect',name]).stdout)[0]
                assert info['Name']=='/'+name and info['Config']['Labels'].get(b.LABEL)==name
                b.call(['rm','-f',name])
                missing=b.call(['inspect',name],check=False)
                record('cleanup',missing.returncode!=0 and bool(re.search(r'no such (object|container)',missing.stderr,re.I)))
            except Exception as exc: record('cleanup',False,{'class':type(exc).__name__})
        record('sources_unchanged',manifest()==source)
        record('a02_unchanged_during_run',a02_manifest()[1]==base0)
        receipt['exit_code']=int(any(x['status']!='PASS' for x in receipt['checks']))
        (out/'runner.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({'evidence':str(out),**receipt},indent=2))
    return receipt['exit_code']
if __name__=='__main__': sys.exit(main())
