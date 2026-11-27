"""Read-only T03 final-state checks; no Docker, writes or PRET mutation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LOTS = ['A-20', 'A-21', 'A-22', 'A-23', 'A-24', 'A-25', 'A-26', 'A-27', 'A-28', 'A-30', 'A-31', 'A-32']
PRET_BYTES = b'T-03 PRET - corrections et gates finales verifiees; aucun GO reel.\n'


def verify_replay(data, failures):
    lines = data.decode('utf-8-sig').splitlines()
    markers = [line[11:] for line in lines if line.startswith('T01_RESULT ')]
    if len(markers) != 1:
        raise ValueError('REPLAY_MARKER')
    marker = json.loads(markers[0])
    packets = marker['packets']
    tools = marker['tools']
    if (marker['pass'] is not True or marker['tests'] < 1 or marker['assertions'] < 1
            or any(marker[key] != 0 for key in ('failures', 'errors', 'skipped'))
            or tools['tools'] < 1 or tools['checks'] < 1 or tools['failures'] != 0 or tools['excluded']
            or packets['verified'] != len(LOTS) or packets['lots'] != LOTS
            or packets['failures'] != failures or packets['excluded']):
        raise ValueError('REPLAY_GATE')
    expected = f"REJEU : {marker['tests']} tests, {marker['assertions']} assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS"
    packet_line = f"PAQUETS : {len(LOTS)} vérifiés, {len(failures)} échecs ; hors rejeu : aucun"
    packet_line += ''.join('; ' + row['lot'] + ' ' + row['control'] for row in failures)
    tools_line = f"OUTILS : {tools['tools']} outils, {tools['checks']} contrôles, 0 échecs ; hors rejeu : aucun"
    if (not lines or lines[-1] != expected
            or [line for line in lines if line.startswith('PAQUETS : ')] != [packet_line]
            or [line for line in lines if line.startswith('OUTILS : ')] != [tools_line]
            or sum(bool(re.fullmatch(r'T01 CLEANUP : absence verifiee de imagine-t01-[a-f0-9]{32}', line)) for line in lines) != 1
            or any('NETTOYAGE EN ECHEC' in line for line in lines)):
        raise ValueError('REPLAY_SUMMARY_OR_CLEANUP')
    return {'marker': marker, 'last': expected, 'packets': packet_line, 'tools': tools_line}
