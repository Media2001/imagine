"""PARENT ONLY: copy one verified full packet, then seal; never creates PRET."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'production/A-31'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', required=True, type=Path)
    ap.add_argument('--gates', required=True, type=Path)
    ap.add_argument('--parent-serialized', required=True, action='store_true')
    a = ap.parse_args()
    helper = load('a31_reseal_delivery', HERE / 'delivery.py')
    evidence, gates = a.evidence.resolve(), a.gates.resolve()
    for path in (evidence, gates):
        if path.is_relative_to(ROOT) or ROOT.is_relative_to(path) or not path.is_dir() or path.is_symlink():
            return {'exit_code': 1, 'code': 'A31_PACKET_INVALID'}
    matrix = helper.read(evidence / 'windows-matrix.json')
    if matrix.get('scope') != 'python_and_native':
        return {'exit_code': 1, 'code': 'A31_PARTIAL_EVIDENCE'}
    verifier = load('a31_reseal_verify', HERE / 'verify.py')
    candidate = verifier.verify(evidence, False)
    if candidate['exit_code'] != 0:
        return {'exit_code': 1, 'code': 'A31_NATIVE_PACKET_INVALID'}
    if not helper.gate_logs_valid(gates):
        return {'exit_code': 1, 'code': 'A31_PARENT_GATES_MISSING'}
    target = BASE / 'preuves/final'
    if target.exists() or target.is_symlink() or (BASE / 'manifest.json').exists():
        return {'exit_code': 1, 'code': 'A31_EXISTING_PACKET_REFUSED'}
    if any(p.is_symlink() for path in (evidence, gates) for p in path.rglob('*')):
        return {'exit_code': 1, 'code': 'A31_PACKET_INVALID'}
    declaration = helper.read(BASE / 'rejeu.json')
    prefix = 'production/A-31/preuves/final/'
    logs = [prefix + p.relative_to(evidence).as_posix() for p in evidence.rglob('*.log')]
    logs += [prefix + 'gates/' + p.relative_to(gates).as_posix() for p in gates.rglob('*.log')]
    if sorted(logs) != sorted(declaration['logs']):
        return {'exit_code': 1, 'code': 'A31_LOG_DECLARATION_MISMATCH'}
    # All prerequisites are resolved before the first repository write.
    shutil.copytree(evidence, target)
    shutil.copytree(gates, target / 'gates')
    final = verifier.verify(target, False)
    if final['exit_code'] != 0 or not helper.gate_logs_valid(target / 'gates'):
        return {'exit_code': 1, 'code': 'A31_NATIVE_PACKET_INVALID'}
    seal = {'lot': 'A-31', 'packet': 'production/A-31/preuves/final',
            'files': helper.inventory(helper.OWN, helper.EXCLUDED)}
    (BASE / 'manifest.json').write_text(json.dumps(seal, indent=2) + '\n', encoding='utf-8')
    production = load('a31_reseal_production', BASE / 'verify.py')
    saved = sys.argv
    try:
        sys.argv = [str(BASE / 'verify.py')]
        code = production.verify()
    finally:
        sys.argv = saved
    return {'exit_code': int(code != 'A31_PACKAGE_PASS'), 'code': code, 'readiness_claimed': False}


if __name__ == '__main__':
    try:
        result = main()
    except Exception:
        result = {'exit_code': 1, 'code': 'A31_PACKET_INVALID'}
    print(json.dumps(result))
    sys.exit(result['exit_code'])
