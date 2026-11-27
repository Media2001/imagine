"""Collect the common-contract blocker honestly; no readiness or global gates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path.home() / 'AppData/Local/hermes/cache/scratch'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for name, encoding, utf8 in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / name
        folder.mkdir()
        temporary = out / (name + '-temp')
        temporary.mkdir()
        env = {**os.environ, 'TEMP': str(temporary), 'TMP': str(temporary),
               'PYTHONIOENCODING': encoding, 'PYTHONUTF8': utf8, 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('TMPDIR', None)
        probe = subprocess.run([sys.executable, '-B', '-c',
            "import os,sys,tempfile,json; print(json.dumps({'python':sys.version,'executable':sys.executable,'encoding':sys.stdout.encoding,'tmpdir_present':'TMPDIR' in os.environ,'temp':tempfile.gettempdir()}))"],
            cwd=ROOT, env=env, capture_output=True, timeout=30)
        measured = json.loads(probe.stdout.decode(encoding))
        command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a32', '-p', 'test_*.py', '-v']
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=120)
        log = folder / 'python-tests.log'
        log.write_text((p.stdout + p.stderr).decode(encoding).replace('\r\n', '\n'), encoding='utf-8', newline='\n')
        row = {'command': command, 'encoding': encoding, 'exit_code': p.returncode,
               'tmpdir_present': measured['tmpdir_present'], 'temp_is_scratch': Path(measured['temp']).is_relative_to(SCRATCH),
               'probe': measured, 'log': name + '/python-tests.log', 'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
        rows.append(row)
    (out / 'windows-matrix.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    command = [sys.executable, '-B', 'wp/tests/a32/run.py', '--output=' + str(out / 'native')]
    p = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=4500,
                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
    (out / 'runner-console.log').write_text((p.stdout + p.stderr).decode('utf-8').replace('\r\n', '\n'), encoding='utf-8', newline='\n')
    (out / 'collection.json').write_text(json.dumps({'native_command': command, 'native_exit_code': p.returncode,
        'windows_suites_pass': all(r['exit_code'] == 0 for r in rows), 'readiness': False,
        'native_cp1252_not_played': True, 'gates_not_played': True}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'native_exit_code': p.returncode, 'readiness': False}))
    return p.returncode


if __name__ == '__main__':
    sys.exit(main())
