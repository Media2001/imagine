"""PARENT ONLY: preparation + sequential common gates; never a native fake."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a29_gates_runner', HERE / 'run.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-serialized', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    out = a.output.resolve()
    scratch = Path(os.environ.get('TMPDIR', 'C:/Users/Ced/AppData/Local/hermes/cache/scratch')).resolve()
    if sys.platform != 'win32' or not out.is_relative_to(scratch) or out == scratch:
        raise RuntimeError('A29_WINDOWS_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    sources, deps = r.manifest(r.OWN), r.manifest(r.DEPS)
    rows = []
    checks = []

    def execute(kind, command, console='utf-8'):
        log = out / (kind + '.log')
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': console,
               'PYTHONUTF8': '0' if console == 'cp1252' else '1'}
        # Existing PS1 entrypoints explicitly emit UTF-8, independently of Python's console context.
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=2400)
        text = (p.stdout + p.stderr).decode('utf-8', errors='strict').replace('\r\n', '\n')
        log.write_text(text, encoding='utf-8', newline='\n')
        ok = p.returncode == 0
        if kind.startswith('T01'):
            final = [line for line in text.splitlines() if line.startswith('REJEU : ')]
            ok = ok and len(final) == 1 and final[0].endswith('PASS') and re.search(r'REJEU : [1-9][0-9]* tests,', final[0]) is not None
        if kind.startswith('verify-'):
            d = json.loads(text)
            ok = ok and type(d.get('exit_code')) is int and d['exit_code'] == 0 and bool(d.get('checks'))
            ok = ok and all(c.get('status') == 'PASS' for c in d['checks'])
        rows.append({'kind': kind, 'command': command, 'console_context': console, 'exit_code': p.returncode,
                     'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
        checks.append({'check': kind, 'status': 'PASS' if ok else 'FAIL'})
        return ok

    try:
        prepared = execute('preparation', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                           '-File', 'wp/tests/preparer-image.ps1'])
        if prepared:
            for console in ('utf-8', 'cp1252'):
                execute('T01-' + console, ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                          '-File', 'wp/tests/rejouer.ps1'], console)
            for lot in ('a20', 'a21', 'a22'):
                execute('verify-' + lot, [sys.executable, '-B', 'wp/tests/' + lot + '/verify.py',
                                         'production/A-' + lot[1:] + '/preuves/final'])
    except Exception as error:
        checks.append({'check': 'exception_' + type(error).__name__, 'status': 'FAIL'})
    stable = sources == r.manifest(r.OWN) and deps == r.manifest(r.DEPS)
    checks.append({'check': 'frozen_sources_and_dependencies', 'status': 'PASS' if stable else 'FAIL'})
    checks.append({'check': 'all_named_gates_executed', 'status': 'PASS' if [row['kind'] for row in rows] == [
        'preparation', 'T01-utf-8', 'T01-cp1252', 'verify-a20', 'verify-a21', 'verify-a22'] else 'FAIL'})
    result = {'scope': 'parent_common_gates', 'readiness_claimed': False, 'sources': sources,
              'dependencies': deps, 'rows': rows, 'checks': checks,
              'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    (out / 'parent-gates.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
