"""T03 integration contracts: parsers / mocked boundaries, never native evidence."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


class IntegrationContracts(unittest.TestCase):
    def test_php_tests_remain_independent_of_package_results(self):
        worker = (HERE / 'executer.php').read_text(encoding='utf-8')
        self.assertIn("'/paquets.php'", worker)
        self.assertLess(worker.index("'/paquets.php'"), worker.index("echo 'T01_RESULT '"))
        self.assertNotIn('$packet', worker[worker.index('$pass = $pass &&'):])
        self.assertIn('exit($pass ? 0 : 1);', worker)

    def test_existing_wp_mount_and_all_isolation_flags_are_preserved(self):
        replay = (ROOT / 'wp/tests/rejouer.ps1').read_text(encoding='utf-8')
        for token in ('--network', "'none'", '--read-only', '--cap-drop', "'ALL'", '--security-opt',
                      'no-new-privileges', "'65534:65534'", '--pids-limit', '--memory', '--cpus',
                      '--no-healthcheck', '--log-driver', "'none'", "'never'", '/tmp:rw,nosuid,nodev,size=512m,mode=1777',
                      'target=/repo/wp,readonly', 'target=/packet-repo,readonly'):
            self.assertIn(token, replay)
        self.assertIn('Assert-T01Isolation $after $owner $image.Id $source $packetSource', replay)
        final = [line for line in replay.splitlines() if "Write-Output ('REJEU :" in line]
        self.assertEqual(len(final), 1)
        self.assertNotIn('packet', final[0].lower())

    def test_python_added_only_by_existing_image_preparation(self):
        dockerfile = (HERE / 'Dockerfile').read_text(encoding='utf-8')
        self.assertIn(' python3 ', dockerfile)
        preparer = (ROOT / 'wp/tests/preparer-image.ps1').read_text(encoding='utf-8')
        self.assertIn("'t01/Dockerfile'", preparer)
        self.assertNotIn('python', (ROOT / 'wp/tests/rejouer.ps1').read_text(encoding='utf-8').lower())

    @unittest.skipUnless(sys.platform == 'win32', 'Windows PowerShell mock boundary')
    def test_complete_script_mock_boundary_never_propagates_packet_red(self):
        outputs = {}
        for case in ('packet-pass', 'packet-fail', 'pass', 'unsafe-packet-mount'):
            child = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                    '-File', str(HERE / 'mock-wsl.ps1')],
                                   env={**os.environ, 'PYTHONIOENCODING': 'utf-8',
                                        'T01_TEST_CASE': case, 'T01_TEST_ROOT': str(ROOT)},
                                   capture_output=True, timeout=30)
            lines = child.stdout.decode('utf-8-sig').splitlines()
            outputs[case] = lines
            self.assertEqual(child.returncode, 1 if case == 'unsafe-packet-mount' else 0,
                             child.stdout.decode('utf-8', errors='replace'))
            self.assertEqual(sum(line.startswith('PAQUETS :') for line in lines), 1)
            self.assertTrue(any(line.startswith('T01 CLEANUP : absence verifiee') for line in lines))
        self.assertEqual(outputs['packet-pass'][-1], outputs['packet-fail'][-1])
        self.assertEqual(outputs['packet-pass'][-1], 'REJEU : 7 tests, 19 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS')
        self.assertIn('PAQUETS : 2 vérifiés, 1 échecs ; hors rejeu : aucun ; A-28 PACKAGE_DRIFT', outputs['packet-fail'])
        self.assertIn('T-03 RUNNER_OUTPUT', outputs['pass'][-3])
        self.assertTrue(outputs['unsafe-packet-mount'][-1].endswith('FAIL'))

    @unittest.skipUnless(sys.platform == 'win32', 'Windows PowerShell parser contract')
    def test_powershell_summary_parser_keeps_red_separate_and_closed(self):
        values = [
            {'verified': 2, 'lots': ['A-22', 'A-28'], 'failures': [], 'excluded': []},
            {'verified': 2, 'lots': ['A-22', 'A-28'], 'failures': [{'lot': 'A-28', 'control': 'PACKAGE_DRIFT'}], 'excluded': []},
            {'verified': 0, 'lots': [], 'failures': [], 'excluded': [{'lot': 'A-22', 'reason': 'journaux absents'}]},
            {'verified': 0, 'lots': [], 'failures': [{'lot': 'A-22', 'control': 'PRIVATE /secret'}], 'excluded': []},
            {'verified': 99, 'lots': [], 'failures': [], 'excluded': []},
        ]
        encoded = base64.b64encode(json.dumps(values).encode()).decode()
        script = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=New-Object Text.UTF8Encoding($false); . '" + str(HERE / 'paquets.ps1') + "'; "
        script += "$items=([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('" + encoded + "')) | ConvertFrom-Json); foreach($item in $items) { Get-T03PacketSummary ('T03_PACKETS ' + ($item | ConvertTo-Json -Compress -Depth 10)) }"
        command = base64.b64encode(script.encode('utf-16le')).decode()
        child = subprocess.run(['powershell.exe', '-NoProfile', '-EncodedCommand', command],
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, capture_output=True, timeout=30)
        self.assertEqual(child.returncode, 0, child.stderr.decode('utf-8', errors='replace'))
        lines = child.stdout.decode('utf-8-sig').splitlines()
        self.assertEqual(lines[0], 'PAQUETS : 2 vérifiés, 0 échecs ; hors rejeu : aucun')
        self.assertEqual(lines[1], 'PAQUETS : 2 vérifiés, 1 échecs ; hors rejeu : aucun ; A-28 PACKAGE_DRIFT')
        self.assertEqual(lines[2], 'PAQUETS : 0 vérifiés, 0 échecs ; hors rejeu : A-22 (journaux absents)')
        self.assertEqual(lines[3:], ['PAQUETS : 0 vérifiés, 1 échecs ; hors rejeu : aucun ; T-03 RUNNER_OUTPUT'] * 2)
        self.assertNotIn('PRIVATE', child.stdout.decode('utf-8-sig'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
