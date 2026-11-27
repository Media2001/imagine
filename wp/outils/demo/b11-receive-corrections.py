"""Réception complémentaire ROUGE B11, après vrai rejeu ; jamais de PRET sur un blocage."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
from datetime import datetime,timezone
import b11

if __name__=='__main__':
    assert len(sys.argv)==1 and not (b11.OUT/'PRET').exists()
    load=lambda n:json.loads((b11.OUT/n).read_text(encoding='utf-8'))
    recipe=load('corrections-final-V2.json')
    assert recipe['error'] is not None or recipe['failures']>0
    assert all(recipe['cleanup'].values()) and recipe['sources']==b11.sources()
    assert load('corrections-image-V2.json')['exit']==0
    assert load('corrections-rejeu-V2.json')['exit']==0
    names=['corrections-final-V2.json','corrections-final-V2-details.json','corrections-final-V2-nettoyage.json','corrections-natif-V2.json','corrections-ecritures-V2.json','corrections-unitaire-V2.log','corrections-preuves-unitaires-V2.log','corrections-image-V2.json','corrections-image-V2.log','corrections-rejeu-V2.json','corrections-rejeu-V2.log','NOTE.md','A-VOIR.md']
    names.extend(p.name for p in b11.OUT.glob('corrections-final-V2-editor-*.png'))
    old=load('reception.json')
    historical={n:h for n,h in old['evidence'].items() if n not in ['NOTE.md','A-VOIR.md']}
    assert all(hashlib.sha256((b11.OUT/n).read_bytes()).hexdigest()==h for n,h in historical.items())
    historical['reception.json']=hashlib.sha256((b11.OUT/'reception.json').read_bytes()).hexdigest()
    b11.save('reception-corrections-V2',{'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','ready':False,'status':'BLOCKED','sources':b11.sources(),'evidence':{n:hashlib.sha256((b11.OUT/n).read_bytes()).hexdigest() for n in names},'historical_receipts':historical,'blockers':['Vrai formulaire : cinq autres options absentes sont créées ; conservation exacte non tenue.','Éditeurs blocs livrés : champs B11 masqués/inaccessibles pendant le parcours réel ; persistance/reload UI non validés.','OFF/ON, effacement et mutation no-persist via éditeurs non terminés ; témoin backend transactionnel distinct, sans substitution.'],'limits':['oEmbed natif réactivable par collage URL dans le corps : consigne seulement.','Catch Throwable Paywall hors B11 : erreur de code masquée en refus ; aucune modification.','A32 partiel connu hors lot ; aucun resceau autre lot.']})
    print('B11 réception complémentaire BLOCKED conservée ; aucun PRET.')
