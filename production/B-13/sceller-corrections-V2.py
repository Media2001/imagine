"""Scellement des corrections B13, historiques conservés."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'production/B-13'
spec = importlib.util.spec_from_file_location('b13_corrected_reader', OUT/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
assert not (OUT/'PRET').exists() and not (OUT/'reception-corrections-V2.json').exists()
files = [p for p in OUT.iterdir() if p.is_file() and p.name != 'PRET']
m = v.c.seal(v.owner, files, [OUT/'reception-initial-V2.json', OUT/'PRET-avant-corrections-V2', OUT/'verifier-initial-V2.py', OUT/'qualifier-initial-V2.py'])
v.verify(False, m, False)
with (OUT/'reception-corrections-V2.json').open('x', encoding='utf-8') as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
with (OUT/'PRET').open('x', encoding='utf-8') as f:
    f.write('B13 PRET technique — corrections B13-01/02/03/04 ; reception-corrections-V2.json et A-VOIR.md.\n34 contrôles natifs, 123 navigateur / 6 surfaces, neuf articles individuellement illustrés.\nSéquence B08/B13 réelle, retrait direct et limites 1/3/10 prouvés ; profils/sessions restaurés.\nImage préparée, REJEU PASS, OUTILS sans échec. Ni validation visuelle ni GO réel.\n')
v.verify(False)
v.verify(True)
