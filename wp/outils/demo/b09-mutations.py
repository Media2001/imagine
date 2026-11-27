"""Mutations des sources Contact en conteneurs jetables hors réseau."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import b09
label=sys.argv[1]
rows=[]
for name in ['slash','consentement','mail','http','prive','rest','export','effacement','lecture','nonce']:
    receipt=label+'-'+name
    p=subprocess.run([sys.executable,'-B',str(b09.ROOT/'wp/outils/demo/b09-local.py'),receipt,name],capture_output=True,encoding='utf-8')
    log=b09.PROOF/(receipt+'.log')
    text=log.read_text(encoding='utf-8')
    m=re.search(r'B09 JUNIT BEGIN\s*(.*?)B09 JUNIT END',text,re.S)
    a=ET.fromstring(m.group(1)).find('testsuite').attrib if m else {}
    detected=p.returncode==1 and int(a.get('failures',0))>0 and int(a.get('errors',99))==0
    rows.append({'mutation':name,'exit':p.returncode,'detected':detected,'junit':a,'log':log.name,'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
    print(name,'détectée' if detected else 'ECHEC')
b09.save(label,{'mutations':rows,'count':len(rows),'detected':sum(r['detected'] for r in rows)})
assert len(rows)==10 and all(r['detected'] for r in rows)
