"""B05 targeted PHP lint/PSR12 in the prepared offline image."""
import importlib.util, json, sys, uuid
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('b05_unit',Path(__file__).with_name('b05-unit.py'))
u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)

def run(label):
    name,owner='imagine-b05-quality-'+uuid.uuid4().hex,uuid.uuid4().hex
    out=u.PROOF/(label+'.json'); assert not out.exists()
    image=json.loads(u.docker('image','inspect','imagine-tests-t01:1').stdout)[0]
    import subprocess
    source=subprocess.run(['wsl.exe','-d','Ubuntu','--','wslpath','-a','-u',str(u.ROOT/'wp').replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    checks={}; created=False
    files=['plugins/imagine-site/Partenaires.php','themes/imagine/functions.php','themes/imagine/archive-imagine_partenaire.php','themes/imagine/inc/partenaires.php','wp/tests/demo/b05-runtime.php']
    files=[f.removeprefix('wp/') for f in files]
    try:
        u.docker('create','--name',name,'--label','org.imagine.b05-quality='+owner,'--pull','never','--network','none','--read-only','--mount','type=bind,source='+source+',target=/repo/wp,readonly','--tmpfs','/tmp:rw,nosuid,nodev,size=64m,mode=1777','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','sleep',image['Id'],'180')
        created=True
        info=json.loads(u.docker('inspect',name).stdout)[0]
        assert info['HostConfig']['NetworkMode']=='none' and info['HostConfig']['ReadonlyRootfs'] and not info['Mounts'][0]['RW']
        u.docker('start',name)
        for f in files+['tests/demo/b05-offline.php']:
            r=u.docker('exec',name,'php','-l','/repo/wp/'+f,check=False)
            checks['lint:'+f]=r.returncode==0
        r=u.docker('exec',name,'php','/opt/t01/imagine-site/vendor/bin/phpcs','-q','--standard=PSR12','--warning-severity=0',*['/repo/wp/'+f for f in files],check=False)
        checks['PSR12_production_et_runtime']=r.returncode==0 and not r.stdout.strip() and not r.stderr.strip()
        (u.PROOF/(label+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8')
    finally:
        if created:
            info=json.loads(u.docker('inspect',name).stdout)[0]
            assert info['Config']['Labels']['org.imagine.b05-quality']==owner
            u.docker('container','rm','-f',name)
            r=u.docker('inspect',name,check=False)
            checks['owned_container_removed']=r.returncode!=0 and 'no such' in (r.stdout+r.stderr).lower()
        failures=[k for k,v in checks.items() if v is not True]
        data=dict(checks=checks,total=len(checks),failures=failures,image=image['Id'])
        out.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data)); assert not failures
if __name__=='__main__': run(sys.argv[1])
