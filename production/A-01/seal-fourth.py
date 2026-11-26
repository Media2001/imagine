"""Seal the fourth-pass final receipts, no archive/site/Docker access."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-01'
ACCEPT='production/A-01/archive-reelle-4/4d311daa09cc/result.json'
UNITS='production/A-01/archive-reelle/5754d4a5d8b8/result.json'
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    command=[sys.executable,'-B',str(ROOT/'wp/tests/a01-court/verify_fourth.py'),ACCEPT,UNITS]
    checked=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    assert checked.returncode==0,checked.stdout+checked.stderr
    summary=json.loads(checked.stdout)
    out=LOT/'archive-reelle-4'
    for source,dest in [('voie1-preparer-image-26nov.log','preparer-image.log'),('voie1-rejouer-26nov-A01.log','rejouer.log'),('a01-4-ntfs.log','ntfs.log')]:
        target=out/dest
        if target.exists(): assert target.read_bytes()==(SCRATCH/source).read_bytes()
        else: shutil.copyfile(SCRATCH/source,target)
    prep=(out/'preparer-image.log').read_text(encoding='utf-8-sig',errors='replace')
    replay=(out/'rejouer.log').read_text(encoding='utf-8-sig',errors='replace')
    assert 'PREPARATION T01 : image verifiee sha256:' in prep
    native=json.loads(re.search(r'T01_RESULT (\{[^\n]+\})',replay)[1])
    assert native['pass'] and not any(native[k] for k in ('failures','errors','skipped'))
    packet=json.loads((ROOT/ACCEPT).read_text()); unit=json.loads((ROOT/UNITS).read_text())
    sources={**packet['source_manifest'],**unit['source_manifest']}
    for relative in ['wp/tests/a01-court/exercise_fourth.py','wp/tests/a01-court/verify_fourth.py','production/A-01/seal-fourth.py',
                     'wp/outils/staging-court/README.md','production/A-01/archive-reelle-4-notes.md']:
        sources[relative]=sha(ROOT/relative)
    evidence=[ROOT/ACCEPT,ROOT/UNITS,ROOT/UNITS.replace('result.json','tests.log')]+list(out.glob('*.log'))
    final={'schema':'imagine-a01-fourth-v1','status':'PASS','scope':'synthetic-only; no real import or publication authorization',
           'acceptance':ACCEPT,'units':UNITS,'verification':summary,'global_suite':native,
           'report':'files/rapports/2026-11-26-02h27.md','sources':sources,
           'evidence':{p.relative_to(ROOT).as_posix():sha(p) for p in evidence}}
    (LOT/'archive-reelle-4-final.json').write_text(json.dumps(final,indent=2),encoding='utf-8')
    historical=LOT/'PRET-archive-reelle-3-historique.txt'
    if not historical.exists(): shutil.copyfile(LOT/'PRET',historical)
    (LOT/'PRET').write_text('A-01 quatrième passe — PRET DE CODE POUR RELECTURE — 26 novembre 2026.\n'
        'Reçu : production/A-01/archive-reelle-4-final.json\n'
        'SHA-256 : '+sha(LOT/'archive-reelle-4-final.json')+'\n'
        'Notes : production/A-01/archive-reelle-4-notes.md\n'
        'Rapport : files/rapports/2026-11-26-02h27.md\n'
        '109 tests Linux : 108 réussis, 1 branche NTFS complétée sur hôte. 9 contrôles runtime.\n'
        'Global : '+str(native['tests'])+' tests, '+str(native['assertions'])+' assertions, aucun échec/erreur/ignoré.\n'
        'Base fictive 522327313 octets, ligne 18 Mio, trois phases et CLI base-seule éprouvés ; runners supprimés.\n'
        'Limites : pas de serveur MySQL8 natif ; objets SQL exécutables refusés ; phases natives différées sans fichiers ; pas de nouvelle publication/qualification commerciale 6.9.1.\n'
        'Aucune archive Imagine, aucun site réel ni compte réel, aucun GO implicite.\n',encoding='utf-8')
    assert all(sha(ROOT/r)==h for r,h in sources.items())
    assert subprocess.run(command,cwd=ROOT,capture_output=True).returncode==0
    print(json.dumps({'status':'PASS','manifest':'production/A-01/archive-reelle-4-final.json','pret':'production/A-01/PRET',**summary},indent=2))

if __name__=='__main__': main()
