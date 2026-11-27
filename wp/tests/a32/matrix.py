"""A32 complete Windows matrix, two consoles, native classic/HPOS twice."""
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
SCRATCH = Path.home() / 'AppData/Local/hermes/cache/scratch'


def sources():
    spec = importlib.util.spec_from_file_location('a32_matrix_runner', HERE / 'run.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    return runner.sources()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    if sys.platform != 'win32':
        raise RuntimeError('A32_WINDOWS_REQUIRED')
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise RuntimeError('A32_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    baseline = sources()
    rows = []
    probe = "import os,sys,tempfile,locale,json; print(json.dumps({'python':sys.version,'platform':sys.platform,'executable':sys.executable,'encoding':sys.stdout.encoding,'utf8_mode':sys.flags.utf8_mode,'locale':locale.getencoding(),'tmpdir_present':'TMPDIR' in os.environ,'temp':tempfile.gettempdir()}))"
    for name, encoding, utf8 in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        folder = out / name
        folder.mkdir()
        temporary = out / (name + '-temp')
        temporary.mkdir()
        env = {**os.environ, 'TEMP': str(temporary), 'TMP': str(temporary),
               'PYTHONIOENCODING': encoding, 'PYTHONUTF8': utf8, 'PYTHONDONTWRITEBYTECODE': '1'}
        env.pop('TMPDIR', None)
        measured = subprocess.run([sys.executable, '-B', '-c', probe], cwd=ROOT, env=env,
                                  capture_output=True, timeout=30)
        if measured.returncode != 0:
            raise RuntimeError('A32_PROBE_FAILED')
        actual = json.loads(measured.stdout.decode(encoding))
        for kind, command, timeout in [
            ('python', [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a32', '-p', 'test_*.py', '-v'], 180),
            ('native', [sys.executable, '-B', 'wp/tests/a32/run.py', '--output=' + str(folder / 'native')], 4500),
        ]:
            p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=timeout)
            log = folder / (kind + '-console.log')
            text = (p.stdout + p.stderr).decode(encoding, errors='strict').replace('\r\n', '\n')
            log.write_text(text, encoding='utf-8', newline='\n')
            row = {'kind': kind, 'command': command, 'encoding': encoding, 'exit_code': p.returncode,
                   'tmpdir_present': actual['tmpdir_present'], 'temp_is_scratch': Path(actual['temp']).is_relative_to(SCRATCH),
                   'probe': actual, 'log': log.relative_to(out).as_posix(), 'sha256': hashlib.sha256(log.read_bytes()).hexdigest()}
            if kind == 'python':
                matches = re.findall(r'^Ran (\d+) tests? in ', text, re.M)
                row['tests_run'] = int(matches[0]) if len(matches) == 1 else 0
                row['all_pass'] = p.returncode == 0 and row['tests_run'] > 0 and 'OK' in text.splitlines()
            rows.append(row)
            print(json.dumps({'console': encoding, 'kind': kind, 'exit_code': p.returncode}), flush=True)
    stable = baseline == sources()
    result = {'scope': 'python_and_native', 'readiness_claimed': False, 'sources_stable': stable, 'rows': rows,
              'exit_code': int(not stable or any(r['exit_code'] != 0 or r.get('all_pass') is False for r in rows))}
    (out / 'sources.json').write_text(json.dumps(baseline, indent=2) + '\n', encoding='utf-8')
    (out / 'windows-matrix.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
