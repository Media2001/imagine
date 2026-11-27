"""Successor reception under the 16h30 bootstrap contract; old receipts remain raw."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
import b12
ROOT, OUT = b12.ROOT, b12.OUT
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def finish():
    import importlib.util
    spec = importlib.util.spec_from_file_location('v', ROOT/'wp/tests/demo/b12-verifier.py')
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    assert not (OUT/'PRET').exists() and not (OUT/'reception-contrat-V2.json').exists()
    names = []
    for script in ['b12-proof-tests.py','b12-correction-proof-tests.py','b12-contract-proof-tests.py']:
        log = 'contrat-' + script.removesuffix('.py') + '-V2.log'
        with (OUT/log).open('xb') as stream:
            r = subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo'/script)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        assert r.returncode==0, (OUT/log).read_text(encoding='utf-8')
        names.append(log)
    names += ['contrat-image-V2.json','contrat-image-V2.log','contrat-replay-V2.json','contrat-replay-V2.log','contrat-native-final-V2.json','contrat-mutation-final-V2.json','contrat-routes-final-V2.json','contrat-lint-V2.json','correction-red-route-V2.json','correction-mutation-case-V2-rejet.json','correction-mutation-case-V2.json','PRET-avant-corrections-V2','PRET-avant-contrat-V2','reception-V2.json','reception-corrections-V2.json','NOTE.md','A-VOIR.md']
    m = {'scope':'imagine-test-demo','ready':True,'contract_version':1,'at':datetime.now(timezone.utc).isoformat(),'sources':b12.contract_sources(),'bootstrap_contract':b12.contract_block(),'readme_section':hashlib.sha256(b12.readme_section().encode()).hexdigest(),'evidence':{n:sha(OUT/n) for n in names},'routes':'contrat-routes-final-V2.json','green':'contrat-native-final-V2.json','mutation':'contrat-mutation-final-V2.json','image':'contrat-image-V2.json','replay':'contrat-replay-V2.json','lint':'contrat-lint-V2.json','arbitration':'A-FAIRE-2.md 16h30 / docs/arbitrages-2026-11-27.md passage 16h: instruction 3 replaced, owned files and exact own bootstrap block; no dependency on neighboring whole bootstrap or PRET','limits':['Native WP-CLI in-process REST, not browser UI or external authenticated HTTP.','Business restored; AUTO_INCREMENT may advance.','B11/C29 contract migration belongs to parent; no neighbor production files changed.','Historical B11/C28/C29 readers may remain red as explicitly accepted at 16h30; no silent reseal.','A31/A32 failures untouched; no real data, mail, payments or third-party transport.']}
    v.verify_contract(False,m,False)
    v.verify_contract(True,m,False)
    b12.save('reception-contrat-V2',m)
    with (OUT/'PRET').open('x',encoding='utf-8') as stream:
        stream.write('B12 PRET TECHNIQUE — reception-contrat-V2.json, NOTE.md, A-VOIR.md.\nArbitrage 16h30 appliqué : fichiers propres, bloc B12 exact unique, section README B12 ; aucun sceau entier du bootstrap ni dépendance aux PRET voisins.\nRoutes natives canonique/MAJ/mixed avec/sans cache et permissions, mutation réelle détectée puis restaurée, image reconstruite, rejeu frais.\nAnciens reçus et PRET archivés bruts, sans resceau silencieux. Ni clôture, validation visuelle ou GO sur le réel.\n')
    v.verify(False)
    v.verify(True)

if __name__ == '__main__': finish()
