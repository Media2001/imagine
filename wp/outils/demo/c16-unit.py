"""C16 PHPUnit, existing offline image; no host/commercial install."""
from pathlib import Path
import json
import subprocess
import sys
import uuid
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT/'production/C-16'

def run(label='final', selection='CommandeReglesTest'):
    def docker(*args, check=True):
        p = subprocess.run(['wsl.exe','-d','Ubuntu','--exec','docker',*args],capture_output=True,text=True,encoding='utf-8')
        if check and p.returncode: raise RuntimeError(p.stderr+p.stdout)
        return p
    source=subprocess.run(['wsl.exe','-d','Ubuntu','--','wslpath','-a','-u',str(ROOT/'wp').replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    image=json.loads(docker('image','inspect','imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image']=='1'
    name='imagine-c16-unit-'+uuid.uuid4().hex
    result={}
    try:
        docker('create','--name',name,'--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,nosuid,nodev,size=256m,mode=1777','--mount','type=bind,source='+source+',target=/repo/wp,readonly','--entrypoint','php',image['Id'],'/repo/wp/tests/demo/c16-unit-runtime.php',selection)
        info=json.loads(docker('inspect',name).stdout)[0]
        assert info['HostConfig']['NetworkMode']=='none' and info['HostConfig']['ReadonlyRootfs'] and not info['Mounts'][0]['RW']
        p=docker('start','-a',name,check=False)
        result={'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'network':'none','image':image['Id'],'selection':selection}
        print(p.stdout+p.stderr)
    finally:
        docker('rm','-f',name)
        absent=docker('inspect',name,check=False)
        result['removed']=bool(absent.returncode and 'no such' in absent.stderr.lower())
        PROOF.mkdir(parents=True,exist_ok=True)
        (PROOF/(label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result['exit']
if __name__=='__main__':
    selection=sys.argv[2] if len(sys.argv)>2 else 'CommandeReglesTest'
    sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'final','' if selection=='--root' else selection))
