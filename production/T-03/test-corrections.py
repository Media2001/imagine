"""Real T03 regressions: Windows launcher, real PHPUnit/PHP/Python in Docker.

No production test switches: only the disposable copy's two literal deadline
constants may be shortened, using the enumerated contract below. No fake clock,
assertion rewriting, isolation change, outer timeout change or native receipt.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_EDITS = {
    '$t01Deadline = hrtime(true) / 1e9 + 600.0;':
        '$t01Deadline = hrtime(true) / 1e9 + 7.0;',
    '$t01PacketMargin = 5.0;': '$t01PacketMargin = 1.0;',
}

# Finite 2 MiB per tested channel, never an OOM stress. A real child spawns a
# real grandchild in the verifier's process group, recording both actual PIDs.
DESCENDANTS = '''import os, pathlib, subprocess, sys, time
p = pathlib.Path('/tmp/t03-pids')
p.write_text(str(os.getpid()) + '\\n')
child = subprocess.Popen([sys.executable, '-c', "import os,pathlib,time; p=pathlib.Path('/tmp/t03-pids'); f=p.open('a'); f.write(str(os.getpid())+'\\\\n'); f.close(); time.sleep(20)"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
while len(p.read_text().splitlines()) < 2: time.sleep(.005)
pathlib.Path('/tmp/t03-ready').touch()
time.sleep(20)
'''
OBSERVER = '''import json, os, pathlib, signal, time
p = pathlib.Path('/tmp/t03-pids')
pids = [int(x) for x in p.read_text().splitlines()] if p.exists() else []
def live(pid):
    try: return pathlib.Path('/proc/' + str(pid) + '/stat').read_text().split(') ')[1][0] != 'Z'
    except FileNotFoundError: return False
for _ in range(100):
    if not any(live(pid) for pid in pids): break
    time.sleep(.01)
ok = len(pids) == 2 and not any(live(pid) for pid in pids)
# RED also cleans its owned descendants; do not leave even rejected runners.
for pid in pids:
    if live(pid): os.kill(pid, signal.SIGKILL)
print(json.dumps({'exit': int(not ok), 'checks': [{'check':'DESCENDANTS_STOPPED','status':'PASS' if ok else 'FAIL'}]}))
'''


def verifier(case):
    prefix = "import pathlib, subprocess, sys, time\n"
    prefix += "subprocess.Popen([sys.executable, '-c', " + repr(DESCENDANTS) + "], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
    prefix += "while not pathlib.Path('/tmp/t03-ready').exists(): time.sleep(.005)\n"
    if case == 'shared-deadline':
        return prefix + "time.sleep(10)\nprint('{\"exit\":0}')\n"
    fd = 1 if case == 'stdout-cap' else 2
    return prefix + "import os\nfor _ in range(512): os.write(" + str(fd) + ", b'PRIVATE_CANARY_PATH:' + b'x' * (4096 - 20))\ntime.sleep(.2)\n"


def fixture(base, case):
    (base / 'wp/tests').mkdir(parents=True)
    shutil.copy2(ROOT / 'wp/tests/rejouer.ps1', base / 'wp/tests/rejouer.ps1')
    shutil.copytree(ROOT / 'wp/tests/t01', base / 'wp/tests/t01',
                    ignore=shutil.ignore_patterns('__pycache__'))
    worker = base / 'wp/tests/t01/executer.php'
    text = worker.read_text(encoding='utf-8')
    edits = []
    if case == 'shared-deadline':
        for before, after in FIXTURE_EDITS.items():
            count = text.count(before)
            if count not in (0, 1):
                raise AssertionError('AMBIGUOUS_FIXTURE_CONTRACT')
            if count:
                text = text.replace(before, after)
                edits.append({'before': before, 'after': after})
        worker.write_text(text, encoding='utf-8', newline='\n')
    # A genuine prepared dependency cache, original composer manifests, and a
    # deliberately tiny real PHPUnit suite, not a synthesized JUnit response.
    lib = base / 'wp/plugins/imagine-site'
    lib.mkdir(parents=True)
    for name in ('composer.json', 'composer.lock'):
        shutil.copy2(ROOT / 'wp/plugins/imagine-site' / name, lib / name)
    (lib / 'phpunit.xml').write_text('<phpunit bootstrap="vendor/autoload.php"><testsuites><testsuite name="T03 real regression"><directory>tests</directory></testsuite></testsuites></phpunit>', encoding='utf-8')
    (lib / 'tests').mkdir()
    sleep = 'usleep(2000000);' if case == 'shared-deadline' else ''
    (lib / 'tests/PacketIsolationTest.php').write_text('<?php\ndeclare(strict_types=1);\nfinal class PacketIsolationTest extends \\PHPUnit\\Framework\\TestCase { public function testRealSuite(): void { ' + sleep + ' self::assertTrue(true); } }\n', encoding='utf-8')
    unit = base / 'wp/tests/t03-regression'
    unit.mkdir()
    (base / 'wp/outils/bascule').mkdir(parents=True)
    sleep = 'usleep(2500000);' if case == 'shared-deadline' else ''
    (unit / 'unit.php').write_text('<?php\ndeclare(strict_types=1);\n' + sleep + "file_put_contents('/report/unit.json', json_encode(['checks' => [['check' => 'real_fixture_unit', 'status' => 'PASS']], 'exit_code' => 0], JSON_THROW_ON_ERROR));\n", encoding='utf-8')
    for lot, source, controls in [('A-01', verifier(case), ['FIXTURE_GREEN']),
                                  ('A-02', OBSERVER, ['DESCENDANTS_STOPPED'])]:
        path = base / 'production' / lot
        path.mkdir(parents=True)
        (path / 'verify.py').write_text(source, encoding='utf-8', newline='\n')
        (path / 'rejeu.json').write_text(json.dumps({'schema': 1, 'entrypoint':'verify.py', 'requires': [], 'logs': [], 'controls': controls}), encoding='utf-8')
    assert (base / 'wp/tests/rejouer.ps1').read_bytes() == (ROOT / 'wp/tests/rejouer.ps1').read_bytes()
    return edits


def run(output, cases):
    if os.name != 'nt':
        raise SystemExit('Windows launcher required; PHP/Python verifiers run only in Docker.')
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='t03-real-', dir=Path(os.environ['LOCALAPPDATA']) / 'hermes/cache/scratch') as temporary:
            base = Path(temporary)
            edits = fixture(base, case)
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(base / 'wp/tests/rejouer.ps1')]
            started = time.monotonic()
            child = subprocess.run(command, capture_output=True, timeout=90,
                                   env={**os.environ, 'PYTHONIOENCODING':'utf-8', 'PYTHONUTF8':'1'})
            elapsed = time.monotonic() - started
            (output / (case + '.log')).write_bytes(child.stdout)
            (output / (case + '.stderr.log')).write_bytes(child.stderr)
            lines = child.stdout.decode('utf-8-sig').splitlines()
            markers = [line for line in lines if line.startswith('T01_RESULT ')]
            packet = json.loads(markers[0][11:]) if len(markers) == 1 else {}
            packets = packet.get('packets', {})
            expected = [{'lot':'T-03','control':'RUNNER_TIMEOUT'}] if case == 'shared-deadline' else [{'lot':'A-01','control':'VERIFIER_OUTPUT'}]
            checks = {
                'real_launcher_exit_zero': child.returncode == 0,
                'exactly_one_marker': len(markers) == 1,
                'real_PHPUnit_tests_only': packet.get('tests') == 1 and packet.get('assertions') == 1 and packet.get('pass') is True,
                'tools_real_receipt': packet.get('tools', {}).get('checks') == 1 and packet.get('tools', {}).get('failures') == 0,
                'closed_packet_red_only': packets.get('failures') == expected,
                'REJEU_PASS': bool(lines and lines[-1] == 'REJEU : 1 tests, 1 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS'),
                'public_streams_closed': 'PRIVATE_CANARY_PATH' not in child.stdout.decode('utf-8-sig'),
                'one_packet_summary': sum(line.startswith('PAQUETS :') for line in lines) == 1,
                'runner_absence_read_back': sum(bool(re.fullmatch(r'T01 CLEANUP : absence verifiee de imagine-t01-[a-f0-9]{32}', line)) for line in lines) == 1,
            }
            if case != 'shared-deadline':
                checks['descendant_observer_executed'] = packets.get('lots') == ['A-01', 'A-02']
            else:
                checks['real_remaining_budget_bounded'] = elapsed < 13 and len(edits) == 2
            results.append({'case':case, 'command': command, 'elapsed_seconds':elapsed,
                            'exit_code':child.returncode, 'fixture_edits': edits, 'checks': checks,
                            'packet_marker': packet, 'status': 'PASS' if all(checks.values()) else 'FAIL'})
        results[-1]['fixture_absent'] = not base.exists()
        (output / 'result.json').write_text(json.dumps({'status':'PASS' if all(r['status']=='PASS' and r['fixture_absent'] for r in results) else 'FAIL', 'cases':results}, indent=2) + '\n', encoding='utf-8')
        print(case, results[-1]['status'], round(elapsed, 3), flush=True)
    return 0 if all(r['status']=='PASS' for r in results) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=['shared-deadline', 'stdout-cap', 'stderr-cap'], action='append')
    args = parser.parse_args()
    raise SystemExit(run(args.output, args.case or ['shared-deadline', 'stdout-cap', 'stderr-cap']))
