"""Read-only sealed delivery verification; default is this lot's current final packet."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
LOT = Path(__file__).resolve().parent.name
N = LOT.split('-')[1]
OWN = [f'wp/outils/bascule/a{N}', f'wp/tests/a{N}', f'production/{LOT}']

def inventory(roots, excluded=()):
    files=[]
    for key in roots:
        p=ROOT/key
        if not p.exists(): raise RuntimeError('MISSING_ROOT')
        files.extend([p] if p.is_file() else [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if p.relative_to(ROOT).as_posix() not in excluded}

def main():
    if len(sys.argv)!=1: raise RuntimeError('NO_ARGUMENTS')
    base=ROOT/'production'/LOT
    manifest=json.loads((base/'manifest.json').read_bytes())
    excluded={f'production/{LOT}/manifest.json',f'production/{LOT}/PRET'}
    assert manifest['lot']==LOT and manifest['packet']==f'production/{LOT}/preuves/final'
    assert manifest['files']==inventory(OWN,excluded),'PACKAGE_DRIFT'
    gates=json.loads((base/'parent-gates.json').read_bytes())
    evidence=ROOT/gates['directory']
    assert evidence.resolve().is_relative_to((ROOT/'files/rapports').resolve())
    for name,digest in gates['files'].items():
        p=evidence/name
        assert p.resolve().is_relative_to(evidence.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==digest
    commands=json.loads((evidence/'commands.json').read_bytes())
    assert len(commands)==19 and all(r['exit_code']==0 and r['sources_stable'] is True for r in commands)
    required={'a26-matrix','a27-matrix','a26-candidate-verify','a27-candidate-verify','prepare-image','global-utf8','global-cp1252'}
    required|={f'a{n}-readonly-{c}' for n in (20,21,22,23,24,25) for c in ('utf8','cp1252')}
    assert {r['name'] for r in commands}==required
    for row in commands:
        assert hashlib.sha256((evidence/row['log']).read_bytes()).hexdigest()==row['log_sha256']
    freeze=json.loads((evidence/'freeze.json').read_bytes())
    assert freeze['sources']==inventory(freeze['roots']),'FROZEN_SOURCE_DRIFT'
    assert json.loads((evidence/'result.json').read_bytes())['exit_code']==0
    p=subprocess.run([sys.executable,'-B',str(ROOT/f'wp/tests/a{N}/verify.py')],cwd=ROOT,
        env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,timeout=90)
    assert p.returncode==0 and p.stderr==b'', 'NATIVE_PACKET_INVALID'
    print(json.dumps({'lot':LOT,'exit_code':0,'package_and_inventory':'PASS','frozen_sources':'PASS',
                      'parent_gates':len(commands),'native_packet':'PASS','pret_present':(base/'PRET').is_file()}))
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as error:
        print(json.dumps({'lot':LOT,'exit_code':1,'code':'SEALED_VERIFICATION_FAILED','class':type(error).__name__}))
        sys.exit(1)
