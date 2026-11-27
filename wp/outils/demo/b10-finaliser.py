"""B10 : lier la réception finale puis vérifier localement et relire le site avant PRET."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import b10

ROOT,OUT=b10.ROOT,b10.OUT
assert not (OUT/'PRET').exists() and not (OUT/'reception.json').exists()
paths=[]
for pattern in ['wp/plugins/imagine-site/PointsVente*.php','wp/plugins/imagine-site/tests/PointsVente*.php','wp/outils/demo/b10*.py','wp/outils/demo/b10*.php','wp/tests/demo/b10*.py','wp/tests/demo/b10*.php']:
    paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
for name in ['NOTE.md','A-VOIR.md','mapping-exemple.json','commerces-fictifs.csv','unitaire-reception.log','natif-reception.json','recette-reception.json','recette-reception-nettoyage.json','page-navigation.json','installation-reception.json','preparation-reception.log','regression-reception.log','page-mobile.png']:
    paths.append(OUT/name)
readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
section='## B-10 — points de vente'+readme.split('## B-10 — points de vente',1)[1]
payload={'scope':'imagine-test-demo','at':datetime.now(timezone.utc).isoformat(),'python':sys.version,'bootstrap_block':b10.BLOCK,'readme_section':section,'sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}}
with (OUT/'reception.json').open('x',encoding='utf-8') as f:json.dump(payload,f,ensure_ascii=False,indent=2)
logs=[]
for flags in [[],['--live']]:
    p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo/b10-verifier.py'),*flags],capture_output=True,encoding='utf-8',env={**__import__('os').environ,'PYTHONIOENCODING':'utf-8'})
    logs.append(p.stdout+p.stderr)
    print(p.stdout+p.stderr)
    assert p.returncode==0, 'Vérification refusée ; aucun PRET déposé'
with (OUT/'verification-finale.log').open('x',encoding='utf-8') as f:f.write('\n'.join(logs))
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('B-10 prêt à relire. Sources et preuves liées par reception.json ; vérification autonome et readback du seul site imagine-test-demo au vert. Validation visuelle de Ced attendue. Voir A-VOIR.md et NOTE.md. Aucun GO sur le réel.\n')
print('B10 PRET :',len(payload['sha256']),'empreintes, vérifications offline et live PASS')
