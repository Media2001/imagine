import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
evidence=['A-VOIR.md','finaliser.py','offline.py','native-corrections-final-V2.json','browser-corrections-final-V2.json','browser-corrections-final-V2.png','standard-V2.json','image-corrections-V2.json','image-corrections-V2.log','replay-corrections-final-V2.json','replay-corrections-final-V2.log','controleurs-red-green-corrections-V2.json','cible-corrections-V2.json','cible-corrections-V2.log','voisins-preimage-corrections-V2.json','voisins-preservation-corrections-V2.json']
evidence += [r['response'] for r in v.load('browser-corrections-final-V2.json')['rows']]
# Préservation des voisins constatée une fois au sceau, pas condition permanente.
import hashlib
protected=v.load('voisins-preimage-corrections-V2.json')
text=(v.ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
current={name:(hashlib.sha256((text.split('## C-33')[0]+text.split('## C-31',1)[1]).encode()).hexdigest() if name=='README_EXCEPT_C33' else v.c.core.digest(v.ROOT/name)) for name in protected}
assert current==protected, 'Voisin C31/C32 ou section README hors C33 modifié'
with (OUT/'voisins-preservation-corrections-V2.json').open('x',encoding='utf-8') as f:json.dump({'unchanged':True,'entries':len(protected),'preimage_sha256':v.c.core.digest(OUT/'voisins-preimage-corrections-V2.json')},f,indent=2)
history=[p for p in OUT.rglob('*') if p.is_file() and p.relative_to(OUT).as_posix() not in evidence and p.name not in [v.RECEIPT,'PRET']]
m=v.c.seal(v.owner,[OUT/n for n in evidence],[])
m['historical_files']={p.relative_to(OUT).as_posix():v.c.core.digest(p) for p in history}
v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-33 corrections P1/P2/M2 prêtes à relire ; '+v.RECEIPT+' ; 89 contrôles navigateur, 20 réponses, six mutations natives et cinq mutations de preuve ; Q1 inchangée.\n')
v.verify(True)
