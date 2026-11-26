"""Seal the corrected A13 packet after actual verification and image preparation."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil

import sys
sys.dont_write_bytecode=True
from verifier_manifeste import inventory, verify
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-13'
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')

def main():
    history=SCRATCH/'a13-prioritaire-20261126'/'avant-scellement';history.mkdir(parents=True,exist_ok=True)
    for name in ['manifeste.json','PRET','reception.json','verification.json','verification.tests.txt']:
        path=LOT/name
        if path.exists() and not (history/name).exists():shutil.copyfile(path,history/name)
    for name in ['reception-verification.json','reception-verification.tests.txt']:
        if (LOT/name).exists():
            assert not (history/name).exists()
            shutil.move(str(LOT/name),str(history/name))
    (LOT/'PRET').unlink(missing_ok=True)
    # Ne pas remplacer la matrice verte par un seul rejeu à la locale courante.
    current=SCRATCH/'a13-prioritaire-20261126'
    proof=json.loads((current/'verification.json').read_text(encoding='utf-8'))
    matrix=proof['matrice_encodages']
    assert len(matrix)==proof['nombre_contextes']==5
    assert sum(x['preuve']['suite']['tests'] for x in matrix)==proof['execution_totale_tests']
    for run in matrix:
        assert run['exit_code']==0
        assert run['preuve']['sources_sha256']==proof['sources_sha256']
        suite=run['preuve']['suite']
        assert suite['tests']==46 and suite['echecs']==suite['erreurs']==suite['ignores']==0
        assert [x['code'] for x in run['preuve']['cli']]==[0,1,2]
        env=run['environnement']
        assert env['locale']=='cp1252' and env['utf8_mode']==int(env['PYTHONUTF8'])
        assert env['stdout']==env['stderr']==env['PYTHONIOENCODING']
    assert any(x['environnement']['python']=='3.14.7' and x['environnement']['preferred']=='cp1252'
        and x['environnement']['utf8_mode']==0 for x in matrix)
    for relative,sha in proof['sources_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==sha,relative
    for name in ['verification.json','verification.tests.txt']:
        shutil.copyfile(current/name,LOT/name)
    prep=current/'preparer-image.log'
    assert 'PREPARATION T01 : image verifiee' in prep.read_text(encoding='utf-8-sig',errors='replace')
    shutil.copyfile(prep,LOT/'preparer-image-corrections-26nov.log')
    (LOT/'reception.json').write_text(json.dumps({'status':'PRET','date':datetime.now().astimezone().isoformat(),
        'preparer_image_exit':0,'verification_exit':0,'tests':proof['suite']['tests'],
        'contextes':len(matrix),'executions_tests':proof['execution_totale_tests'],
        'scope':'Consigne 0 : encodage test, filtre types, dedoublonnage postal, Python et encodages exacts',
        'real_go':False},indent=2),encoding='utf-8')
    files=inventory()
    manifest={'lot':'A-13','status':'PRET','horodatage':datetime.now().astimezone().isoformat(),
        'nombre_fichiers':len(files),'fichiers':[files[k] for k in sorted(files)],
        'excluded_dynamic':['production/A-13/PRET','production/A-13/manifeste.json'],
        'report':'files/rapports/2026-11-26-05h05-A13.md','real_go':False}
    (LOT/'manifeste.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    verify(marker=False)
    sha=hashlib.sha256((LOT/'manifeste.json').read_bytes()).hexdigest()
    (LOT/'PRET').write_text('PRET\nA-13 consigne 0 : 46 tests verts dans cinq contextes Windows, preparation image code 0.\n'
        'Controle : python production/A-13/verifier_manifeste.py\n'
        'Rejeu : python wp/tests/a13/verifier_livraison.py --preuve <scratch>/verification.json\n'
        'Manifeste SHA-256 : '+sha+'\nAucun reel ni GO de migration.\n',encoding='utf-8')
    print(json.dumps(verify(),indent=2))

if __name__=='__main__':main()
