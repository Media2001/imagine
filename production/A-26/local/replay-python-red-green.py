"""Replay a real Python RED/GREEN witness in a disposable canonical-depth mirror.
No PHP, WSL, Docker, site, database, archive or network is invoked.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a26_python_rg_sources', ROOT / 'wp/tests/a26/run.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
original = r.manifest(r.OWN)
dependencies = r.manifest(r.DEPS)
rows = []
with tempfile.TemporaryDirectory(prefix='a26-python-red-green-', dir=os.environ.get('TMPDIR')) as tmp:
    mirror = Path(tmp)
    for relative in {**original, **dependencies}:
        target = mirror / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    subject = mirror / 'wp/outils/bascule/a26/report.py'
    saved = subject.read_bytes()
    needle = b"    if data['neutralisation'] == UNKNOWN:\n        return content == UNKNOWN\n"
    assert saved.count(needle) == 1
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a26', '-p', 'test_*.py', '-v']
    for phase in ('red', 'green'):
        subject.write_bytes(saved.replace(needle, b'') if phase == 'red' else saved)
        for console, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
            env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
            p = subprocess.run(command, cwd=mirror, env=env, capture_output=True, timeout=120)
            log = OUT / ('python-rg-' + phase + '-' + console + '.log')
            text = (p.stdout + p.stderr).decode(encoding).replace('\r\n', '\n')
            log.write_bytes(text.encode('utf-8'))
            expected = (p.returncode == 1 and 'test_neutralised_source_counts_unknown_not_zero' in text
                        and 'FAILED (failures=1)' in text) if phase == 'red' else (p.returncode == 0 and '\nOK\n' in text)
            rows.append({'phase': phase, 'console': console, 'encoding': encoding, 'utf8_mode': mode,
                         'command': command, 'exit_code': p.returncode, 'expected_outcome_observed': expected,
                         'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
    assert subject.read_bytes() == saved
receipt = {'kind': 'real Python-only RED/GREEN, disposable missing-neutralisation mutation',
           'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': rows,
           'sources': original, 'dependencies': dependencies,
           'original_sources_unchanged': original == r.manifest(r.OWN),
           'dependencies_unchanged': dependencies == r.manifest(r.DEPS),
           'php_docker_wsl_executed': False,
           'exit_code': int(not all(row['expected_outcome_observed'] for row in rows))}
(OUT / 'python-red-green.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
print(json.dumps({key: value for key, value in receipt.items() if key not in ('sources', 'dependencies')}, indent=2))
sys.exit(receipt['exit_code'])
