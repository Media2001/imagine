"""A31: no-argument read-only delivery verifier; never converts partial evidence to native PASS."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'production/A-31'
CODES = ('A31_ARGUMENTS_REFUSED', 'A31_PARTIAL_EVIDENCE', 'A31_PACKAGE_DRIFT', 'A31_PARENT_GATES_MISSING',
         'A31_NATIVE_PACKET_INVALID', 'A31_PACKET_INVALID', 'A31_PACKAGE_PASS')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify():
    if len(sys.argv) != 1:
        return 'A31_ARGUMENTS_REFUSED'
    if not (BASE / 'manifest.json').is_file() or not (BASE / 'preuves/final/windows-matrix.json').is_file():
        return 'A31_PARTIAL_EVIDENCE'
    helper = load('a31_delivery', ROOT / 'wp/tests/a31/delivery.py')
    seal = helper.read(BASE / 'manifest.json')
    if seal.get('lot') != 'A-31' or seal.get('packet') != 'production/A-31/preuves/final':
        return 'A31_PACKET_INVALID'
    if seal['files'] != helper.inventory(helper.OWN, helper.EXCLUDED):
        return 'A31_PACKAGE_DRIFT'
    gates = BASE / 'preuves/final/gates'
    if not gates.is_dir() or not helper.gate_logs_valid(gates):
        return 'A31_PARENT_GATES_MISSING'
    native = load('a31_native_verify', ROOT / 'wp/tests/a31/verify.py')
    result = native.verify(BASE / 'preuves/final', False)
    if result['exit_code'] != 0 or result['scope'] != 'python_and_native':
        return 'A31_NATIVE_PACKET_INVALID'
    return 'A31_PACKAGE_PASS'


def main():
    try:
        code = verify()
    except Exception:
        code = 'A31_PACKET_INVALID'
    exit_code = int(code != 'A31_PACKAGE_PASS')
    print(json.dumps({'lot': 'A-31', 'exit_code': exit_code, 'code': code, 'readiness_claimed': False,
                      'checks': [{'check': code, 'status': 'FAIL' if exit_code else 'PASS'}]}))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
