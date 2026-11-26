"""Full A23 Windows UTF-8/cp1252 matrix, external fresh evidence only."""
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


def python_summary(text, returncode):
    match = re.search(r'Ran (\d+) tests? in ', text)
    total = int(match[1]) if match else 0
    return {'tests_run': total, 'all_pass': returncode == 0 and 'OK' in text.splitlines() and total > 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    if sys.platform != 'win32':
        raise RuntimeError('A23_WINDOWS_REQUIRED')
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    probe = "import sys,locale,json; print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,'version_info':list(sys.version_info[:3]),'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"

    def execute(command, env, encoding, log):
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
        text = (p.stdout.decode(encoding, errors='strict') + p.stderr.decode(encoding, errors='strict')).replace('\r\n', '\n')
        log.write_text(text, encoding='utf-8', newline='\n')
        row = {'command': command, 'console': encoding, 'exit_code': p.returncode,
               'log': log.relative_to(out).as_posix(), 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
        if '-m' in command and 'unittest' in command:
            row.update(python_summary(text, p.returncode))
        rows.append(row)
        return p

    for console, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / console
        folder.mkdir()
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode,
               'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': 'C:/Users/Ced/AppData/Local/hermes/cache/scratch'}
        p = subprocess.run([sys.executable, '-B', '-c', probe], env=env, capture_output=True, timeout=30)
        assert p.returncode == 0
        (folder / 'environment.json').write_text(json.dumps(json.loads(p.stdout.decode(encoding)), indent=2) + '\n', encoding='utf-8')
        execute([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a23', '-p', 'test_*.py', '-v'],
                env, encoding, folder / 'python-tests.log')
        execute([sys.executable, '-B', 'wp/tests/a23/run.py', '--output=' + str(folder / 'native')],
                env, encoding, folder / 'runner-console.log')
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    execute([sys.executable, '-B', 'wp/tests/a23/style.py', '--output=' + str(out / 'style')],
            env, 'utf-8', out / 'style-console.log')
    spec = importlib.util.spec_from_file_location('a23_runner', HERE / 'run.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    (out / 'sources.json').write_text(json.dumps(runner.manifest(runner.OWN), indent=2) + '\n', encoding='utf-8')
    (out / 'candidate.json').write_text(json.dumps({'status': 'CANDIDAT_GATE_PARENT', 'readiness_claimed': False,
                                                  'parent_preparation': 'pending', 'parent_global_T01': 'pending'}, indent=2) + '\n', encoding='utf-8')
    result = {'rows': rows, 'exit_code': int(any(row['exit_code'] != 0 or row.get('all_pass') is False for row in rows))}
    (out / 'windows-matrix.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
