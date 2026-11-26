"""A11 dedicated offline runner. Intermediates outside repository by default."""
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
spec = importlib.util.spec_from_file_location('a02bench', REPO/'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a11-addresses'

def hashes(roots):
    return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for root in roots for p in ([root] if root.is_file() else root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--unit-only', action='store_true')
    ap.add_argument('--final', action='store_true')
    args = ap.parse_args()
    run_id = uuid.uuid4().hex[:12]
    name = 'imagine-a11-addresses-'+run_id
    if args.final:
        out = REPO/'production/A-11/preuves'/run_id
    else:
        out = pathlib.Path.home()/'AppData/Local/hermes/cache/scratch/a11'/run_id
    out.mkdir(parents=True, exist_ok=False)
    roots = [HERE, REPO/'wp/outils/bascule/a11']
    protected = [REPO/'wp/tests/a02-audit', REPO/'wp/tests/a10', REPO/'wp/outils/bascule/a10', REPO/'wp/outils/bascule/a09/check.py', REPO/'wp/outils/bascule/audit']
    source, base = hashes(roots), hashes(protected)
    (out/'sources.json').write_text(json.dumps(source, indent=2)+'\n')
    (out/'protected-before.json').write_text(json.dumps(base, indent=2)+'\n')
    receipt = {'run_id':run_id, 'container':name, 'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks':[], 'exit_code':1}
    created = False
    def record(key, ok, detail=None):
        receipt['checks'].append({'check':key, 'status':'PASS' if ok else 'FAIL', 'detail':detail})
    try:
        image = json.loads(b.call(['image','inspect',b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity'])
        created = True
        record('isolation_before', True, b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name])
        b.call(['exec',name,'mkdir','-p','/subject/a11','/opt/a11','/opt/a02','/report','/reference/wp/outils/bascule/a09'])
        for root, dest in [(HERE,'/opt/a11/'),(REPO/'wp/outils/bascule/a11','/subject/a11/')]:
            for p in root.iterdir():
                if p.is_file(): b.call(['cp',b.local(p),name+':'+dest+p.name])
        b.call(['cp',b.local(REPO/'wp/outils/bascule/audit'),name+':/subject/audit'])
        for common in ['stream_guard.py','stream_refusals.json','stream_bridge.php']:
            b.call(['cp',b.local(REPO/'wp/outils/bascule'/common),name+':/subject/'+common])
        b.call(['cp',b.local(REPO/'wp/outils/bascule/a09/check.py'),name+':/reference/wp/outils/bascule/a09/check.py'])
        unit = b.call(['exec',name,'php','/opt/a11/unit.php'],check=False)
        (out/'unit.log').write_text(unit.stdout+unit.stderr,encoding='utf-8')
        b.call(['cp',name+':/report/unit.json',b.local(out/'unit.json')])
        record('unit',unit.returncode==0,{'exit_code':unit.returncode})
        if not args.unit_only:
            for p in (REPO/'wp/tests/a02-audit').iterdir():
                if p.is_file(): b.call(['cp',b.local(p),name+':/opt/a02/'+p.name])
            for f in b.LICENSED: b.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a02/'+f])
            native = b.call(['exec',name,'python3','/opt/a11/inside.py'],check=False,timeout=1500)
            (out/'execution.log').write_text(native.stdout+native.stderr,encoding='utf-8')
            b.call(['cp',name+':/report/.',b.local(out)])
            result = json.loads((out/'result.json').read_text())
            record('native', native.returncode==0 and result['exit_code']==0, {'exit_code':native.returncode})
        record('isolation_after',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
    except Exception as exc:
        record('exception',False,{'class':type(exc).__name__,'code':str(exc)[:200]})
    finally:
        if created:
            try:
                info=json.loads(b.call(['inspect',name]).stdout)[0]
                assert info['Name']=='/'+name and info['Config']['Labels'].get(b.LABEL)==name
                b.call(['rm','-f',name])
                missing=b.call(['inspect',name],check=False)
                record('cleanup', missing.returncode!=0 and bool(re.search(r'no such (object|container)',missing.stderr,re.I)))
            except Exception as exc: record('cleanup',False,{'class':type(exc).__name__})
        record('sources_unchanged',hashes(roots)==source)
        record('protected_sources_unchanged',hashes(protected)==base)
        (out/'protected-after.json').write_text(json.dumps(hashes(protected),indent=2)+'\n')
        receipt['exit_code']=int(any(c['status']!='PASS' for c in receipt['checks']))
        (out/'runner.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({'evidence':str(out),**receipt},indent=2))
    return receipt['exit_code']
if __name__=='__main__': sys.exit(main())
