"""A16 isolated native runner; no host PHP, archives or site arguments."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('a02_runner',ROOT/'wp/tests/a02-audit/run.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.LABEL='org.imagine.a16-issues'
OWN=['wp/tests/a16','wp/outils/bascule/a16']
DEPENDENCIES=['wp/tests/a02-audit','wp/outils/bascule/audit','wp/outils/bascule/a11','wp/outils/bascule/a12']

def manifest(roots):
    files=[]
    for key in roots:
        p=ROOT/key;files.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if '__pycache__' not in p.parts}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--unit-only',action='store_true')
    a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    name='imagine-a16-issues-'+uuid.uuid4().hex[:12];owned=manifest(OWN);deps=manifest(DEPENDENCIES)
    receipt={'suite':'A16-owned-runner','container':name,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'unit' if a.unit_only else 'native','checks':[],'exit_code':1}
    created=False
    def check(key,ok,detail=None):receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL','detail':detail})
    try:
        image=json.loads(b.call(['image','inspect',b.IMAGE]).stdout)[0];assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity']);created=True
        check('isolation_before',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name]);b.call(['exec',name,'mkdir','-p','/subject/a16','/opt/a16','/opt/a02','/report'])
        for source,dest in [(HERE,'/opt/a16'),(ROOT/'wp/outils/bascule/a16','/subject/a16')]:
            for p in sorted(source.glob('*')):
                if p.is_file():b.call(['cp',b.local(p),name+':'+dest+'/'+p.name])
        for dependency in ['audit','a11','a12']:b.call(['cp',b.local(ROOT/'wp/outils/bascule'/dependency),name+':/subject/'+dependency])
        p=b.call(['exec',name,'php','/opt/a16/unit.php'],check=False);(out/'unit.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        b.call(['cp',name+':/report/unit.json',b.local(out/'unit.json')]);check('unit_return',p.returncode==0,{'exit_code':p.returncode})
        if not a.unit_only:
            for f in ['inside.py','seed.php','fingerprint.php','unit.php','readonly-probe.php']:b.call(['cp',b.local(ROOT/'wp/tests/a02-audit'/f),name+':/opt/a02/'+f])
            for f in b.LICENSED:b.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a02/'+f])
            p=b.call(['exec',name,'python3','/opt/a16/inside.py'],check=False,timeout=1500);(out/'native.log').write_text(p.stdout+p.stderr,encoding='utf-8')
            b.call(['cp',name+':/report/.',b.local(out)]);check('native_return',p.returncode==0,{'exit_code':p.returncode})
        check('isolation_after',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
    except Exception as error:check('exception',False,{'class':type(error).__name__,'code':str(error)[:180]})
    finally:
        if created:
            info=json.loads(b.call(['inspect',name]).stdout)[0];assert info['Name']=='/'+name and info['Config']['Labels'].get(b.LABEL)==name
            b.call(['rm','-f',name]);missing=b.call(['inspect',name],check=False);check('cleanup_exact_owned_runner',missing.returncode!=0 and re.search('no such (object|container)',missing.stderr,re.I) is not None)
        check('owned_sources_stable',owned==manifest(OWN));check('dependencies_stable',deps==manifest(DEPENDENCIES))
        receipt['exit_code']=int(any(x['status']!='PASS' for x in receipt['checks']))
        for filename,data in [('runner.json',receipt),('sources.json',owned),('dependency-snapshot.json',deps)]:
            (out/filename).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(receipt,indent=2))
    return receipt['exit_code']

if __name__=='__main__':sys.exit(main())
