import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('b15_correction_reader',OUT/'verifier.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
names=['A-VOIR.md','browser-corrections-final-V2.png']
for prefix in ['pure','native','browser','image','replay']:
    names.append(prefix+'-corrections-final-V2.json')
    if prefix in ['image','replay']:names.append(prefix+'-corrections-final-V2.log')
history=['red-V2.json','red-contexte-V2.json','reception-V2.json','A-VOIR-avant-corrections-V2.md','verifier-avant-corrections-V2.py','PRET-avant-correction-V2.txt']
m=v.c.seal(v.owner,[OUT/n for n in names],[OUT/n for n in history])
v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('B-15 corrections prêtes à relire ; '+v.RECEIPT+' ; preuve cache résistante au mutant, code fonctionnel inchangé.\n')
v.verify(True)
