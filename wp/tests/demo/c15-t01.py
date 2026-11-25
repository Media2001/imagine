"""C15: real PHPUnit in the prepared, disconnected T01 image."""
from pathlib import Path
import json
import subprocess
import sys
import uuid
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]

def run(label, selection='EcheancesReglesTest'):
    def docker(*args, check=True):
        p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', *args], capture_output=True, text=True, encoding='utf-8')
        if check and p.returncode:
            raise RuntimeError(p.stderr + p.stdout)
        return p
    image = json.loads(docker('image', 'inspect', 'imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image'] == '1'
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT/'wp').replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    name = 'imagine-c15-phpunit-' + uuid.uuid4().hex
    # Actual T01 discovery/coverage; only the owned package is executed.
    try:
        docker('create','--name',name,'--label','org.imagine.c15-proof=1','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,nosuid,nodev,size=256m,mode=1777','--mount','type=bind,source='+source+',target=/repo/wp,readonly','--entrypoint','php',image['Id'],'/repo/wp/tests/demo/c15-t01-runtime.php',selection)
        inspect=json.loads(docker('inspect',name).stdout)[0]
        assert inspect['HostConfig']['NetworkMode']=='none' and inspect['HostConfig']['ReadonlyRootfs'] and not inspect['Mounts'][0]['RW']
        p=docker('start','-a',name,check=False)
        result={'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'network':'none','image':image['Id'],'selection':selection}
        (ROOT/'production/C-15'/f'{label}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(p.stdout+p.stderr)
        return p.returncode
    finally:
        docker('rm','-f',name)
        missing=docker('inspect',name,check=False)
        assert missing.returncode and 'no such' in missing.stderr.lower()

if __name__=='__main__':
    sys.exit(run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'EcheancesReglesTest'))
