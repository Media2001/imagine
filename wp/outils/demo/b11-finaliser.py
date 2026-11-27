"""B11 réception : vérifications réelles, puis manifeste et PRET sans écraser de reçu."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
from datetime import datetime,timezone
import b11

if __name__=='__main__':
    assert len(sys.argv)==1
    spec=importlib.util.spec_from_file_location('b11_verify',b11.ROOT/'wp/tests/demo/b11-verifier.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    offline=module.verify();live=module.verify(True)
    evidence=['recette-finale.json','recette-finale-nettoyage.json','natif-final.json','unitaire-final.log','preparation-image.json','preparation-image.log','regression-finale.json','regression-finale.log','NOTE.md','A-VOIR.md']
    manifest={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','sources':b11.sources(),'evidence':{n:hashlib.sha256((b11.OUT/n).read_bytes()).hexdigest() for n in evidence},'offline_checks':len(offline),'live_checks':len(live),'ready':True,'limits':['Validation visuelle de Ced attendue.','Aucun consentement ni lecteur tiers intégré.','Tentatives Novamira ambiantes bloquées et distinguées du zéro B11.','Premier essai : empreinte usermeta administrateur résiduelle déclarée ; les recettes suivantes restaurent leur préimage complète.']}
    b11.save('reception',manifest)
    target=b11.OUT/'PRET'
    assert not target.exists()
    target.write_text('B11 prêt à relire — code et recette fictive ; ni validation visuelle ni GO sur le réel.\nVoir A-VOIR.md, NOTE.md et reception.json.\n',encoding='utf-8')
    print('B11 PRET — réception offline et lecture live vérifiées')
