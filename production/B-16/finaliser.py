import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reader',OUT/'verifier.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
evidence=[OUT/n for n in ['native-final5-V2.json','browser-final5-V2.json','browser-final5-V2.png','b11-complement-V2.json','image2-V2.json','image2-V2.log','replay2-V2.json','replay2-V2.log','A-VOIR.md']]
history=[OUT/'red-V2.json']
m=v.c.seal(v.owner,evidence,history)
v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('B-16 prêt technique à relire ; '+v.RECEIPT+' ; validation visuelle attendue.\n')
v.verify(True)
