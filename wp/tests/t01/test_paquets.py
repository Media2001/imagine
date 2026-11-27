"""T03 local contract tests. Boundary doubles only: NOT a native replay."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t03_paquets', HERE / 'paquets.py')
paquets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(paquets)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t03-contract-', dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lot = self.root / 'production/A-22'
        self.lot.mkdir(parents=True)
        (self.lot / 'verify.py').write_text('# Never executed on host.\n', encoding='utf-8')
        self.execute = Mock(side_effect=AssertionError('Undeclared verifier was launched'))

    def declare(self, **changes):
        value = {'schema': 1, 'entrypoint': 'verify.py', 'requires': [],
                 'logs': ['production/A-22/preuves/final/native.stdout.log'],
                 'controls': ['exact_packet_inventory_and_hashes', 'PACKAGE_DRIFT']}
        value.update(changes)
        (self.lot / 'rejeu.json').write_text(json.dumps(value), encoding='utf-8')
        return value

    def test_missing_declared_log_is_outside_not_failed(self):
        self.declare()
        result = paquets.replay(self.root, execute=self.execute)
        self.assertEqual(result, {'verified': 0, 'lots': [], 'failures': [], 'excluded': [
            {'lot': 'A-22', 'reason': 'journaux absents'}]})
        self.execute.assert_not_called()

    def test_invalid_declaration_is_closed_and_never_executed(self):
        for changes in ({'schema': True}, {'extra': 'secret'}, {'entrypoint': '../run.py'},
                        {'requires': ['wsl']}, {'logs': ['../../secret.log']},
                        {'logs': ['production/A-23/private.log']},
                        {'controls': ['secret /path']}, {'controls': ['PACKAGE_DRIFT', 'PACKAGE_DRIFT']}):
            with self.subTest(changes=changes):
                self.declare(**changes)
                result = paquets.replay(self.root, execute=self.execute)
                self.assertEqual(result['failures'], [{'lot': 'A-22', 'control': 'DECLARATION_INVALID'}])
                self.execute.assert_not_called()

    def test_unsupported_requirements_are_outside_with_fixed_reason(self):
        for requirement, reason in [('docker', 'Docker requis'), ('network', 'reseau requis'),
                                    ('repository-write', 'ecriture depot requise'), ('arguments', 'argument requis')]:
            self.declare(requires=[requirement])
            result = paquets.replay(self.root, execute=self.execute)
            self.assertEqual(result['excluded'], [{'lot': 'A-22', 'reason': reason}])
            self.execute.assert_not_called()

    def ready(self):
        data = self.declare()
        log = self.root / data['logs'][0]
        log.parent.mkdir(parents=True)
        log.write_bytes(b'Local boundary fixture, not native evidence.\n')
        return data

    def test_declared_success_calls_no_argument_python_boundary(self):
        self.ready()
        process = Mock(returncode=0, stdout=b'{"exit_code":0,"checks":[{"check":"PACKAGE_DRIFT","status":"PASS"}]}', stderr=b'')
        result = paquets.replay(self.root, execute=Mock(return_value=process))
        self.assertEqual(result, {'verified': 1, 'lots': ['A-22'], 'failures': [], 'excluded': []})

    def test_named_red_is_closed_and_untrusted_output_is_suppressed(self):
        self.ready()
        for stdout, stderr, control in [
            (b'{"exit_code":1,"checks":[{"check":"PACKAGE_DRIFT","status":"FAIL"}]}', b'', 'PACKAGE_DRIFT'),
            (b'{"exit":1,"status":"FAIL","code":"PACKAGE_DRIFT"}', b'', 'PACKAGE_DRIFT'),
            (b'{"exit":1,"code":"PRIVATE_CANARY_PATH"}', b'', 'VERIFIER_OUTPUT'),
            (b'PRIVATE_CANARY_PATH\n{"exit":0}', b'', 'VERIFIER_OUTPUT'),
            (b'{"exit_code":0}', b'PRIVATE_CANARY_PATH', 'VERIFIER_OUTPUT'),
            (b'{"exit_code":0,"exit_code":1}', b'', 'VERIFIER_OUTPUT'),
            (b'{"exit_code":false}', b'', 'VERIFIER_OUTPUT'),
            (b'{"exit_code":0,"exit":1}', b'', 'VERIFIER_OUTPUT'),
            (b'{"exit_code":0,"checks":[{"check":"PACKAGE_DRIFT","status":"FAIL"}]}', b'', 'PACKAGE_DRIFT'),
        ]:
            with self.subTest(control=control, stdout=stdout):
                process = Mock(returncode=1, stdout=stdout, stderr=stderr)
                result = paquets.replay(self.root, execute=Mock(return_value=process))
                self.assertEqual(result['verified'], 1)
                self.assertEqual(result['failures'], [{'lot': 'A-22', 'control': control}])
                self.assertNotIn('PRIVATE', json.dumps(result))

    def test_forged_process_success_does_not_hide_red(self):
        self.ready()
        for payload in ({'exit_code': 1, 'code': 'PACKAGE_DRIFT'},
                        {'exit_code': 0, 'checks': [{'check': 'PACKAGE_DRIFT', 'status': 'FAIL'}]}):
            process = Mock(returncode=0, stdout=json.dumps(payload).encode(), stderr=b'')
            result = paquets.replay(self.root, execute=Mock(return_value=process))
            self.assertEqual(result['failures'], [{'lot': 'A-22', 'control': 'PACKAGE_DRIFT'}])

    def test_timeout_and_launch_errors_are_closed_and_next_lot_continues(self):
        import subprocess
        self.ready()
        other = self.root / 'production/A-28'
        other.mkdir()
        (other / 'verify.py').write_text('# Not executed\n', encoding='utf-8')
        (other / 'rejeu.json').write_text(json.dumps({'schema': 1, 'entrypoint': 'verify.py', 'requires': [],
            'logs': [], 'controls': ['PACKAGE_DRIFT']}), encoding='utf-8')
        good = Mock(returncode=0, stdout=b'{"exit":0,"status":"PASS"}', stderr=b'')
        for error, control in [(subprocess.TimeoutExpired('PRIVATE_CANARY_PATH', 1), 'VERIFIER_TIMEOUT'),
                               (OSError('PRIVATE_CANARY_PATH'), 'VERIFIER_START')]:
            result = paquets.replay(self.root, execute=Mock(side_effect=[error, good]))
            self.assertEqual(result['verified'], 2)
            self.assertEqual(result['failures'], [{'lot': 'A-22', 'control': control}])

    def test_process_command_is_fixed_and_writes_are_redirected_to_tmp(self):
        from unittest.mock import patch
        self.ready()
        process = Mock(returncode=0)
        with patch.object(paquets.subprocess, 'run', return_value=process) as run:
            paquets.execute_verifier(self.root, self.lot / 'verify.py')
        args, kwargs = run.call_args
        self.assertEqual(args[0], ['/usr/bin/python3', '-B', str(self.lot / 'verify.py')])
        self.assertEqual(kwargs['cwd'], self.root)
        self.assertEqual(kwargs['timeout'], 90)
        self.assertEqual(kwargs['env']['PYTHONDONTWRITEBYTECODE'], '1')
        self.assertEqual(kwargs['env']['HOME'], '/tmp')
        self.assertEqual(kwargs['env']['TMPDIR'], '/tmp')
        self.assertEqual(kwargs['env']['PYTHONIOENCODING'], 'utf-8')
        self.assertNotIn('shell', kwargs)

    def test_verified_lots_are_explicit_and_counted_exactly(self):
        self.ready()
        good = Mock(returncode=0, stdout=b'{"exit":0,"status":"PASS"}', stderr=b'')
        result = paquets.replay(self.root, execute=Mock(return_value=good))
        self.assertEqual(result['lots'], ['A-22'])
        self.assertEqual(result['verified'], len(result['lots']))

    def test_cli_refuses_windows_without_running_a_verifier(self):
        import subprocess
        environment = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
        process = subprocess.run([sys.executable, '-B', str(HERE / 'paquets.py')],
                                 capture_output=True, env=environment, timeout=15)
        self.assertEqual(process.returncode, 0)  # Packet status never becomes suite status.
        payload = json.loads(process.stdout.decode('utf-8').removeprefix('T03_PACKETS '))
        self.assertEqual(payload['failures'], [{'lot': 'T-03', 'control': 'RUNNER_CONTEXT'}])

    def test_undeclared_verifier_is_outside_without_execution(self):
        result = paquets.replay(self.root, execute=self.execute)
        self.assertEqual(result, {'verified': 0, 'lots': [], 'failures': [], 'excluded': [
            {'lot': 'A-22', 'reason': 'declaration absente'}]})
        self.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
