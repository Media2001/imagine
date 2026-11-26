"""C16 V2 bounded qualification, with captured real commands and exact cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import importlib.util
import json
import os
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/C-16'

def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--deploy',action='store_true')
    parser.add_argument('--canonical',action='store_true')
    args=parser.parse_args()
    execution={'started_at':datetime.now(timezone.utc).isoformat(),'steps':[],'scope':'imagine-test-demo'}
    def step(name,command):
        started=datetime.now(timezone.utc).isoformat()
        process=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (PROOF/(name+'.log')).write_text(process.stdout+process.stderr,encoding='utf-8')
        execution['steps'].append({'name':name,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit':process.returncode,'command':command})
        (PROOF/'execution-V2.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2),encoding='utf-8')
        print(name+': '+str(process.returncode),flush=True)
        if process.returncode: raise RuntimeError('C16 qualification failed: '+name+'; see its log')
    if args.prepare:step('preparer-image-V2',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/preparer-image.ps1'])
    if args.deploy:step('deployment-V2',[sys.executable,'wp/outils/demo/c16.py','--deploy'])
    step('unit-focused-V2',[sys.executable,'wp/outils/demo/c16-unit.py','unit-focused-V2','CommandeReglesTest|SansEmailTest'])
    step('unit-root-V2',[sys.executable,'wp/outils/demo/c16-unit.py','unit-root-V2','--root'])
    step('http-base-V2',[sys.executable,'wp/tests/demo/c16-baseline-V2.py'])
    step('http-corrections-V2',[sys.executable,'wp/tests/demo/c16-corrections-http.py'])
    if args.canonical:step('rejouer-t01-V2',['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/rejouer.ps1'])
    # Qualification requires preparation/canonical evidence; partial runs are not PRET.
    if args.prepare and args.canonical:
        process=subprocess.run([sys.executable,'wp/tests/demo/c16-gates-V2.py','--strict-global'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (PROOF/'gates-V2.log').write_text(process.stdout+process.stderr,encoding='utf-8')
        print(process.stdout,end='')
        if process.returncode: raise RuntimeError('Fresh C16 gates failed; see gates-V2.log')
    return 0
if __name__=='__main__':sys.exit(run())
