"""Réception corrigée B14, limites B01 et complément B11 explicites."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'production/B-14'
spec = importlib.util.spec_from_file_location('b14_corrected_reader', OUT/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
assert not (OUT/'PRET').exists() and not (OUT/'reception-corrections-V2.json').exists()
files = [p for p in OUT.iterdir() if p.is_file() and p.name != 'PRET']
m = v.c.seal(v.owner, files, [OUT/'reception-initial-V2.json', OUT/'PRET-avant-corrections-V2', OUT/'verifier-initial-V2.py'])
v.verify(False, m, False)
with (OUT/'reception-corrections-V2.json').open('x', encoding='utf-8') as f:
    json.dump(m, f, ensure_ascii=False, indent=2)
with (OUT/'PRET').open('x', encoding='utf-8') as f:
    f.write('B14 PRET technique — reception-corrections-V2.json, A-VOIR.md.\n22 contrôles natifs, 52 navigateur ; ancre paywall réelle, helper partagé, garde-fou de structure découvert dans les 2 tests PHPUnit B14.\nREJEU 1209/36693 PASS ; OUTILS 23/852/0 ; 13 paquets/0.\nDeux anciennes recettes B01 restent rouges sur contrats historiques : limites détaillées ; complément B11 natif23 + diff strict du gabarit sous B14, aucun reçu voisin réécrit.\nNi clôture, validation visuelle ni GO réel.\n')
v.verify(False)
v.verify(True)
