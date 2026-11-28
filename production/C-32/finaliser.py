import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
b=v.load('browser-final-V2.json');rows=[r for r in b['rows'] if r['kind']=='lecture']
with (OUT/'strict-reading-V2.json').open('x',encoding='utf-8') as f:json.dump({'status':'FAIL','expected':0,'pages':len(rows),'observed_cookie_names_per_page':sorted({c['name'] for r in rows for c in r['browser']}),'native_order_attribution_unchanged':True,'browser_receipt':'browser-final-V2.json'},f,ensure_ascii=False,indent=2)
evidence=['A-VOIR.md','native-final-V2.json','browser-final-V2.json','browser-final-V2.png','standard-V2.json','strict-reading-V2.json','recovery-essai-V2.json','image-V2.json','image-V2.log','replay-V2.json','replay-V2.log']
historical=[p for p in OUT.glob('*.json') if p.name not in evidence]
m=v.c.seal(v.owner,[OUT/n for n in evidence],historical);v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-32 prêt à relire — inventaire et contrôleur fermés ; '+v.RECEIPT+' ; réserve explicite : zéro cookie en lecture FAIL (sept cookies natifs d’attribution, non désactivés conformément au brief).\n')
v.verify(True)
