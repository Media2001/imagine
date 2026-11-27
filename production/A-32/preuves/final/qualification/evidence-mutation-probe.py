"""Falsify copies of the genuine A32 receipt; no synthetic PASS evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path('C:/Users/Ced/imagine')
BASE = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a32-active-20261127')
SOURCE = BASE / 'matrix-final-v2'
OUT = BASE / 'evidence-mutations'
assert not OUT.exists()
OUT.mkdir()
spec = importlib.util.spec_from_file_location('a32_mutation_delivery', ROOT / 'wp/tests/a32/delivery.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
rows = [{'check': 'genuine_full_packet_accepted', 'status': 'PASS' if m.local_valid(SOURCE) else 'FAIL'}]

def apply_json(folder, relative, fn):
    path = folder / relative
    data = json.loads(path.read_text(encoding='utf-8'))
    fn(data)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def mutant(name, edit):
    folder = OUT / name
    shutil.copytree(SOURCE, folder)
    edit(folder)
    try:
        accepted = m.local_valid(folder)
    except Exception:
        accepted = False
    rows.append({'check': name, 'status': 'FAIL' if accepted else 'PASS', 'tampered_packet_accepted': accepted})

mutant('python_only_not_native', lambda p: apply_json(p, 'windows-matrix.json', lambda d: d.update(scope='python_only')))
mutant('missing_zero_tool_case', lambda p: apply_json(p, 'utf8/native/result.json', lambda d: d.update(checks=[c for c in d['checks'] if c['check'] != 'classic:tour_guard_zero_tools:absent'])))
mutant('nonzero_subprocess_trace', lambda p: apply_json(p, 'utf8/native/classic-unverified-absent-proof.json', lambda d: d.update(commands=[['CANARY']], tools_launched=1)))
mutant('production_database_changed', lambda p: apply_json(p, 'utf8/native/classic-unverified-production-proof.json', lambda d: d['database_after'].update(MUTATION='changed')))
mutant('missing_a27_from_complete_tour', lambda p: apply_json(p, 'utf8/native/hpos-complete/bilan.json', lambda d: d.update(outils=d['outils'][:-1])))

def fake_ok(folder):
    matrix = folder / 'windows-matrix.json'
    data = json.loads(matrix.read_text(encoding='utf-8'))
    row = data['rows'][0]
    log = folder / row['log']
    log.write_text(log.read_text(encoding='utf-8').replace('\nOK\n', '\nNOT_OK\n'), encoding='utf-8')
    row['sha256'] = hashlib.sha256(log.read_bytes()).hexdigest()
    matrix.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
mutant('exit_zero_without_unittest_ok_rehashed', fake_ok)
mutant('native_source_hash_changed', lambda p: apply_json(p, 'utf8/native/sources.json', lambda d: d.update({'wp/outils/bascule/tournee/tournee.py': '0' * 64})))
mutant('duplicate_native_exit', lambda p: (p / 'utf8/native/result.json').write_text('{"exit_code":0,"exit_code":1}', encoding='utf-8'))
result = {'exit_code': int(any(c['status'] != 'PASS' for c in rows)), 'readiness_claimed': False,
          'source': str(SOURCE), 'sources': m.sources(), 'checks': rows}
(OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'exit_code': result['exit_code'], 'checks': rows}, indent=2))
sys.exit(result['exit_code'])
