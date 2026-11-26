"""Verifier rejects partial, stale and fabricated-positive summaries."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a27_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifyTests(unittest.TestCase):
    def test_receipt_requires_real_nonempty_checks(self):
        for data in ({}, {'exit_code': 0}, {'exit_code': 0, 'tests': 42, 'checks': []},
                     {'exit_code': 1, 'checks': [{'check': 'x', 'status': 'PASS'}]},
                     {'exit_code': False, 'checks': [{'check': 'x', 'status': 'PASS'}]}):
            self.assertFalse(v.receipt_valid(data))

    def test_duplicate_or_failed_checks_rejected(self):
        row = {'check': 'x', 'status': 'PASS'}
        self.assertFalse(v.receipt_valid({'exit_code': 0, 'checks': [row, row]}))
        self.assertFalse(v.receipt_valid({'exit_code': 0, 'checks': [{'check': 'x', 'status': 'FAIL'}]}))
        self.assertTrue(v.receipt_valid({'exit_code': 0, 'checks': [row]}))

    def test_python_summary_requires_terminal_ok_and_one_total(self):
        self.assertEqual(v.log_summary('\nRan 22 tests in 0.5s\n\nOK\n'), (22, True))
        for text in ('OK\n', '\nRan 22 tests in 0.5s\n\nFAILED\n',
                     '\nRan 22 tests in 0.5s\n\nOK\nA27_PRIVATE_CANARY',
                     '\nRan 22 tests in 0.5s\nRan 4 tests in 0.2s\n\nOK\n'):
            self.assertFalse(v.log_summary(text)[1])

    def test_missing_packet_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix='a27-no-packet-', dir=os.environ.get('TMPDIR')) as tmp:
            q = subprocess.run([sys.executable, '-B', str(HERE / 'verify.py'), '--evidence=' + tmp],
                               capture_output=True, text=True, encoding='utf-8', timeout=20,
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(q.returncode, 1)
            self.assertEqual(json.loads(q.stdout), {'exit_code': 1, 'code': 'A27_PACKET_INVALID', 'readiness_claimed': False})
            self.assertEqual(q.stderr, '')

    def test_native_tools_require_explicit_parent_flag(self):
        for filename in ('run.py', 'style.py'):
            q = subprocess.run([sys.executable, '-B', str(HERE / filename), '--output=A27_PRIVATE_CANARY'],
                               capture_output=True, text=True, encoding='utf-8', timeout=20,
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(q.returncode, 2)
            self.assertIn('--parent-serialized', q.stderr)
            self.assertFalse((ROOT / 'A27_PRIVATE_CANARY').exists())

    def test_matrix_native_requires_parent_flag(self):
        q = subprocess.run([sys.executable, '-B', str(HERE / 'matrix.py'), '--include-native', '--output=A27_PRIVATE_CANARY'],
                           capture_output=True, text=True, encoding='utf-8', timeout=20,
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(q.returncode, 2)
        self.assertIn('--include-native requires --parent-serialized', q.stderr)
        self.assertFalse((ROOT / 'A27_PRIVATE_CANARY').exists())


if __name__ == '__main__':
    unittest.main()
