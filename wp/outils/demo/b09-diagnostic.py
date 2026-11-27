"""Diagnostic borné de la première reprise B09 (aucun contenu/secret imprimé)."""
import sys
sys.dont_write_bytecode=True
import json
import os
from pathlib import Path
import b09
r=json.loads((b09.PROOF/'reprise-finale.json').read_text(encoding='utf-8'))
saved=json.loads((Path(os.environ['TMPDIR'])/r['private_snapshot']['file']).read_text(encoding='utf-8'))['payload']
a=saved['database'];b=b09.b08.snapshot()
for key in a:
    if a[key]==b.get(key): continue
    if key=='posts':
        x={r['ID']:r for r in a[key]};y={r['ID']:r for r in b[key]}
        print(key,[{'id':k,'type':x[k]['post_type'],'fields':[f for f in x[k] if x[k][f]!=y.get(k,{}).get(f)]} for k in x if x[k]!=y.get(k)])
    elif key not in ['options','actionscheduler_actions','actionscheduler_logs','actionscheduler_claims','actionscheduler_groups']:
        print('Other table changed:',key)
print('Business fingerprint changed keys:')
def diff(a,b,p=''):
    if a==b:return
    if isinstance(a,dict) and isinstance(b,dict):
        for k in set(a)|set(b):diff(a.get(k),b.get(k),p+'/'+k)
    else:print(p)
diff(saved['business'],b09.b08.c25.b06.state())
