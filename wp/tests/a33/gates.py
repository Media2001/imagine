"""A33 canonical gates, strictly serialized, no runner changes or exclusions."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
from delivery import ROOT, digest, gates_valid, inventory, load


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--parent-serialized', required=True, action='store_true')
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A33_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    r = load('a33_gate_runner', Path(__file__).with_name('run.py'))
    before = inventory(r.OWN + r.DEPS)
    rows = []
    for name, script, encoding, mode in [('prepare-image', 'preparer-image.ps1', 'utf-8', '1'), ('global-utf8', 'rejouer.ps1', 'utf-8', '1'), ('global-cp1252', 'rejouer.ps1', 'cp1252', '0')]:
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/' + script]
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('TMPDIR', None)
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
        row = {'name': name, 'command': command, 'encoding': encoding, 'exit_code': p.returncode, 'tmpdir_present': 'TMPDIR' in env, 'sources_stable': before == inventory(r.OWN + r.DEPS)}
        for key, raw in [('stdout', p.stdout), ('stderr', p.stderr)]:
            path = out / (name + '.' + key + '.log')
            path.write_text(raw.decode('utf-8', errors='strict').replace('\r\n', '\n'), encoding='utf-8', newline='\n')
            row[key], row[key + '_sha256'] = path.name, digest(path)
        rows.append(row)
        print(json.dumps({'gate': name, 'exit_code': p.returncode}), flush=True)
        # Preserve both real console receipts even when the first gate is red.
    stable = before == inventory(r.OWN + r.DEPS)
    for filename, value in [('commands.json', rows), ('sources.json', before), ('result.json', {'exit_code': int(not stable or len(rows) != 3 or any(x['exit_code'] != 0 for x in rows)), 'sources_stable': stable})]:
        (out / filename).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    valid = gates_valid(out)
    if not valid:
        (out / 'result.json').write_text(json.dumps({'exit_code': 1, 'sources_stable': stable,
            'checks': [{'check': 'A33_CANONICAL_GATES', 'status': 'FAIL'}]}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'exit_code': int(not valid), 'canonical_gates_verified': valid}))
    return int(not valid)


if __name__ == '__main__':
    sys.exit(main())
