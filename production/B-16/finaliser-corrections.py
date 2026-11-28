import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('b16_corrections_reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
evidence=['A-VOIR.md','native-corrections-final2-V2.json','browser-corrections-final-V2.json','browser-corrections-final-V2.png','image-corrections-V2.json','image-corrections-V2.log','replay-corrections-V2.json','replay-corrections-V2.log','recovery-actions-final-V2.json']
history=['reception-V2.json','verifier-avant-corrections-V2.py','A-VOIR-avant-corrections-V2.md','PRET-avant-correction-V2.txt','red-V2.json','red-corrections-V2.json']
m=v.c.seal(v.owner,[OUT/n for n in evidence],[OUT/n for n in history]);v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('B-16 corrigé R1/R2/R3, prêt à relire ; '+v.RECEIPT+' ; visuel attendu.\n')
v.verify(True)
