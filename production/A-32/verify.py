"""A32 no-argument read-only verifier: partial evidence is never a PASS."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'production/A-32'


def verify():
    if len(sys.argv) != 1:
        return 'A32_ARGUMENTS_REFUSED'
    seal = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    if seal.get('lot') != 'A-32' or seal.get('packet') != 'production/A-32/preuves/final':
        return 'A32_PACKET_INVALID'
    for key, digest in seal['files'].items():
        p = ROOT / key
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            return 'A32_PACKAGE_DRIFT'
    lines = (ROOT / 'wp/outils/bascule/README.md').read_bytes().splitlines(keepends=True)
    for line in (BASE / 'readme-contract.txt').read_bytes().splitlines(keepends=True):
        if lines.count(line) != 1:
            return 'A32_README_CONTRACT_DRIFT'
    matrix = json.loads((BASE / 'preuves/final/windows-matrix.json').read_text(encoding='utf-8'))
    if len(matrix) != 2 or {r['encoding'] for r in matrix} != {'utf-8', 'cp1252'} or any(
            r['exit_code'] != 0 or r['tmpdir_present'] or not r['temp_is_scratch'] for r in matrix):
        return 'A32_WINDOWS_INVALID'
    native = BASE / 'preuves/final/native'
    result = json.loads((native / 'result.json').read_text(encoding='utf-8'))
    runner = json.loads((native / 'runner.json').read_text(encoding='utf-8'))
    if result['exit_code'] != 0 or runner['exit_code'] != 0 or any(
            c['status'] != 'PASS' for d in (result, runner) for c in d['checks']):
        return 'A32_PARTIAL_EVIDENCE'
    for storage in ('classic', 'hpos'):
        wanted = {storage + ':' + name for name in ('documented_command_exact_complete',
                  'named_doubles_continue_every_remaining_real_tool', 'every_tool_checks_site',
                  'whole_tour_all_tables_scheduler_files_immutable', 'config_never_executed')}
        if not wanted.issubset({c['check'] for c in result['checks'] if c['status'] == 'PASS'}):
            return 'A32_PARTIAL_EVIDENCE'
    gates = BASE / 'preuves/final/gates/result.json'
    if not gates.is_file() or json.loads(gates.read_text(encoding='utf-8')).get('exit_code') != 0:
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
