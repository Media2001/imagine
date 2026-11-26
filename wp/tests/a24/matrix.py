"""One final A24 Windows UTF-8/cp1252 replay; output only into fresh scratch."""
import argparse
import datetime
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
spec = importlib.util.spec_from_file_location('a24_matrix_verifier', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def save(path, data):
    path.write_bytes((json.dumps(data, indent=2, ensure_ascii=True) + '\n').encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT) or sys.platform != 'win32' or sys.version_info[:2] != (3, 14):
        raise RuntimeError('A24_WINDOWS314_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    initial, deps = v.inventory(ROOT, v.OWN), v.inventory(ROOT, v.DEPS)
    matrix = {'suite': 'A24-final-replay', 'started': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'platform': sys.platform, 'python': {'executable': sys.executable, 'version': sys.version},
              'contexts': {}, 'exit_code': 1}
    for context, encoding, utf8 in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': utf8, 'PYTHONDONTWRITEBYTECODE': '1'}
        target = out / context
        command = [sys.executable, '-B', str(HERE / 'run.py'), '--output=' + str(target)]
        native = subprocess.run(command, capture_output=True, timeout=1800, cwd=ROOT, env=env)
        target.mkdir(exist_ok=True)
        (target / 'runner-command.log').write_bytes((native.stdout.decode(encoding) + native.stderr.decode(encoding)).encode('utf-8'))
        probe = subprocess.run([sys.executable, '-B', '-c',
                                'import sys,locale,json;print(json.dumps(dict(executable=sys.executable,version=sys.version,platform=sys.platform,stdout_encoding=sys.stdout.encoding,stderr_encoding=sys.stderr.encoding,locale=locale.getencoding(),preferred=locale.getpreferredencoding(False),utf8_mode=sys.flags.utf8_mode)))'],
                               capture_output=True, timeout=30, env=env)
        if probe.returncode:
            raise RuntimeError('A24_ENCODING_PROBE_FAILED')
        runtime = json.loads(probe.stdout.decode(encoding))
        tests = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(HERE), '-p', 'test_*.py', '-v'],
                               capture_output=True, timeout=180, cwd=ROOT, env=env)
        log = tests.stdout.decode(encoding) + tests.stderr.decode(encoding)
        (target / 'python.log').write_bytes(log.encode('utf-8'))
        found = re.search(r'^Ran (\d+) tests? in ', log, re.M)
        receipt = {'suite': 'A24-Windows-unittest', 'encoding': encoding, 'python': runtime,
                   'tests': int(found[1]) if found else 0, 'exit_code': tests.returncode,
                   'log_sha256': hashlib.sha256((target / 'python.log').read_bytes()).hexdigest()}
        save(target / 'python.json', receipt)
        matrix['contexts'][context] = {'native_exit': native.returncode, 'python_exit': tests.returncode,
                                       'python_tests': receipt['tests'], 'encoding': encoding,
                                       'command': command, 'encoding_runtime': runtime}
        print(json.dumps({'context': context, **matrix['contexts'][context]}, ensure_ascii=True), flush=True)
    matrix['sources_stable'] = initial == v.inventory(ROOT, v.OWN)
    matrix['dependencies_stable'] = deps == v.inventory(ROOT, v.DEPS)
    matrix['exit_code'] = int(not matrix['sources_stable'] or not matrix['dependencies_stable'] or
                              any(c['native_exit'] or c['python_exit'] or c['python_tests'] < 15 for c in matrix['contexts'].values()))
    save(out / 'matrix.json', matrix)
    print(json.dumps({'suite': matrix['suite'], 'exit_code': matrix['exit_code']}))
    return matrix['exit_code']


if __name__ == '__main__':
    sys.exit(main())
