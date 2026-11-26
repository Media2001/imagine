"""Windows UTF-8/cp1252 evidence. Native containers require explicit parent opt-in."""
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
    m = re.search(r'Ran (\d+) tests? in ', text)
    total = int(m[1]) if m else 0
    return {'tests_run': total, 'all_pass': returncode == 0 and 'OK' in text.splitlines() and total > 0}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--include-native', action='store_true')
    ap.add_argument('--parent-serialized', action='store_true')
    a = ap.parse_args()
    if a.include_native and not a.parent_serialized:
        ap.error('--include-native requires --parent-serialized')
    if sys.platform != 'win32':
        raise RuntimeError('A29_WINDOWS_REQUIRED')
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A29_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    probe = "import sys,locale,json;print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"
    spec = importlib.util.spec_from_file_location('a29_runner', HERE / 'run.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    before, deps = runner.manifest(runner.OWN), runner.manifest(runner.DEPS)

    def execute(command, env, encoding, log, kind):
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
        text = (p.stdout.decode(encoding, errors='strict') + p.stderr.decode(encoding, errors='strict')).replace('\r\n', '\n')
        log.write_text(text, encoding='utf-8', newline='\n')
        row = {'kind': kind, 'command': command, 'console': encoding, 'exit_code': p.returncode,
               'log': log.relative_to(out).as_posix(), 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
        if kind == 'python':
            row.update(python_summary(text, p.returncode))
        rows.append(row)

    for console, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / console
        folder.mkdir()
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode,
               'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': 'C:/Users/Ced/AppData/Local/hermes/cache/scratch'}
        p = subprocess.run([sys.executable, '-B', '-c', probe], env=env, capture_output=True, timeout=30)
        if p.returncode:
            raise RuntimeError('A29_ENVIRONMENT_PROBE_FAILED')
        (folder / 'environment.json').write_text(json.dumps(json.loads(p.stdout.decode(encoding)), indent=2) + '\n', encoding='utf-8')
        execute([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a29', '-p', 'test_*.py', '-v'],
                env, encoding, folder / 'python-tests.log', 'python')
        if a.include_native:
            execute([sys.executable, '-B', 'wp/tests/a29/run.py', '--parent-serialized', '--output=' + str(folder / 'native')],
                    env, encoding, folder / 'runner-console.log', 'native')
    if a.include_native:
        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
        execute([sys.executable, '-B', 'wp/tests/a29/style.py', '--parent-serialized', '--output=' + str(out / 'style')],
                env, 'utf-8', out / 'style-console.log', 'style')
    stable = before == runner.manifest(runner.OWN) and deps == runner.manifest(runner.DEPS)
    for filename, data in [('sources.json', before), ('dependencies.json', deps)]:
        (out / filename).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    result = {'scope': 'python_and_native' if a.include_native else 'python_only', 'readiness_claimed': False,
              'sources_stable': stable, 'rows': rows,
              'exit_code': int(not stable or any(row['exit_code'] != 0 or row.get('all_pass') is False for row in rows))}
    (out / 'windows-matrix.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
