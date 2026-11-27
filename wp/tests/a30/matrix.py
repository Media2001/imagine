"""A30 real Windows Python matrix; native execution is an explicit parent gate."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT = ROOT / 'production/A-30/preuves/final'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=DEFAULT)
    ap.add_argument('--with-native', action='store_true', help='Parent only, after A28 import freeze')
    ap.add_argument('--refresh-python', action='store_true', help='Replace ONLY the default incomplete A30 packet')
    args = ap.parse_args()
    if sys.platform != 'win32':
        raise RuntimeError('A30_WINDOWS_REQUIRED')
    out = args.output.resolve()
    if args.refresh_python:
        if out != DEFAULT.resolve() or not (out / 'candidate.json').is_file():
            raise RuntimeError('A30_REFRESH_UNSAFE')
        previous = json.loads((out / 'candidate.json').read_text(encoding='utf-8'))
        if previous.get('native_executed') is not False:
            raise RuntimeError('A30_REFRESH_NATIVE_FORBIDDEN')
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    probe = "import sys,locale,json; print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"
    for label, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / label; folder.mkdir()
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode, 'PYTHONDONTWRITEBYTECODE': '1'}
        p = subprocess.run([sys.executable, '-B', '-c', probe], env=env, capture_output=True, timeout=30)
        if p.returncode:
            raise RuntimeError('A30_ENV_PROBE_FAILED')
        (folder / 'environment.json').write_text(json.dumps(json.loads(p.stdout.decode(encoding)), indent=2) + '\n', encoding='utf-8')
        command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a30', '-p', 'test_*.py', '-v']
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
        text = (p.stdout.decode(encoding) + p.stderr.decode(encoding)).replace('\r\n', '\n')
        log = folder / 'python-tests.log'; log.write_text(text, encoding='utf-8', newline='\n')
        match = re.search(r'Ran (\d+) tests? in ', text)
        rows.append({'console': encoding, 'command': command, 'exit_code': p.returncode,
                     'tests_run': int(match[1]) if match else 0,
                     'all_pass': p.returncode == 0 and 'OK' in text.splitlines(),
                     'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()})
        if args.with_native:
            command = [sys.executable, '-B', str(HERE / 'run.py'), '--output=' + str(folder / 'native')]
            p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=1800)
            (folder / 'runner-console.log').write_bytes(p.stdout + p.stderr)
            rows.append({'console': encoding, 'command': command, 'exit_code': p.returncode,
                         'kind': 'native', 'executed': True})
    spec = importlib.util.spec_from_file_location('a30_runner_manifest', HERE / 'run.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    for filename, value in [('sources.json', runner.manifest(runner.OWN)),
                            ('candidate.json', {'status': 'CANDIDAT_GATE_PARENT', 'readiness_claimed': False,
                                                'native_executed': args.with_native,
                                                'parent_preparation': 'pending', 'parent_global_T01': 'pending'}),
                            ('windows-matrix.json', {'rows': rows, 'exit_code': int(any(r['exit_code'] != 0 or r.get('all_pass') is False for r in rows))})]:
        (out / filename).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rows': rows, 'native_executed': args.with_native, 'readiness_claimed': False}, indent=2))
    return int(any(r['exit_code'] != 0 or r.get('all_pass') is False for r in rows))


if __name__ == '__main__':
    sys.exit(main())
