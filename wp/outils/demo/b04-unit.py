"""B04: real root PHPUnit + C12, existing T01 dependencies, no host install."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import uuid
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b04_c11_unit', HERE/'c11-unit.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
docker = bench.docker
ROOT = bench.ROOT
PROOF = ROOT/'production/B-04'

def run(phase='final'):
    name='imagine-b04-unit-'+uuid.uuid4().hex
    owner=uuid.uuid4().hex
    image=json.loads(docker('image','inspect','imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image']=='1'
    source=subprocess.run(['wsl.exe','-d','Ubuntu','--','wslpath','-a','-u',str(ROOT/'wp').replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    destination=subprocess.run(['wsl.exe','-d','Ubuntu','--','wslpath','-a','-u',str(PROOF).replace('\\','/')],capture_output=True,text=True,check=True).stdout.strip()
    result={'scope':'isolated-B04-PHPUnit','image':image['Id'],'runs':[]}
    created=False
    try:
        docker('create','--name',name,'--label','org.imagine.b04-unit='+owner,'--pull','never',
            '--network','none','--read-only','--mount','type=bind,source='+source+',target=/repo/wp,readonly',
            '--tmpfs','/tmp:rw,nosuid,nodev,size=256m,mode=1777','--user','65534:65534',
            '--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128',
            '--memory','512m','--cpus','2','--no-healthcheck','--log-driver','none',
            '--entrypoint','sleep',image['Id'],'300')
        created=True
        info=json.loads(docker('inspect',name).stdout)[0]
        host=info['HostConfig']
        assert host['NetworkMode']=='none' and host['ReadonlyRootfs'] and not host['Privileged']
        assert len(info['Mounts'])==1 and not info['Mounts'][0]['RW'] and info['Mounts'][0]['Destination']=='/repo/wp'
        assert not host.get('PortBindings') and not info['Config'].get('ExposedPorts')
        result['isolation_verified']=True
        docker('start',name)
        for label,config in [('root','phpunit.xml'),('c12','phpunit.c12.xml'),('b04','phpunit.b04.xml')]:
            args=['exec','--env','TMPDIR=/tmp',name,'php','/opt/t01/imagine-site/vendor/bin/phpunit',
                '--configuration','/repo/wp/plugins/imagine-site/'+config,
                '--bootstrap','/repo/wp/tests/demo/b04-unit-bootstrap.php',
                '--do-not-cache-result','--fail-on-warning','--fail-on-risky','--fail-on-deprecation',
                '--fail-on-skipped','--fail-on-incomplete','--log-junit','/tmp/'+label+'.xml']
            r=docker(*args,check=False)
            log=PROOF/('phpunit-'+label+'-'+phase+'.log')
            log.write_text(r.stdout+r.stderr,encoding='utf-8')
            print(r.stdout+r.stderr,flush=True)
            result['runs'].append({'suite':label,'config':config,'exit':r.returncode,'log':log.name})
            # Docker cp cannot read a tmpfs file on this daemon; stream PHP over stdin.
            xml=subprocess.run(['wsl.exe','-d','Ubuntu','--','docker','exec','-i',name,'php'],
                input='<?php readfile('+json.dumps('/tmp/'+label+'.xml')+');',
                capture_output=True,text=True,encoding='utf-8',check=True).stdout
            assert xml.lstrip().startswith('<?xml')
            (PROOF/('junit-'+label+'-'+phase+'.xml')).write_text(xml,encoding='utf-8')
            if r.returncode: raise RuntimeError('PHPUnit '+label+' failed')
    finally:
        if created:
            info=json.loads(docker('inspect',name).stdout)[0]
            assert info['Config']['Labels'].get('org.imagine.b04-unit')==owner
            docker('container','rm','-f',name)
            absent=docker('inspect',name,check=False)
            result['owned_container_removed']=absent.returncode!=0 and 'no such' in (absent.stdout+absent.stderr).lower()
            assert result['owned_container_removed']
        (PROOF/('unit-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert all(r['exit']==0 for r in result['runs']) and len(result['runs'])==3
    print(json.dumps(result),flush=True)

if __name__=='__main__': run(sys.argv[1] if len(sys.argv)>1 else 'final')
