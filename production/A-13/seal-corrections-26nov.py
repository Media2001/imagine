"""Seal the corrected A13 packet after actual verification and image preparation."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
from verifier_manifeste import inventory, verify
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-13'
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')

def main():
    history=SCRATCH/'a13-historical-corrections-26nov';history.mkdir(exist_ok=True)
    for name in ['manifeste.json','PRET','reception.json','verification.json','verification.tests.txt']:
        path=LOT/name
        if path.exists() and not (history/name).exists():shutil.copyfile(path,history/name)
    for name in ['reception-verification.json','reception-verification.tests.txt']:
        if (LOT/name).exists():
            assert not (history/name).exists()
            shutil.move(str(LOT/name),str(history/name))
    (LOT/'PRET').unlink(missing_ok=True)
    process=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/a13/verifier_livraison.py'),
        '--preuve',str(LOT/'verification.json')],capture_output=True,text=True,encoding='utf-8')
    assert process.returncode==0,process.stdout+process.stderr
    proof=json.loads((LOT/'verification.json').read_text(encoding='utf-8'))
    prep=SCRATCH/'voie1-preparer-image-26nov-new-tests.log'
    assert 'PREPARATION T01 : image verifiee' in prep.read_text(encoding='utf-8-sig',errors='replace')
    shutil.copyfile(prep,LOT/'preparer-image-corrections-26nov.log')
    (LOT/'reception.json').write_text(json.dumps({'status':'PRET','date':datetime.now().astimezone().isoformat(),
        'preparer_image_exit':0,'verification_exit':process.returncode,'tests':proof['suite']['tests'],
        'scope':'B1 IBAN cellule normalisee; I1 nom/adresse; I3 console; donnees fictives seulement',
        'real_go':False},indent=2),encoding='utf-8')
    files=inventory()
    manifest={'lot':'A-13','status':'PRET','horodatage':datetime.now().astimezone().isoformat(),
        'nombre_fichiers':len(files),'fichiers':[files[k] for k in sorted(files)],
        'excluded_dynamic':['production/A-13/PRET','production/A-13/manifeste.json'],
        'report':'files/rapports/2026-11-26-03h08.md','real_go':False}
    (LOT/'manifeste.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    verify(marker=False)
    sha=hashlib.sha256((LOT/'manifeste.json').read_bytes()).hexdigest()
    (LOT/'PRET').write_text('PRET\nA-13 corrections B1/I1/I3, 40 tests et trois CLI fictives, preparation image code 0.\n'
        'Controle : python production/A-13/verifier_manifeste.py\n'
        'Rejeu : python wp/tests/a13/verifier_livraison.py --preuve <scratch>/verification.json\n'
        'Manifeste SHA-256 : '+sha+'\nAucun reel ni GO de migration.\n',encoding='utf-8')
    print(json.dumps(verify(),indent=2))

if __name__=='__main__':main()
