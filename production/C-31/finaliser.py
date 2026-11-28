import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('c31_reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
evidence=['A-VOIR.md','native-final-V2.json','browser-final-V2.json','browser-final-V2.png','standard-V2.json','seed-V2.json','image-V2.json','image-V2.log','replay-V2.json','replay-V2.log']
m=v.c.seal(v.owner,[OUT/n for n in evidence],[OUT/'red-V2.json']);v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-31 prêt technique à relire ; '+v.RECEIPT+' ; liste fictive, transports natifs wp-login bloqués et documentés.\n')
v.verify(True)
