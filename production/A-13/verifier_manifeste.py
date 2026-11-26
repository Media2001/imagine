"""A13 manifest checks only A13 files, never live sibling/orchestration files."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-13'
DYNAMIC={'production/A-13/PRET','production/A-13/manifeste.json'}

def inventory():
    fixed=[ROOT/'wp/outils/bascule/controler-export',ROOT/'wp/outils/bascule/controler-export.md']
    fixed+=list((ROOT/'wp/tests/fixtures').glob('a13-*-fictif.csv'))
    files=fixed+[p for d in ['production/A-13','wp/tests/a13','wp/outils/bascule/a13'] for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return {p.relative_to(ROOT).as_posix():{'chemin':p.relative_to(ROOT).as_posix(),'octets':p.stat().st_size,
        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.relative_to(ROOT).as_posix() not in DYNAMIC}

def verify(marker=True):
    data=json.loads((LOT/'manifeste.json').read_text(encoding='utf-8'))
    items=data['fichiers']; found={x['chemin']:x for x in items}; actual=inventory()
    assert len(items)==len(found)==data['nombre_fichiers']
    assert found==actual, 'A13_MANIFEST_MEMBERSHIP_OR_HASH'
    proof=json.loads((LOT/'verification.json').read_text(encoding='utf-8'))
    assert proof['sources_sha256']=={k:v['sha256'] for k,v in actual.items() if not k.startswith('production/')}
    assert proof['suite']['tests']>=40 and proof['suite']['echecs']==proof['suite']['erreurs']==proof['suite']['ignores']==0
    assert [x['code'] for x in proof['cli']]==[0,1,2]
    receipt=json.loads((LOT/'reception.json').read_text(encoding='utf-8'))
    assert receipt['preparer_image_exit']==0 and receipt['status']=='PRET'
    if marker:
        sha=hashlib.sha256((LOT/'manifeste.json').read_bytes()).hexdigest()
        assert sha in (LOT/'PRET').read_text(encoding='utf-8')
    return {'lot':'A-13','exit_code':0,'manifest_files':len(found),'tests':proof['suite']['tests'],'real_go':False}

if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
