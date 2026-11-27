"""Réception neuve B11 après la politique 13h30 ; refuse toute réécriture d'historique."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
import b11

if __name__=='__main__':
    assert len(sys.argv)==1 and not (b11.OUT/'PRET').exists()
    load=lambda n:json.loads((b11.OUT/n).read_text(encoding='utf-8'))
    digest=lambda n:hashlib.sha256((b11.OUT/n).read_bytes()).hexdigest()
    historical={}
    for old_name in ['reception.json','reception-corrections-V2.json']:
        old=load(old_name)
        for name,sha in {**old.get('historical_receipts',{}),**old['evidence']}.items():
            if name not in ['NOTE.md','A-VOIR.md']:
                assert digest(name)==sha,('Historical evidence drift',name)
                historical[name]=sha
        historical[old_name]=digest(old_name)
    names=['politique1330-final-V2.json','politique1330-final-V2-details.json','politique1330-final-V2-nettoyage.json',
        'politique1330-natif-V2.json','politique1330-ecritures-V2.json','politique1330-editeurs-final-V2.json',
        'politique1330-unitaire-V2.log','politique1330-preuves-V2.log','politique1330-preuves-red-V2.log',
        'politique1330-image-V2.json','politique1330-image-V2.log','politique1330-rejeu-V2.json','politique1330-rejeu-V2.log',
        'politique1330-voisins-V2.json','NOTE.md','A-VOIR.md']
    details=load('politique1330-final-V2-details.json')
    explicit=sorted(set().union(*(set(x['absent_to_exact_default']) for x in details['settings_evidence'])))
    manifest={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo',
        'policy':'A-FAIRE-2 2026-11-27 13h30','ready':True,'status':'PASS',
        'sources':b11.sources(),'evidence':{n:digest(n) for n in names},'historical_receipts':historical,
        'absent_to_exact_default':explicit,'limits':['Saisie/enregistrement/reload UI des deux éditeurs non automatisés ; parcours Ced dans A-VOIR.',
            'Atteignabilité établie par lecture du code natif installé et enregistrement/rendu réels de la boîte ; aucun défaut de déclaration.',
            'Persistance : vrai hook save_post et témoin backend transactionnel 8/8, non présentés comme preuve UI.',
            'Collage URL dans le corps : futur B12, non implémenté ici. Catch Paywall intact. A31/A32 hors périmètre.']}
    spec=importlib.util.spec_from_file_location('verify1330',b11.ROOT/'wp/tests/demo/b11-verifier1330.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.verify(False,manifest,False);module.verify(True,manifest,False)
    b11.save('reception-politique1330-V2',manifest)
    with (b11.OUT/'PRET').open('x',encoding='utf-8') as stream:
        stream.write('B11 PRET TECHNIQUE — politique du 27 novembre 2026, 13h30.\nRéception courante : reception-politique1330-V2.json ; NOTE.md et A-VOIR.md.\nPersistance backend prouvée ; saisie UI/reload à parcourir par Ced. Ni validation visuelle, ni clôture, ni GO réel.\n')
    print('B11 PRET : nouvelle réception vérifiée offline et live ; historiques intacts.')
