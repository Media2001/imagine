"""Promote a real green A12 native/style packet, sealing A12 only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-12'
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')
SOURCE=SCRATCH/'a12-corrections-26nov-0233'
TARGET=LOT/'preuves/final'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(path):
    p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/a12/verify.py'),str(path)],capture_output=True,text=True,encoding='utf-8')
    assert p.returncode==0,p.stdout+p.stderr
    return json.loads(p.stdout)

def main():
    history=SCRATCH/'a12-historical-26nov';history.mkdir(exist_ok=True)
    if SOURCE.exists():
        verify(SOURCE)
        if TARGET.exists():
            assert not (history/'final').exists()
            shutil.move(str(TARGET),str(history/'final'))
        shutil.move(str(SOURCE),str(TARGET))
    proof=verify(TARGET)
    for name in ['manifeste-final.json','PRET','reception.json','verdict.json']:
        p=LOT/name
        if p.exists() and not (history/name).exists(): shutil.copyfile(p,history/name)
    prep=SCRATCH/'a11-preparer-image-26nov.log'
    assert 'PREPARATION T01 : image verifiee' in prep.read_text(encoding='utf-8-sig',errors='replace')
    shutil.copyfile(prep,LOT/'preparer-image-corrections-26nov.log')
    (LOT/'verdict.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    (LOT/'reception.json').write_text(json.dumps({'status':'PRET','scope':'propagation stricte A11; native+style green','verification':proof},indent=2),encoding='utf-8')
    dynamic={'production/A-12/manifeste-final.json','production/A-12/PRET','production/A-12/verification-corrections-26nov.json'}
    files={p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}
        for root in [ROOT/'wp/tests/a12',ROOT/'wp/outils/bascule/a12',LOT] for p in root.rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and p.relative_to(ROOT).as_posix() not in dynamic}
    manifest={'schema':'imagine-a12-final-manifest-v2','status':'PRET','verdict':'PRET','readiness':True,
              'file_count':len(files),'files':files,'excluded_dynamic':sorted(dynamic),'verification':proof,
              'report':'files/rapports/2026-11-26-02h38.md','real_go':False}
    (LOT/'manifeste-final.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (LOT/'PRET').write_text('PRET\nA-12, propagation des refus nommes A-11, 26 novembre 2026.\n'
        'Paquet unique : production/A-12/preuves/final\n'
        'Controle : python wp/tests/a12/verify.py production/A-12/preuves/final\n'
        'Manifeste SHA-256 : '+sha(LOT/'manifeste-final.json')+'\nAucun GO reel.\n',encoding='utf-8')
    (LOT/'verification-corrections-26nov.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    assert all(sha(ROOT/r)==h['sha256'] for r,h in files.items())
    assert [p.name for p in (LOT/'preuves').iterdir() if p.is_dir()]==['final']
    print(json.dumps({'exit_code':0,'counts':proof['counts'],'verification_checks':len(proof['checks']),'packet':'production/A-12/preuves/final'},indent=2))

if __name__=='__main__':main()
