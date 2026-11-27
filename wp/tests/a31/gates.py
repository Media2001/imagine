"""PARENT ONLY: serial common gates; never run this alongside A30/another Docker user."""
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


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--parent-serialized', action='store_true', required=True)
    a = ap.parse_args()
    output = a.output.resolve()
    if output.is_relative_to(ROOT) or ROOT.is_relative_to(output):
        raise RuntimeError('A31_SCRATCH_REQUIRED')
    output.mkdir(parents=True, exist_ok=False)
    runner = load('a31_gate_runner', HERE / 'run.py')
    helper = load('a31_gate_delivery', HERE / 'delivery.py')
    roots = list(dict.fromkeys(runner.OWN + runner.DEPS + ['wp/tests/t01', 'wp/tests/preparer-image.ps1',
                 'wp/tests/rejouer.ps1', 'production/A-22/verify.py', 'production/A-28/verify.py',
                 'production/A-28/preuves/final/dependency-invalidations.json']))
    before = helper.inventory(roots)
    commands = [('prepare-image', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                  'wp/tests/preparer-image.ps1'], 'utf-8', '1')]
    for console, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        commands.append(('global-' + console, ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                               '-File', 'wp/tests/rejouer.ps1'], encoding, mode))
    commands += [('a' + n + '-readonly', [sys.executable, '-B', 'production/A-' + n + '/verify.py'], 'utf-8', '1')
                 for n in ('20', '21', '22', '28')]
    rows = []
    for name, command, encoding, mode in commands:
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('TMPDIR', None)
        try:
            p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
            # The canonical PowerShell runner emits UTF-8 bytes; Python children use their explicitly set encoding.
            decode = 'utf-8' if command[0] == 'powershell.exe' else encoding
            stdout = p.stdout.decode(decode, errors='strict').replace('\r\n', '\n')
            stderr = p.stderr.decode(decode, errors='strict').replace('\r\n', '\n')
            code = p.returncode
        except Exception:
            stdout, stderr, code = '', 'A31_GATE_EXECUTION_FAILED\n', 1
        row = {'name': name, 'command': command, 'exit_code': code, 'console': encoding,
               'sources_stable': before == helper.inventory(roots)}
        for field, value in [('stdout', stdout), ('stderr', stderr)]:
            path = output / (name + '.' + field + '.log')
            path.write_text(value, encoding='utf-8', newline='\n')
            row[field] = path.name
            row[field + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(row)
    stable = before == helper.inventory(roots)
    for name, value in [('commands.json', rows), ('sources.json', before), ('source-roots.json', roots),
                        ('result.json', {'exit_code': int(not stable or any(r['exit_code'] != 0 for r in rows)),
                                         'sources_stable': stable})]:
        (output / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    valid = helper.gate_logs_valid(output)
    result = {'exit_code': int(not valid), 'sources_stable': stable,
              'checks': [{'check': 'A31_PARENT_GATES', 'status': 'PASS' if valid else 'FAIL'}]}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
