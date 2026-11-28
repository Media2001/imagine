import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('c31_reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
evidence = ['A-VOIR.md','README-fragment-V2.md','FINALISATION-V2.md','verifier-corrections.py','offline.py','style.py','finaliser.py',
    'corrections-native-final-V2.json','corrections-browser-final-V2.json','corrections-browser-final-V2.png',
    'corrections-compte-final-V2.json','corrections-compte-final-V2-inchange.png','corrections-compte-final-V2-refuse.png','corrections-compte-final-V2-autorise.png',
    'corrections-commande-final-V2.json','corrections-commande-final-V2.png',
    'corrections-cible-final-V2.json','corrections-cible-final-V2.log','corrections-suite-final-V2.json','corrections-suite-final-V2.log','corrections-style-final-V2.json','corrections-style-final-V2.log',
    'corrections-image-V2.json','corrections-image-V2.log','corrections-replay-V2.json','corrections-replay-V2.log',
    'corrections-installation2-V2.json','corrections-cart-restaure-V2.json','corrections-standard-V2.json','standard-corrections.py']
v.local(True)
v.global_gates()
m = v.c.seal(v.owner, [OUT/n for n in evidence], [OUT/'red-V2.json',OUT/'corrections-red-V2.json',OUT/'corrections-native-red3-V2.json',OUT/'corrections-store-offline-red-V2.json',OUT/'corrections-store-red1-V2.json',OUT/'reception-V2.json'])
v.verify(False, m, False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-31 prêt technique à relire ; '+v.RECEIPT+' ; liste fictive, transports natifs wp-login bloqués et documentés.\n')
v.verify(True)
