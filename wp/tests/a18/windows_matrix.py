"""Run the full owned A18 suite under real Windows UTF-8 and cp1252 consoles."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROBE = (
    "import json,locale,sys; print(json.dumps({"
    "'platform':sys.platform,'executable':sys.executable,'version':sys.version,"
    "'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,"
    "'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),"
    "'utf8_mode':sys.flags.utf8_mode}))"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert sys.platform == 'win32' and not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    probes = []
    for console, encoding, mode, folder in [
        ('cp1252', 'cp1252', '0', out / 'cp1252-run'),
        ('utf8', 'utf-8', '1', out / 'utf8'),
    ]:
        env = {**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': mode,
               'PYTHONDONTWRITEBYTECODE': '1'}
        def run(command, log, timeout):
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                     text=True, encoding=encoding, errors='strict', timeout=timeout)
            (out / log).write_text(process.stdout + process.stderr, encoding='utf-8')
            return process
        probe_command = [sys.executable, '-B', '-c', PROBE]
        probe = run(probe_command, console + '-probe.log', 30)
        measured = json.loads(probe.stdout)
        assert probe.returncode == 0 and measured['stdout'] == encoding
        assert measured['stderr'] == encoding and measured['utf8_mode'] == int(mode)
        (out / (console + '-environment.json')).write_text(
            json.dumps(measured, indent=2) + '\n', encoding='utf-8')
        probes.append({'console': console, 'command': probe_command, 'exit_code': probe.returncode})
        for label, command, timeout in [
            ('launcher', [sys.executable, '-B', str(HERE / 'test_launcher.py')], 120),
            ('native', [sys.executable, '-B', str(HERE / 'run.py'), '--output=' + str(folder)], 1800),
        ]:
            process = run(command, console + '-' + ('launcher-tests' if label == 'launcher' else 'runner') + '.log', timeout)
            rows.append({'console': console, 'suite': label, 'command': command,
                         'environment': {k: env[k] for k in ['PYTHONIOENCODING', 'PYTHONUTF8', 'PYTHONDONTWRITEBYTECODE']},
                         'subprocess_decoder': encoding, 'exit_code': process.returncode})
    # Keep the established packet layout: cp1252 at its root, UTF-8 in utf8/.
    cp = out / 'cp1252-run'
    for path in cp.iterdir():
        path.rename(out / path.name)
    cp.rmdir()
    result = {'exit_code': int(any(row['exit_code'] for row in rows)), 'probes': probes, 'rows': rows}
    (out / 'windows-matrix.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
