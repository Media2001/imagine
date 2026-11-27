"""C29 final evidence, no historical receipt writes and no demo mutation."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
import re
import subprocess
from datetime import datetime,timezone
import c29
ROOT,OUT=c29.ROOT,c29.OUT

def lint():
    files=['wp/plugins/imagine-site/ContactBrevoRegles.php','wp/plugins/imagine-site/ContactBrevo.php','wp/plugins/imagine-site/imagine-site.php','wp/plugins/imagine-site/tests/ContactBrevoC29Test.php','wp/plugins/imagine-site/tests/fixtures/c29-cases.php','wp/tests/demo/c29-pure.php','wp/tests/demo/c29-runtime.php','wp/tests/demo/c29-attendus.php','wp/tests/demo/c29-observer.php']
    rows=[]
    for file in files:
        rows.append(c29.docker('run','--rm','--pull','never','--network','none','--read-only',
            '--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
            '--entrypoint','php','imagine-tests-t01:1','-l','/repo/'+file))
    c29.save('lint-final-V2',{'files':files,'exit':max(r.returncode for r in rows),'stdout':''.join(r.stdout for r in rows),'stderr':''.join(r.stderr for r in rows)})
    assert all(r.returncode==0 and not r.stderr for r in rows)
    print('PHP lint',len(files),'PASS')

def finish():
    assert not (OUT/'PRET').exists() and not (OUT/'reception-V2.json').exists()
    log=OUT/'proof-reader-tests-V2.log'
    with log.open('xb') as stream:
        r=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo/c29-proof-tests.py')],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    assert r.returncode==0,log.read_text(encoding='utf-8')
    spec=importlib.util.spec_from_file_location('c29_verify',OUT/'verifier.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    table=(OUT/'attendus-C09.md').read_text(encoding='utf-8')
    codes=re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|',table,re.M)
    assert len(codes)==len(set(codes))==27
    names=['pure-reception-V2.json','native-reception-V2.json','http-reception-V2.json','http-reception-V2-baseline.json','http-reception-V2.png',
        'red-slice1-V2.json','red-slice2-V2.json','green-slice1-V2.json','green-slice2-V2.json','red-native-V2.json','red-native-matrix-V2.json','red-screen-V2.json','red-settings-V2.json',
        'image-rebuilt-V2.json','image-rebuilt-V2.log','replay-final-V2.json','replay-final-V2.log',
        'reception-complement-voisins-V2.json','reception-complement-voisins-V2.log','sources-officielles-V2.json','lint-final-V2.json','proof-reader-tests-V2.log',
        'demo-tarifs-V2.json','demo-tarifs-idempotent-V2.json','NOTE.md','A-VOIR.md','attendus-C09.md','verifier.py',
        'recovery-setup-shutdown-V2.json','recovery-setup-shutdown2-V2.json','recovery-HTTP-fixture-V2.json','recovery-HTTP-finally-interrupted-V2.json']
    m={'scope':'imagine-test-demo','ready':True,'at':datetime.now(timezone.utc).isoformat(),'sources':c29.sources(),
        'evidence':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names},
        'pure':'pure-reception-V2.json','native':'native-reception-V2.json','http':'http-reception-V2.json','image':'image-rebuilt-V2.json','replay':'replay-final-V2.json','neighbors':'reception-complement-voisins-V2.json',
        'readme_section':hashlib.sha256(v.section().encode()).hexdigest(),
        'unknowns':['Grille réelle et rattachement des tarifs non arrêtés : liste fermée vide hors réglage explicite.','Statut et tarif des bénéficiaires identifiés offerts/groupés inconnus.','Noms des attributs Brevo et branchement non définis.'],
        'limits':['No Brevo account, activation, connection, key, queue, scheduler, Odoo or real data.','Read-only consultation; separate explicit Settings API configuration is intentionally writable.','C29 render path zero SQL-write/HTTP/mail attempts; native WordPress bootstrap has individually evidenced volatile cache expiries.','Historical interrupted HTTP experiment recovered exact original business/profile/scheduler checksums; original session-byte equality for that experiment is not claimed. Final HTTP session restoration is exact to its own baseline.','B11 UI_save_verified=false is unchanged; A31/A32 known foreign packet failures remain untouched.']}
    v.verify(False,m,False);v.verify(True,m,False)
    c29.save('reception-V2',m)
    with (OUT/'PRET').open('x',encoding='utf-8') as stream:
        stream.write('C29 PRET TECHNIQUE — reception-V2.json, NOTE.md et A-VOIR.md.\nProjection pure et aperçu en lecture seule ; aucune transmission.\nImage reconstruite, suite canonique et réceptions pure/native/HTTP vertes ; complément voisins dans C29, historiques B12/B11/C28/C27 intacts.\nNi clôture, ni validation visuelle, ni GO sur le réel.\n')
    v.verify(False);v.verify(True)
if __name__=='__main__':
    assert sys.argv[1:] in [[],['lint']]
    lint() if sys.argv[1:] else finish()
