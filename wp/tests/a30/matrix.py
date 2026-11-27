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
import tempfile

from temp_support import assert_outside_repo

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT = ROOT / 'production/A-30/preuves/final'
SCRATCH = Path.home() / 'AppData/Local/hermes/cache/scratch'


def clean_environment(encoding, mode, scratch, *, repo=ROOT):
    scratch = assert_outside_repo(scratch, repo=repo)
    env = {key: value for key, value in os.environ.items()
           if key.upper() not in {'TMPDIR', 'TEMP', 'TMP'}}
    env.update(TEMP=str(scratch), TMP=str(scratch), PYTHONIOENCODING=encoding,
               PYTHONUTF8=str(mode), PYTHONDONTWRITEBYTECODE='1')
    return env


def environment_valid(env, encoding, mode, scratch):
    try:
        expected = assert_outside_repo(scratch)
        return (env['platform'] == 'win32' and env['stdout'].lower() == encoding
                and env['stderr'].lower() == encoding and env['utf8_mode'] == mode
                and env['TMPDIR_present'] is False and env['TMPDIR'] is None
                and all(Path(env[key]).resolve() == expected for key in ('TEMP', 'TMP', 'tempdir'))
                and type(env['suite_discovered']) is int and env['suite_discovered'] > 0)
    except (KeyError, TypeError, ValueError, RuntimeError):
        return False


def test_result(text, returncode, discovered):
    text = text.replace('\r\n', '\n')
    matches = re.findall(r'^Ran (\d+) tests? in [^\n]+$', text, re.M)
    count = int(matches[0]) if len(matches) == 1 else 0
    finals = [line for line in text.splitlines() if line == 'OK' or line.startswith(('OK (', 'FAILED ('))]
    counters = {key: sum(int(n) for n in re.findall(r'\b' + key + r'=(\d+)', '\n'.join(finals)))
                for key in ('failures', 'errors', 'skipped')}
    return {'tests_run': count, 'suite_discovered': discovered, **counters,
            'all_pass': returncode == 0 and count == discovered and count > 0
                        and finals == ['OK'] and not any(counters.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=DEFAULT)
    ap.add_argument('--temp-root', type=Path, default=SCRATCH,
                    help='Authorized scratch parent for Windows standard TEMP/TMP')
    ap.add_argument('--with-native', action='store_true', help='Parent only, after A28 import freeze')
    ap.add_argument('--refresh-python', action='store_true', help='Replace ONLY the default incomplete A30 packet')
    args = ap.parse_args()
    if sys.platform != 'win32':
        raise RuntimeError('A30_WINDOWS_REQUIRED')
    temp_root = assert_outside_repo(args.temp_root)
    if not temp_root.is_dir():
        raise RuntimeError('A30_SCRATCH_PARENT_REQUIRED')
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
    probe = ("import sys,locale,json,os,tempfile,unittest;"
             "suite=unittest.defaultTestLoader.discover('wp/tests/a30',pattern='test_*.py');"
             "print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,"
             "'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),"
             "'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode,"
             "'TMPDIR_present':'TMPDIR' in os.environ,'TMPDIR':os.environ.get('TMPDIR'),"
             "'TEMP':os.environ.get('TEMP'),'TMP':os.environ.get('TMP'),'tempdir':tempfile.gettempdir(),"
             "'suite_discovered':suite.countTestCases()}))")
    temporary = tempfile.TemporaryDirectory(prefix='a30-clean-windows-', dir=temp_root)
    import atexit
    atexit.register(temporary.cleanup)
    scratch = temporary.name
    for label, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / label; folder.mkdir()
        env = clean_environment(encoding, mode, scratch)
        probe_command = [sys.executable, '-B', '-c', probe]
        p = subprocess.run(probe_command, cwd=ROOT, env=env, capture_output=True, timeout=30)
        if p.returncode:
            raise RuntimeError('A30_ENV_PROBE_FAILED')
        measured = json.loads(p.stdout.decode(encoding))
        measured.update(probe_command=probe_command, probe_exit_code=p.returncode,
                        requested_console=encoding, probe_decode_encoding=encoding, proof_json_encoding='utf-8')
        (folder / 'environment.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8')
        if not environment_valid(measured, encoding, int(mode), scratch):
            raise RuntimeError('A30_CLEAN_WINDOWS_ENV_REQUIRED')
        command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a30', '-p', 'test_*.py', '-v']
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=180)
        text = (p.stdout.decode(encoding) + p.stderr.decode(encoding)).replace('\r\n', '\n')
        log = folder / 'python-tests.log'; log.write_text(text, encoding='utf-8', newline='\n')
        rows.append({'console': encoding, 'command': command, 'exit_code': p.returncode,
                     **test_result(text, p.returncode, measured['suite_discovered']),
                     'TMPDIR_present': measured['TMPDIR_present'],
                     'environment_sha256': hashlib.sha256((folder / 'environment.json').read_bytes()).hexdigest(),
                     'log_encoding': 'utf-8', 'subprocess_decode_encoding': encoding,
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
                            ('windows-matrix.json', {'schema': 'a30-clean-windows-v1', 'rows': rows, 'exit_code': int(any(r['exit_code'] != 0 or r.get('all_pass') is False for r in rows))})]:
        (out / filename).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'rows': rows, 'native_executed': args.with_native, 'readiness_claimed': False}, indent=2))
    temporary.cleanup()
    return int(any(r['exit_code'] != 0 or r.get('all_pass') is False for r in rows))


if __name__ == '__main__':
    sys.exit(main())
