"""B05 isolated real WordPress HTML engine, no network/site/database."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, uuid
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-05'

def docker(*args, check=True):
    return subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args], capture_output=True, text=True, encoding='utf-8', check=check)

def run(label, case='all'):
    path = PROOF / (label + '.json')
    assert label.endswith('-V2') and not path.exists()
    image = json.loads(docker('image','inspect','wordpress:php8.3-fpm-alpine').stdout)[0]
    source = subprocess.run(['wsl.exe','-d','Ubuntu','--','wslpath','-a','-u',str(ROOT/'wp').replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    name, owner = 'imagine-b05-unit-'+uuid.uuid4().hex, uuid.uuid4().hex
    data = {'scope':'isolated-offline-B05','image':image['Id'],'case':case}
    created = False
    try:
        docker('create','--name',name,'--label','org.imagine.b05-unit='+owner,'--pull','never','--network','none','--read-only','--mount','type=bind,source='+source+',target=/repo/wp,readonly','--tmpfs','/tmp:rw,nosuid,nodev,size=64m,mode=1777','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','64','--memory','256m','--cpus','1','--no-healthcheck','--log-driver','none','--entrypoint','php',image['Id'],'/repo/wp/tests/demo/b05-offline.php',case)
        created = True
        info = json.loads(docker('inspect',name).stdout)[0]
        assert info['HostConfig']['NetworkMode']=='none' and info['HostConfig']['ReadonlyRootfs']
        assert len(info['Mounts'])==2 and all(not m['RW'] for m in info['Mounts'] if m['Type']=='bind')
        assert not info['HostConfig'].get('PortBindings')
        data['isolation_verified'] = True
        result = docker('start','-a',name,check=False)
        after = json.loads(docker('inspect',name).stdout)[0]
        data.update(exit=after['State']['ExitCode'],stdout=result.stdout,stderr=result.stderr)
        print(result.stdout+result.stderr,flush=True)
        data['source_sha256'] = {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'wp/tests/demo/b05-offline.php', ROOT/'wp/themes/imagine/functions.php',ROOT/'wp/plugins/imagine-site/Partenaires.php']}
    finally:
        if created:
            info = json.loads(docker('inspect',name).stdout)[0]
            assert info['Config']['Labels']['org.imagine.b05-unit']==owner
            docker('container','rm',name)
            missing = docker('inspect',name,check=False)
            data['owned_container_removed'] = missing.returncode!=0 and 'no such' in (missing.stdout+missing.stderr).lower()
            assert data['owned_container_removed']
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    assert data['exit']==0 and not data['stderr'], 'B05 isolated tests failed: '+label

if __name__=='__main__': run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'all')
