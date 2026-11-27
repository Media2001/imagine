"""A32 no-argument read-only verifier: partial evidence is never a PASS."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'production/A-32'


def verify():
    if len(sys.argv) != 1:
        return 'A32_ARGUMENTS_REFUSED'
    spec = importlib.util.spec_from_file_location('a32_production_delivery', ROOT / 'wp/tests/a32/delivery.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    seal = m.read(BASE / 'manifest.json')
    if seal.get('lot') != 'A-32' or seal.get('packet') != 'production/A-32/preuves/final':
        return 'A32_PACKET_INVALID'
    if seal['files'] != m.inventory(m.OWN, m.EXCLUDED):
        return 'A32_PACKAGE_DRIFT'
    for path in (ROOT / 'wp/outils/bascule/README.md', ROOT / 'wp/outils/bascule/tournee/README.md'):
        lines = path.read_bytes().splitlines(keepends=True)
        for line in (BASE / 'readme-contract.txt').read_bytes().splitlines(keepends=True):
            count = lines.count(line) if path.parent.name != 'tournee' else [value.rstrip(b'\r\n') for value in lines].count(line.rstrip(b'\r\n'))
            if count != 1:
                return 'A32_README_CONTRACT_DRIFT'
    if not m.local_valid(BASE / 'preuves/final'):
        return 'A32_PARTIAL_EVIDENCE'
    gates = BASE / 'preuves/final/gates'
    if seal.get('complete') is not True or not gates.is_dir() or not m.gates_valid(gates):
        return 'A32_GATES_MISSING'
    return 'A32_PACKAGE_PASS'


def main():
    try:
        code = verify()
    except Exception:
        code = 'A32_PACKET_INVALID'
    failed = code != 'A32_PACKAGE_PASS'
    result = {'lot': 'A-32', 'exit_code': int(failed), 'readiness_claimed': False,
              'checks': [{'check': code, 'status': 'FAIL' if failed else 'PASS'}]}
    if failed:
        result['code'] = code
    print(json.dumps(result))
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
