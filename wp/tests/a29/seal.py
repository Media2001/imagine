"""Seal only a genuinely verified A29 packet. No readiness marker, no Docker."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCTION = ROOT / 'production/A-29'
spec = importlib.util.spec_from_file_location('a29_seal_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def inventory(folder):
    if folder.is_symlink() or any(p.is_symlink() for p in folder.rglob('*')):
        raise RuntimeError('A29_SEAL_REFUSED')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts
            and p.name not in {'PRET', 'manifest.json', 'manifest-python-partiel.json'}}


def gates_valid(path, sources, deps):
    try:
        path = path.resolve(strict=True)
        if not path.is_relative_to(PRODUCTION) or path.is_symlink():
            return False
        d = v.read(path)
        if (not v.receipt_valid(d) or d.get('scope') != 'parent_common_gates'
                or d.get('readiness_claimed') is not False or d['sources'] != sources or d['dependencies'] != deps):
            return False
        if [row['kind'] for row in d['rows']] != ['preparation', 'T01-utf-8', 'T01-cp1252', 'verify-a20', 'verify-a21', 'verify-a22']:
            return False
        for row in d['rows']:
            log = path.parent / row['log']
            if (type(row['exit_code']) is not int or row['exit_code'] != 0 or log.is_symlink()
                    or not log.resolve().is_relative_to(path.parent) or hashlib.sha256(log.read_bytes()).hexdigest() != row['log_sha256']):
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--python-only', action='store_true')
    parser.add_argument('--gates', type=Path)
    a = parser.parse_args()
    packet = a.evidence.resolve(strict=True)
    expected = PRODUCTION / 'preuves' / ('partiel-python' if a.python_only else 'final')
    if packet != expected.resolve() or a.evidence.is_symlink() or expected.is_symlink():
        raise RuntimeError('A29_OWNED_PACKET_REQUIRED')
    if not a.python_only and (PRODUCTION / 'preuves/partiel-python').exists():
        raise RuntimeError('A29_SINGLE_PACKET_REQUIRED')
    name = 'manifest-python-partiel.json' if a.python_only else 'manifest.json'
    target = PRODUCTION / name
    if target.exists():
        raise RuntimeError('A29_NEW_SEAL_REQUIRED')
    p = subprocess.run([sys.executable, '-B', str(HERE / 'verify.py'), '--evidence=' + str(packet),
                        *(['--python-only'] if a.python_only else [])], capture_output=True, timeout=240,
                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
    result = json.loads(p.stdout.decode('utf-8'))
    if p.returncode or p.stderr or not v.receipt_valid(result):
        raise RuntimeError('A29_PACKET_NOT_VERIFIED')
    sources, deps = v.read(packet / 'sources.json'), v.read(packet / 'dependencies.json')
    if not a.python_only and (not a.gates or not gates_valid(a.gates, sources, deps)):
        raise RuntimeError('A29_PARENT_GATES_REQUIRED')
    verification = PRODUCTION / ('verification-python-partielle.json' if a.python_only else 'verification-finale.json')
    verification.write_bytes(p.stdout)
    files = {}
    for folder in (ROOT / 'wp/outils/bascule/a29', HERE, PRODUCTION):
        files.update(inventory(folder))
    report = {'scope': 'python_only_partial' if a.python_only else 'python_and_native_parent_gates',
              'readiness_claimed': False, 'exit_code': 0, 'evidence': packet.relative_to(ROOT).as_posix(),
              'verification': verification.relative_to(ROOT).as_posix(),
              'executed_sources': sources, 'executed_dependencies': deps, 'files': files}
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'seal': target.relative_to(ROOT).as_posix(), 'scope': report['scope'],
                      'files': len(files), 'exit_code': 0, 'readiness_claimed': False}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        allowed = {'A29_OWNED_PACKET_REQUIRED', 'A29_SINGLE_PACKET_REQUIRED', 'A29_NEW_SEAL_REQUIRED',
                   'A29_PACKET_NOT_VERIFIED', 'A29_PARENT_GATES_REQUIRED'}
        code = str(error) if isinstance(error, RuntimeError) and str(error) in allowed else 'A29_SEAL_REFUSED'
        print(json.dumps({'exit_code': 1, 'code': code, 'readiness_claimed': False}))
        sys.exit(1)
