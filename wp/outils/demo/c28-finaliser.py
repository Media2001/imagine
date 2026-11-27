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
    evidence = ['correction-recette-finale.json','correction-recette-finale-nettoyage.json','correction-recette-finale-pack.png','correction-natif-final.json','correction-fenetre-finale.json','correction-c14-final.json','correction-preservation-finale.json','correction-canaris-final.json','correction-unitaire-final.log','correction-image-finale.json','correction-image-finale.log','correction-regression-finale.json','correction-regression-finale.log','correction-lint-final.json','NOTE.md','A-VOIR.md']
    c28.save('reception-corrections', {'at':datetime.now(timezone.utc).isoformat(), 'scope':'imagine-test-demo','sources':c28.sources(),'evidence':{name:hashlib.sha256((c28.OUT/name).read_bytes()).hexdigest() for name in evidence},'preseal_offline_checks':len(offline),'preseal_live_checks':len(live),'ready':True,'limits':['Validation visuelle de Ced attendue.','Paiements et remboursements synthétiques natifs, aucune passerelle ni transfert.','Exception Coming Soon sur la fiche fictive seulement ; autres pages boutique inchangées.','A31 hors rejeu / journaux absents ; A32_PACKAGE_DRIFT connu hors lot ; aucun paquet rescelle.','Les caches/logs non métier du cœur ne sont pas présentés comme une base intégralement identique.','B11 reste BLOQUE sans PRET, aucune modification de son code ou de ses preuves.']})
    target = c28.OUT/'PRET'
    assert not target.exists()
    target.write_text('C28 corrections du 27/11 12h40 prêtes à relire — gardes serveur et non-reconstruction après panne prouvées.\nVoir A-VOIR.md, NOTE.md et reception-corrections.json.\nNi clôture, ni validation visuelle, ni GO sur le réel.\n', encoding='utf-8')
    print('C28 PRET : vérificateurs offline et lecture native live verts.')
