"""Real RED/GREEN report tests on disposable mirrors in both Windows encodings."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    checks = []
    source = (ROOT / 'wp/outils/bascule/a29/report.py').read_bytes()
    tests = (HERE / 'test_report.py').read_bytes()
    old = "row['count'] < 5"
    text = source.decode('utf-8')
    if text.count(old) != 1:
        raise RuntimeError('A29_RED_MUTATION_TARGET')
    for console, mode in [('utf-8', '1'), ('cp1252', '0')]:
        with tempfile.TemporaryDirectory(prefix='a29-red-', dir=os.environ.get('TMPDIR')) as temporary:
            mirror = Path(temporary)
            tools = mirror / 'wp/outils/bascule/a29'
            bank = mirror / 'wp/tests/a29'
            tools.mkdir(parents=True)
            bank.mkdir(parents=True)
            subject = tools / 'report.py'
            subject.write_bytes(source)
            (bank / 'test_report.py').write_bytes(tests)
            env = {**os.environ, 'PYTHONIOENCODING': console, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
            command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a29',
                       '-p', 'test_report.py', '-k', 'test_k5_and_closed_family', '-v']
            for phase in ('baseline-green', 'mutation-red', 'restored-green'):
                if phase == 'mutation-red':
                    subject.write_text(text.replace(old, "row['count'] < 4"), encoding='utf-8', newline='\n')
                elif phase == 'restored-green':
                    subject.write_bytes(source)
                p = subprocess.run(command, cwd=mirror, env=env, capture_output=True, timeout=60)
                log_text = (p.stdout + p.stderr).decode(console, errors='strict').replace('\r\n', '\n')
                log = output / (console + '-' + phase + '.log')
                log.write_text(log_text, encoding='utf-8', newline='\n')
                is_red = phase == 'mutation-red'
                ok = (p.returncode == (1 if is_red else 0) and 'Ran 1 test in ' in log_text
                      and ('FAIL: test_k5_and_closed_family' in log_text and 'FAILED (failures=1)' in log_text
                           if is_red else log_text.endswith('\nOK\n')))
                rows.append({'console': console, 'phase': phase, 'exit_code': p.returncode, 'command': command,
                             'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
                checks.append({'check': console + ':' + phase, 'status': 'PASS' if ok else 'FAIL'})
            checks.append({'check': console + ':exact_restore', 'status': 'PASS' if subject.read_bytes() == source else 'FAIL'})
    checks.append({'check': 'repository_unchanged', 'status': 'PASS' if source == (ROOT / 'wp/outils/bascule/a29/report.py').read_bytes()
                   and tests == (HERE / 'test_report.py').read_bytes() else 'FAIL'})
    result = {'scope': 'python_closed_schema_mutation_only', 'readiness_claimed': False, 'rows': rows, 'checks': checks,
              'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    (output / 'red-python.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result
