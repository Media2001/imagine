import sys
sys.dont_write_bytecode=True
import importlib.util,json,difflib
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('reader',OUT/'verifier.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
parts=[]
for name,rel in [('CodesSuivis.php','wp/plugins/imagine-site/CodesSuivis.php'),('CodesSuivisAdmin.php','wp/plugins/imagine-site/CodesSuivisAdmin.php'),('CodesSuivisConfidentialite.php','wp/plugins/imagine-site/CodesSuivisConfidentialite.php'),('c30-runtime.php','wp/tests/demo/c30-runtime.php')]:
    parts.extend(difflib.unified_diff((OUT/'avant-corrections-V2'/name).read_text(encoding='utf-8').splitlines(True),(v.ROOT/rel).read_text(encoding='utf-8').splitlines(True),fromfile='avant/'+rel,tofile='apres/'+rel))
with (OUT/'correction-diff-V2.patch').open('x',encoding='utf-8') as f:f.write(''.join(parts))
evidence=['A-VOIR.md','correction-native-final-V2.json','correction-unit-final-V2.json','correction-browser-final-V2.json','correction-browser-final-V2-sessions.json','correction-browser-final-V2.png','correction-recovery-essai2-V2.json','correction-image-V2.json','correction-image-V2.log','correction-replay-V2.json','correction-replay-V2.log','correction-diff-V2.patch']
history=[OUT/'reception-V2.json',OUT/'red-V2.json',OUT/'seed-V2.json',OUT/'correction-red-invite-V2.json',OUT/'correction-red-store-api-V2.json',OUT/'correction-native-essai-V2.json',OUT/'correction-native-essai2-V2.json']
m=v.c.seal(v.owner,[OUT/n for n in evidence],history)
m['historical_files'].update({p.relative_to(OUT).as_posix():v.c.core.digest(p) for p in (OUT/'avant-corrections-V2').glob('*') if p.is_file()})
v.verify(False,m,False)
with (OUT/v.RECEIPT).open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
with (OUT/'PRET').open('x',encoding='utf-8') as f:f.write('C-30 corrections prêtes à relire ; '+v.RECEIPT+' ; instructions 1–6 appliquées, optimisation 7 différée comme non urgente ; aucun paiement réel.\n')
v.verify(True)
