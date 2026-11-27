"""Replay T03 corrections into a NEW external evidence directory; never seal/PRET.

The real native scripts are sequential: T01's orphan sweep is not concurrent-safe.
No image build, native business-matrix replay, Git, site or other-lane operation.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OWN_TOOLS = [
    'wp/tests/t01/executer.php', 'wp/tests/t01/paquets.php', 'wp/tests/t01/paquets.py',
    'wp/tests/t01/test_paquets.py', 'wp/tests/t01/test_t03_integration.py',
    'wp/tests/t01/test_t03_streams_native.py', 'wp/tests/t01/corrections-php.php',
    'wp/tests/t01/tools-contract.php', 'wp/tests/t01/paquets.ps1',
    'wp/tests/rejouer.ps1',
    'wp/tests/t01/commun.ps1', 'wp/tests/t01/Dockerfile',
]


def source_hashes():
    names = list(OWN_TOOLS) + [p.relative_to(ROOT).as_posix()
        for p in (ROOT / 'production/T-03').iterdir()
        if p.is_file() and p.name not in ('PRET', 'manifest.json')]
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def console_environment(context, inherited=None):
    environment = dict(os.environ if inherited is None else inherited)
    environment.pop('TMPDIR', None)
    environment.update(PYTHONIOENCODING='utf-8' if context == 'utf8' else 'cp1252',
                       PYTHONUTF8='1' if context == 'utf8' else '0',
                       PYTHONDONTWRITEBYTECODE='1')
    return environment


def run(output, nominal=False):
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('NEW_EXTERNAL_OUTPUT_REQUIRED')
    output.mkdir(parents=True, exist_ok=False)
    before = source_hashes()
    commands = []
    for context in ('utf8', 'cp1252'):
        environment = console_environment(context)
        probe = "import json,locale,os,sys;print(json.dumps({'executable':sys.executable,'version':sys.version,'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode,'tmpdir_present':'TMPDIR' in os.environ}))"
        commands.append((context + '-python-context', [sys.executable, '-c', probe], environment, 30))
        for name in ('test_paquets', 'test_t03_integration'):
            commands.append((context + '-' + name,
                             [sys.executable, '-B', str(ROOT / 'wp/tests/t01' / (name + '.py'))], environment, 120))
        commands.append((context + '-real-corrections',
                         [sys.executable, '-B', str(ROOT / 'production/T-03/test-corrections.py'),
                          '--output', str(output / (context + '-real-fixtures'))], environment, 180))
    environment = console_environment('utf8')
    for name, path in [('streams-native', 'production/T-03/test-streams-native.ps1'),
                       ('php-corrections', 'wp/tests/t01/test-php-corrections.ps1'),
                       ('tools-contract', 'wp/tests/t01/test-tools.ps1'),
                       ('rejeu-mock', 'wp/tests/t01/test-rejeu.ps1'),
                       ('tools-summary-mock', 'wp/tests/t01/test-tools-summary.ps1')]:
        commands.append((name, ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', path], environment, 120))
    if nominal:
        commands.append(('nominal-observed', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], environment, 720))
    receipts = []
    for name, command, environment, timeout in commands:
        started = time.monotonic()
        process = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, timeout=timeout)
        (output / (name + '.log')).write_bytes(process.stdout)
        (output / (name + '.stderr.log')).write_bytes(process.stderr)
        receipt = {'name': name, 'command': command, 'exit_code':process.returncode,
                   'elapsed_seconds':time.monotonic() - started,
                   'stdout_sha256':hashlib.sha256(process.stdout).hexdigest(),
                   'stderr_sha256':hashlib.sha256(process.stderr).hexdigest()}
        if name == 'nominal-observed':
            text = process.stdout.decode('utf-8-sig')
            receipt['summaries'] = [line for line in text.splitlines() if line.startswith(('PAQUETS :', 'OUTILS :', 'REJEU :', 'T01 CLEANUP :'))]
            markers = [line for line in text.splitlines() if line.startswith('T01_RESULT ')]
            receipt['marker'] = json.loads(markers[0][11:]) if len(markers) == 1 else None
        receipts.append(receipt)
        print(name, 'exit=' + str(process.returncode), flush=True)
        result = {'at':datetime.now().astimezone().isoformat(),
                  'status': ('PASS' if all(row['exit_code']==0 for row in receipts) and before == source_hashes() else 'FAIL') if len(receipts) == len(commands) else 'IN_PROGRESS',
                  'expected_command_count':len(commands), 'completed_command_count':len(receipts),
                  'qualification': 'CORRECTION_TESTS_ONLY_NOT_PARENT_FINAL',
                  'source_unchanged': before == source_hashes(), 'source_sha256': before,
                  'python': {'executable':sys.executable, 'version':sys.version},
                  'readiness_claimed':False, 'parent_final_gates_pending':True, 'commands':receipts}
        (output / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    return 0 if result['status']=='PASS' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--nominal', action='store_true', help='Capture current real OUTILS/REJEU, not a final parent gate')
    args = parser.parse_args()
    raise SystemExit(run(args.output, args.nominal))
