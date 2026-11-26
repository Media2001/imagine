"""Promote only the observed green A11 packet; keep all earlier bytes external."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-11'
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')
PACKET='8b3b9bdcf308'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=SCRATCH/'a11'/PACKET
    target=LOT/'preuves'/PACKET
    if source.exists():
        checked=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/a11/verifier.py'),str(source)],capture_output=True,text=True,encoding='utf-8')
        assert checked.returncode==0,checked.stdout+checked.stderr
        history=SCRATCH/'a11-historical-26nov'; history.mkdir(exist_ok=True)
        for p in (LOT/'preuves').iterdir():
            if p.name!=PACKET:
                assert not (history/p.name).exists()
                shutil.move(str(p),str(history/p.name))
        shutil.move(str(source),str(target))
    result=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/a11/verifier.py'),str(target)],capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
    proof=json.loads(result.stdout)
    prep=SCRATCH/'a11-preparer-image-26nov.log'
    assert 'PREPARATION T01 : image verifiee' in prep.read_text(encoding='utf-8-sig',errors='replace')
    shutil.copyfile(prep,LOT/'preparer-image-corrections-26nov.log')
    for name in ['manifest.json','PRET','reception.json']:
        p=LOT/name; history=SCRATCH/'a11-historical-26nov'; history.mkdir(exist_ok=True)
        if p.exists() and not (history/name).exists(): shutil.copyfile(p,history/name)
    (LOT/'reception.json').write_text(json.dumps({'status':'PRET','corrections':'C1,C2,3,4; refus nommes','verification':proof},indent=2),encoding='utf-8')
    dynamic={p.relative_to(ROOT).as_posix() for p in [LOT/'manifest.json',LOT/'PRET',LOT/'verification-corrections-26nov.json']}
    files={p.relative_to(ROOT).as_posix():sha(p) for root in [ROOT/'wp/tests/a11',ROOT/'wp/outils/bascule/a11',LOT]
           for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.relative_to(ROOT).as_posix() not in dynamic}
    manifest={'schema':'imagine-a11-delivery-v2','status':'PRET','packet':target.relative_to(ROOT).as_posix(),
              'file_count':len(files),'files':files,'excluded_dynamic':sorted(dynamic),'verification':proof,
              'report':'files/rapports/2026-11-26-02h36.md','shared_readme_policy':'contract only; no sibling/orchestration hash pins',
              'real_go':False}
    (LOT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (LOT/'PRET').write_text('PRET'+PACKET+'\nA-11 corrections 26 novembre, C1/C2 et refus nommes prouves.\n'
        +'Manifeste SHA-256 : '+sha(LOT/'manifest.json')+'\nControle : python wp/tests/a11/verifier.py '+target.relative_to(ROOT).as_posix()+'\nAucun GO reel.\n',encoding='utf-8')
    (LOT/'verification-corrections-26nov.json').write_text(result.stdout,encoding='utf-8')
    assert all(sha(ROOT/r)==h for r,h in files.items())
    assert len(list((LOT/'preuves').iterdir()))==1
    print(result.stdout)

if __name__=='__main__':main()
