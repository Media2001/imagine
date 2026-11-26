"""Packaging-only reseal: own lot paths, frozen receipts, no Docker."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode=True
LOT=Path(__file__).resolve().parent
ROOT=LOT.parents[1]
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    spec=importlib.util.spec_from_file_location('packaging_verifier',LOT/'verifier.py')
    v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
    path=LOT/'manifeste.json';manifest=json.loads(path.read_text(encoding='utf-8'))
    history=SCRATCH/'a09-packaging-26nov';history.mkdir(exist_ok=True)
    for name in ['manifeste.json','PRET']:
        if not (history/name).exists():shutil.copyfile(LOT/name,history/name)
    original=json.loads((history/'manifeste.json').read_text(encoding='utf-8'))
    categories=['sources','evidence'];removed={}
    for category in categories:
        removed[category]=sum(not v.owned(n) for n in manifest[category])
        retained={}
        for name,digest in manifest[category].items():
            if not v.owned(name):continue
            current=sha(ROOT/name)
            if name!=(LOT/'verifier.py').relative_to(ROOT).as_posix():assert current==digest,('unexpected own-file drift',name)
            retained[name]=current
        manifest[category]=retained
    business={n:h for n,h in original['sources'].items() if n.startswith('wp/') and v.owned(n)}
    assert business and all(sha(ROOT/n)==h for n,h in business.items())
    for p in [LOT/'verifier.py',Path(__file__)]:manifest['sources'][p.relative_to(ROOT).as_posix()]=sha(p)
    manifest.update(packaging_policy='own-lot paths only; shared audit README by contract; frozen dependency snapshots not current pins',
                    packaging_removed_counts=removed,runtime_and_tests_unchanged=True,packaging_verifier_no_docker=True,
                    report='files/rapports/2026-11-26-02h45.md')
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pre=subprocess.run([sys.executable,'-B',str(LOT/'verifier.py'),'--pre-pret'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    assert pre.returncode==0,pre.stdout+pre.stderr
    (LOT/'PRET').write_text('A-09 — PRET, correction des manifestes du 26 novembre.\n'
        'Code et preuves natives inchanges ; aucun rejeu Docker.\nManifeste SHA-256 : '+sha(path)+'\nPaquet : '+manifest['proof']+'\n'
        'Controle pur : python production/A-09/verifier.py\nAucun GO reel.\n',encoding='utf-8')
    final=subprocess.run([sys.executable,'-B',str(LOT/'verifier.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    assert final.returncode==0,final.stdout+final.stderr
    receipt={'exit_code':final.returncode,'runtime_and_tests_unchanged':True,'runtime_source_files':len(business),
             'removed_counts':removed,'no_docker':True,'verification':json.loads(final.stdout)}
    (LOT/'verification-manifestes-26nov.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    assert all(v.owned(n) for category in categories for n in manifest[category])
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
