"""A21 owned offline runner, reusing the unchanged A19/A02 bench."""
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
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a19_runner', ROOT/'wp/tests/a19/run.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
b = r.b
b.LABEL = 'org.imagine.a21-external-doors'
OWN = ['wp/tests/a21', 'wp/outils/bascule/a21']
DEPENDENCIES = ['wp/tests/a02-audit', 'wp/tests/a19', 'wp/outils/bascule/audit', 'wp/outils/bascule/a11', 'wp/outils/bascule/a12', 'wp/outils/staging','wp/outils/bascule/stream_guard.py','wp/outils/bascule/stream_refusals.json','wp/outils/bascule/stream_bridge.php','wp/tests/a22/run.py','wp/tests/a22/replay.py','wp/tests/a22/channels.py','wp/tests/a22/documented.json']
def manifest(roots):
    # Shared documentation is a two-line contract, never a whole-file hash.
    return {key:value for key,value in r.manifest(roots).items() if key != 'wp/tests/a02-audit/README.md'}
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--unit-only', action='store_true')
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a21-external-doors-'+uuid.uuid4().hex[:12]
    owned, deps = manifest(OWN), manifest(DEPENDENCIES)
    receipt = {'suite':'A21-owned-runner','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'container':name,'mode':'unit' if a.unit_only else 'native','checks':[],'exit_code':1}
    created = False
    def check(key, ok, detail=None):
        receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL','detail':detail})
    try:
        image = json.loads(b.call(['image','inspect',b.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity'])
        created = True
        check('isolation_before', True, b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name])
        b.call(['exec',name,'mkdir','-p','/subject/a21','/opt/a21','/opt/a02','/report'])
        for source,dest in [(HERE,'/opt/a21'),(ROOT/'wp/outils/bascule/a21','/subject/a21')]:
            if source.is_dir():
                for p in sorted(source.glob('*')):
                    if p.is_file():
                        b.call(['cp',b.local(p),name+':'+dest+'/'+p.name])
        for dependency in ['audit','a11','a12','stream_guard.py','stream_refusals.json','stream_bridge.php']:
            b.call(['cp',b.local(ROOT/'wp/outils/bascule'/dependency),name+':/subject/'+dependency])
        p = b.call(['exec',name,'php','/opt/a21/unit.php'],check=False)
        (out/'unit.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        b.call(['cp',name+':/report/unit.json',b.local(out/'unit.json')])
        check('unit_return',p.returncode==0,{'exit_code':p.returncode})
        pure=b.call(['exec',name,'php','/opt/a21/pure-include.php'],check=False)
        (out/'pure-include.log').write_text(pure.stdout+pure.stderr,encoding='utf-8')
        if pure.returncode!=0 or pure.stderr:
            raise RuntimeError('A21_PURE_INCLUDE_FAILED')
        pure_data=json.loads(pure.stdout)
        (out/'pure-include.json').write_text(json.dumps(pure_data,indent=2)+'\n',encoding='utf-8')
        check('pure_include_no_native_or_side_effect',pure.returncode==0 and pure.stderr=='' and pure_data['count']>0
              and all(pure_data[key] is True for key in ['green','quiet','files_unchanged','native_absent']))
        if not a.unit_only and p.returncode == 0:
            for f in ['inside.py','seed.php','fingerprint.php','unit.php','readonly-probe.php']:
                b.call(['cp',b.local(ROOT/'wp/tests/a02-audit'/f),name+':/opt/a02/'+f])
            for f in b.LICENSED:
                b.call(['cp','/home/ced/staging-wp/plugins/'+f,name+':/opt/a02/'+f])
            b.call(['cp',b.local(ROOT/'wp/outils/staging'),name+':/subject/staging'])
            p = b.call(['exec',name,'python3','/opt/a21/inside.py'],check=False,timeout=1500)
            (out/'native.log').write_text(p.stdout+p.stderr,encoding='utf-8')
            b.call(['cp',name+':/report/.',b.local(out)])
            check('native_return',p.returncode==0,{'exit_code':p.returncode})
        check('isolation_after',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
    except Exception as error:
        check('exception',False,{'class':type(error).__name__,'code':str(error)[:180]})
    finally:
        if created:
            info = json.loads(b.call(['inspect',name]).stdout)[0]
            assert info['Name']=='/'+name and info['Config']['Labels'].get(b.LABEL)==name
            b.call(['rm','-f',name])
            missing=b.call(['inspect',name],check=False)
            check('cleanup_exact_owned_runner',missing.returncode!=0 and re.search('no such (object|container)',missing.stderr,re.I) is not None)
        check('owned_sources_stable',owned==manifest(OWN))
        check('dependencies_stable',deps==manifest(DEPENDENCIES))
        receipt['exit_code']=int(any(x['status']!='PASS' for x in receipt['checks']))
        for filename,data in [('runner.json',receipt),('sources.json',owned),('dependency-snapshot.json',deps)]:
            (out/filename).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(receipt,indent=2))
    return receipt['exit_code']
if __name__=='__main__':
    sys.exit(main())
