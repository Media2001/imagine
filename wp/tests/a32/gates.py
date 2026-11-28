"""A32 serial preparation/global gates; real packet failures remain failures."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
from delivery import ROOT, digest, gates_valid, inventory, read


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A32_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    roots = read(ROOT / 'production/A-32/source-roots.json')['gates']
    before = inventory(roots)
    commands = [('prepare-image', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1'], 'utf-8', '1')]
    commands += [('global-' + name, ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], encoding, mode)
                 for name, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]]
    commands += [('a' + n + '-readonly', [sys.executable, '-B', 'production/A-' + n + '/verify.py'], 'utf-8', '1') for n in ('20', '21', '22', '28')]
    rows = []
    for name, command, encoding, mode in commands:
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('TMPDIR', None)
        try:
            p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
            decode = 'utf-8' if command[0] == 'powershell.exe' else encoding
            stdout, stderr = [v.decode(decode, errors='strict').replace('\r\n', '\n') for v in (p.stdout, p.stderr)]
            code = p.returncode
        except Exception:
            stdout, stderr, code = '', 'A32_GATE_EXECUTION_FAILED\n', 1
        row = {'name': name, 'command': command, 'exit_code': code, 'encoding': encoding,
               'tmpdir_present': 'TMPDIR' in env, 'sources_stable': before == inventory(roots)}
        for field, value in [('stdout', stdout), ('stderr', stderr)]:
            path = out / (name + '.' + field + '.log')
            path.write_text(value, encoding='utf-8', newline='\n')
            row[field], row[field + '_sha256'] = path.name, digest(path)
        rows.append(row)
        print(json.dumps({'gate': name, 'exit_code': code}), flush=True)
    stable = before == inventory(roots)
    for name, data in [('commands.json', rows), ('sources.json', before), ('source-roots.json', roots),
                       ('result.json', {'exit_code': int(not stable or any(r['exit_code'] != 0 for r in rows)), 'sources_stable': stable})]:
        (out / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    valid = gates_valid(out)
    result = {'exit_code': int(not valid), 'sources_stable': stable,
              'checks': [{'check': 'A32_CANONICAL_GATES', 'status': 'PASS' if valid else 'FAIL'}]}
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
