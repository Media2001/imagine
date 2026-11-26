"""C24 : cible fictive gardée, preuves V2 immuables et banc hors réseau."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, subprocess, uuid
from pathlib import Path
from datetime import datetime, timezone
import b06
ROOT, wp, profils, hashes, state = b06.ROOT, b06.wp, b06.profils, b06.hashes, b06.state
php_json = b06.b05.php_json
PROOF = ROOT/'production/C-24'
NAMES = ['plugins/imagine-site/'+n for n in ['PersonnalisationRegles.php','Personnalisation.php','PersonnalisationReglages.php','PersonnalisationConfidentialite.php','imagine-site.php']]
BLOCK = "require_once __DIR__ . '/PersonnalisationRegles.php';\nrequire_once __DIR__ . '/Personnalisation.php';\nrequire_once __DIR__ . '/PersonnalisationReglages.php';\nrequire_once __DIR__ . '/PersonnalisationConfidentialite.php';\nPersonnalisation::register();\nPersonnalisationReglages::register();\nPersonnalisationConfidentialite::register();\n\n"
guard = b06.guard

def save(label, data):
    assert label.endswith('-V2') and label.replace('-','').isalnum()
    PROOF.mkdir(parents=True, exist_ok=True)
    p=PROOF/(label+'.json'); assert not p.exists(), p
    p.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),scope='imagine-test-demo',**data),ensure_ascii=False,indent=2),encoding='utf-8')

def rules(label):
    def docker(*args,check=True):
        p=subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args],capture_output=True,text=True,encoding='utf-8')
        if check: assert p.returncode==0,p.stderr
        return p
    image=json.loads(docker('image','inspect','imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image']=='1'
    name='imagine-c24-pure-'+uuid.uuid4().hex
    docker('create','--name',name,'--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php',image['Id'],'/repo/wp/tests/demo/c24-rules.php')
    try:
        info=json.loads(docker('inspect',name).stdout)[0]
        assert info['HostConfig']['NetworkMode']=='none' and info['HostConfig']['ReadonlyRootfs']
        assert len(info['Mounts'])==1 and not info['Mounts'][0]['RW'] and not info['HostConfig']['PortBindings']
        p=docker('start','-a',name,check=False)
        data=json.loads(p.stdout); data.update(exit=p.returncode,stderr=p.stderr,image=image['Id'])
    finally:
        docker('rm','-f',name)
        absent=docker('inspect',name,check=False)
        assert absent.returncode and 'no such' in absent.stderr.lower()
    data['container_removed']=True
    save(label,data); print(json.dumps(data,ensure_ascii=False))
    assert not data['failures'] and not data['exit'] and not data['stderr']

def baseline(label):
    save(label,{'identity':guard(),'state':state(),'sources':hashes(NAMES)})

def deploy(label):
    identity=guard(); before=state()
    bootstrap=NAMES[-1]
    remote=wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+bootstrap+'"));')
    local=(ROOT/'wp'/bootstrap).read_text(encoding='utf-8')
    assert remote==local or remote==local.replace(BLOCK,''),'Bootstrap partagé divergent'
    for n in NAMES: profils.b00.upload(n,(ROOT/'wp'/n).read_bytes())
    actual=hashes(NAMES)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in NAMES}
    assert before==state()
    save(label,{'identity':identity,'sources':actual,'state_preserved':True})

def runtime(label, mutation=''):
    guard(); source=ROOT/'wp/tests/demo/c24-runtime.php'; target='imagine-demo-build/c24-runtime.php'
    profils.b00.upload(target,source.read_bytes())
    assert hashes([target])[target]==hashlib.sha256(source.read_bytes()).hexdigest()
    before=state()
    p=profils.b00.wp('eval','$GLOBALS["imagine_c24_mutation"]='+json.dumps(mutation)+';require WP_CONTENT_DIR."/'+target+'";',check=False)
    data=json.loads(p['stdout']);data.update(exit=p['code'],stderr=p['stderr'],state_preserved=before==state(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    save(label,data);print(json.dumps(data,ensure_ascii=False))
    assert not data['exit'] and not data['failures'] and not data['stderr'] and data['state_preserved']

if __name__=='__main__':
    assert sys.argv[1] in ('rules','baseline','deploy','runtime')
    globals()[sys.argv[1]](*sys.argv[2:])
