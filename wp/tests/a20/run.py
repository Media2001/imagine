"""A20 isolated native runner; no host PHP, archives or site arguments."""
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
b.LABEL='org.imagine.a20-prices'
OWN=['wp/tests/a20','wp/outils/bascule/a20']
DEPENDENCIES=['wp/tests/a02-audit/'+f for f in ['run.py','inside.py','seed.php','fingerprint.php','unit.php','readonly-probe.php']]+['wp/outils/bascule/audit','wp/outils/bascule/a11','wp/outils/bascule/a12']

def manifest(roots):
    files=[]
    for key in roots:
        p=ROOT/key;files.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if '__pycache__' not in p.parts}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--unit-only',action='store_true')
    a=ap.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    name='imagine-a20-prices-'+uuid.uuid4().hex[:12];owned=manifest(OWN);deps=manifest(DEPENDENCIES)
    receipt={'suite':'A20-owned-runner','container':name,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':'unit' if a.unit_only else 'native','checks':[],'exit_code':1}
    created=False
    def check(key,ok,detail=None):receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL','detail':detail})
    try:
        image=json.loads(b.call(['image','inspect',b.IMAGE]).stdout)[0];assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity']);created=True
        check('isolation_before',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name]);b.call(['exec',name,'mkdir','-p','/subject/a20','/opt/a20','/opt/a02','/report'])
        for source,dest in [(HERE,'/opt/a20'),(ROOT/'wp/outils/bascule/a20','/subject/a20')]:
            for p in sorted(source.glob('*')):
                if p.is_file():b.call(['cp',b.local(p),name+':'+dest+'/'+p.name])
        for dependency in ['audit','a11','a12','stream_guard.py','stream_refusals.json','stream_bridge.php']:b.call(['cp',b.local(ROOT/'wp/outils/bascule'/dependency),name+':/subject/'+dependency])
        p=b.call(['exec',name,'php','/opt/a20/unit.php'],check=False);(out/'unit.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        b.call(['cp',name+':/report/unit.json',b.local(out/'unit.json')]);check('unit_return',p.returncode==0,{'exit_code':p.returncode})
        pure=b.call(['exec',name,'php','-n','-d','disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open','/opt/a20/pure-probe.php'],check=False)
        (out/'pure.log').write_text(pure.stdout+pure.stderr,encoding='utf-8')
        check('pure_no_extensions_no_writes',pure.returncode==0 and pure.stderr=='' and pure.stdout=='A20_PURE_OK '+str(len(json.loads((out/'unit.json').read_text(encoding='utf-8'))['checks']))+'\n')
        relocate="from pathlib import Path; import shutil; root=Path('/tmp/a20-pure'); (root/'wp/tests/a20').mkdir(parents=True); (root/'report').mkdir(); shutil.copytree('/subject/a20',root/'wp/outils/bascule/a20'); (root/'wp/tests/a20/unit.php').write_text(Path('/opt/a20/unit.php').read_text(encoding='utf-8').replace('/report/unit.json','/tmp/a20-pure/report/unit.json'),encoding='utf-8')"
        b.call(['exec',name,'python3','-c',relocate])
        p=b.call(['exec',name,'php','-n','/tmp/a20-pure/wp/tests/a20/unit.php'],check=False)
        b.call(['cp',name+':/tmp/a20-pure/report/unit.json',b.local(out/'relocated-unit.json')])
        check('temporary_layout_pure_receipt_identical',p.returncode==0 and p.stdout==p.stderr=='' and json.loads((out/'relocated-unit.json').read_text(encoding='utf-8'))==json.loads((out/'unit.json').read_text(encoding='utf-8')))
        if not a.unit_only:
            for f in ['inside.py','seed.php','fingerprint.php','unit.php','readonly-probe.php']:b.call(['cp',b.local(ROOT/'wp/tests/a02-audit'/f),name+':/opt/a02/'+f])
            for f in b.LICENSED:b.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a02/'+f])
            p=b.call(['exec',name,'python3','/opt/a20/inside.py'],check=False,timeout=1500);(out/'native.log').write_text(p.stdout+p.stderr,encoding='utf-8')
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
