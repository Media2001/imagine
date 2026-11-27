"""B12 final evidence only; all historical neighbor packets remain untouched."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime,timezone
import b12
ROOT,OUT=b12.ROOT,b12.OUT

def lint():
    files=['wp/plugins/imagine-site/IntegrationsCorps.php','wp/plugins/imagine-site/imagine-site.php','wp/plugins/imagine-site/tests/IntegrationsCorpsB12Test.php','wp/plugins/imagine-site/tests/IntegrationsCorpsB12Stubs.php','wp/tests/demo/b12-runtime.php']
    prefix=['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1']
    rows=[subprocess.run(prefix+['-l','/repo/'+n],capture_output=True,encoding='utf-8') for n in files]
    b12.save('lint-final-V2',{'files':files,'exit':max(r.returncode for r in rows),'stdout':''.join(r.stdout for r in rows),'stderr':''.join(r.stderr for r in rows)})
    assert all(r.returncode==0 and not r.stderr for r in rows)
    print('PHP syntax:',len(files),'PASS')

def finish():
    assert not (OUT/'PRET').exists() and not (OUT/'reception-V2.json').exists()
    log=OUT/'proof-reader-tests-V2.log'
    with log.open('xb') as stream:
        r=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo/b12-proof-tests.py')],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    assert r.returncode==0,log.read_text(encoding='utf-8')
    names=['native-reception-V2.json','mutation-reception-V2.json','red-verrou-absent-V2.json','red-mutation-native-V2.json','image-rebuilt-V2.json','image-rebuilt-V2.log','replay-corrected-V2.json','replay-corrected-V2.log','reception-complement-voisins-V2.json','reception-complement-voisins-V2.log','reception-complement-voisins-V2-B11-native.json','reception-complement-voisins-V2-C28-native.json','sources-officielles-V2.json','lint-final-V2.json','proof-reader-tests-V2.log','NOTE.md','A-VOIR.md']
    m={'scope':'imagine-test-demo','ready':True,'at':datetime.now(timezone.utc).isoformat(),'sources':b12.sources(),'evidence':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names},'green':'native-reception-V2.json','mutation':'mutation-reception-V2.json','neighbors':'reception-complement-voisins-V2.json','readme_section':hashlib.sha256((ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## B-12 — aucun appel sortant depuis le corps',1)[1].strip().encode()).hexdigest(),'limits':['Native WordPress execution via WP-CLI: real save/cache/render/REST router, not a manual editor UI recording.','Exact business rows restored; InnoDB AUTO_INCREMENT counters may advance despite rollback.','B11 UI_save_verified=false remains the accepted 13h30 boundary.','A31 A31_PARTIAL_EVIDENCE and A32 A32_PACKAGE_DRIFT are foreign packet failures; untouched.']}
    spec=importlib.util.spec_from_file_location('b12_verify',ROOT/'wp/tests/demo/b12-verifier.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    v.verify(False,m,False);v.verify(True,m,False)
    b12.save('reception-V2',m)
    with (OUT/'PRET').open('x',encoding='utf-8') as stream:stream.write('B12 PRET TECHNIQUE — reception-V2.json, NOTE.md et A-VOIR.md.\nRejeu natif et mutation B00 verts ; réception complémentaire B11/C27/C28 conservant les historiques.\nNi validation visuelle, ni clôture, ni GO sur le réel.\n')
    v.verify(False);v.verify(True)
if __name__=='__main__':
    assert sys.argv[1:] in [[],['lint']]
    lint() if sys.argv[1:] else finish()
