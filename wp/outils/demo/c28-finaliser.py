"""Sceller C28 après les vraies vérifications, sans écraser de reçu."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
from datetime import datetime, timezone
import c28


if __name__ == '__main__':
    assert len(sys.argv) == 1
    spec = importlib.util.spec_from_file_location('c28_verify', c28.ROOT/'wp/tests/demo/c28-verifier.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    offline = module.verify()
    live = module.verify(True)
    evidence = ['recette-finale.json','recette-finale-nettoyage.json','recette-finale-pack.png','natif-final.json','c14-regressions-finales.json','preservation-finale.json','unitaire-final.log','preparation-image.json','preparation-image.log','regression-finale.json','regression-finale.log','lint-final.json','NOTE.md','A-VOIR.md']
    c28.save('reception', {'at':datetime.now(timezone.utc).isoformat(), 'scope':'imagine-test-demo','sources':c28.sources(),'evidence':{name:hashlib.sha256((c28.OUT/name).read_bytes()).hexdigest() for name in evidence},'preseal_offline_checks':len(offline),'preseal_live_checks':len(live),'ready':True,'limits':['Validation visuelle de Ced attendue.','Paiements et remboursements synthétiques natifs, aucune passerelle ni transfert.','Exception Coming Soon sur la fiche fictive seulement ; autres pages boutique inchangées.','A32_PARTIAL_EVIDENCE connu et hors lot ; aucun paquet rescelle.','Les caches/logs non métier du cœur ne sont pas présentés comme une base intégralement identique.']})
    target = c28.OUT/'PRET'
    assert not target.exists()
    target.write_text('C28 prêt à relire — recette complète sur données fictives.\nVoir A-VOIR.md, NOTE.md et reception.json.\nNi clôture, ni validation visuelle, ni GO sur le réel.\n', encoding='utf-8')
    print('C28 PRET : vérificateurs offline et lecture native live verts.')
