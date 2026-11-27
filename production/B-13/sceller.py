"""Scellement proportionné des lots V2 de structure, aucun site muté."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
lot = sys.argv[1] if len(sys.argv) > 1 else 'B-13'
assert lot in ['B-13','B-14','B-15']
spec = importlib.util.spec_from_file_location('seal_reader', ROOT/'production'/lot/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
owner, out = v.owner, v.OUT
assert (out/'A-VOIR.md').is_file() and (out/'browser-final-V2.png').is_file()
assert not (out/'PRET').exists() and not (out/'reception-V2.json').exists()
files = [p for p in out.iterdir() if p.is_file() and p.name not in ['PRET','reception-V2.json']]
m = v.c.seal(owner, files, [out/'red-V2.json'])
v.verify(False, m, False)
with (out/'reception-V2.json').open('x', encoding='utf-8') as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
with (out/'PRET').open('x', encoding='utf-8') as f:
    f.write(lot+' PRET technique — reception-V2.json et A-VOIR.md.\nCode et tests réels, image préparée, REJEU PASS et OUTILS sans échec.\nValidation visuelle attendue ; aucun GO réel, aucun paiement, envoi ni déploiement.\n')
v.verify(False)
v.verify(True)
