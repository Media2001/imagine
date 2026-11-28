import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
evidence=['A-VOIR.md','native-final-V2.json','browser-final-V2.json','browser-final-V2.png','standard-V2.json','image-V2.json','image-V2.log','replay-V2.json','replay-V2.log']
evidence += [r['response'] for r in v.load('browser-final-V2.json')['rows']]
history=[p for p in OUT.glob('*.json') if p.name not in evidence]
m=v.c.seal(v.owner,[OUT/n for n in evidence],history);v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-33 prêt à relire ; '+v.RECEIPT+' ; fermetures anonymes, six mutations réelles, administrateur/éditeur natifs préservés.\n')
v.verify(True)
