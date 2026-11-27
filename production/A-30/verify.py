"""A30 sealed package reader. No arguments, no site access or native execution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
OWN = ['wp/outils/bascule/a30', 'wp/tests/a30', 'production/A-30']


def inventory():
    files = []
    for key in OWN:
        root = ROOT / key
        if not root.is_dir():
            raise ValueError('PACKAGE_DRIFT')
        files += [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and p not in (BASE / 'manifest.json', BASE / 'PRET')]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    if len(sys.argv) != 1:
        return {'exit_code': 1, 'code': 'NO_ARGUMENTS'}
    try:
        seal = json.loads((BASE / 'manifest.json').read_bytes())
        if (seal['lot'] != 'A-30' or seal['packet'] != 'production/A-30/preuves/final'
                or seal['file_count'] != len(seal['files']) or seal['files'] != inventory()):
            raise ValueError('PACKAGE_DRIFT')
    except Exception:
        return {'exit_code': 1, 'code': 'PACKAGE_DRIFT'}
    p = subprocess.run([sys.executable, '-B', str(ROOT / 'wp/tests/a30/verify.py')], cwd=ROOT,
                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'},
                       capture_output=True, timeout=90)
    try:
        data = json.loads(p.stdout)
        if p.returncode or p.stderr or data['exit_code'] != 0 or data['native_proven'] is not True:
            raise ValueError
    except Exception:
        return {'exit_code': 1, 'code': 'NATIVE_PACKET_INVALID'}
    return {'exit_code': 0, 'lot': 'A-30', 'package': 'PASS', 'native_packet': 'PASS'}


if __name__ == '__main__':
    try:
        result = main()
    except Exception:
        result = {'exit_code': 1, 'code': 'NATIVE_PACKET_INVALID'}
    print(json.dumps(result))
    sys.exit(result['exit_code'])
