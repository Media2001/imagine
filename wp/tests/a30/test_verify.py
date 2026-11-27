"""A30 verifier must not turn Python-only or forged receipts into native evidence."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
VERIFY = ROOT / 'wp/tests/a30/verify.py'


class VerifierTests(unittest.TestCase):
    def test_missing_native_packet_is_never_green(self):
        self.assertTrue(VERIFY.is_file(), 'A30 no-argument package verifier missing')
        spec = importlib.util.spec_from_file_location('a30_verify', VERIFY)
        v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
        with tempfile.TemporaryDirectory(prefix='a30-verify-', dir=os.environ['TMPDIR']) as temp:
            result = v.verify(Path(temp))
            self.assertEqual(1, result['exit_code'])
            self.assertFalse(result['native_proven'])

    def test_production_reader_exists_and_refuses_arguments(self):
        import subprocess
        entry = ROOT / 'production/A-30/verify.py'
        self.assertTrue(entry.is_file(), 'A30 production no-argument reader missing')
        p = subprocess.run([sys.executable, '-B', str(entry), '--unexpected'],
                           cwd=ROOT, capture_output=True,
                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=20)
        self.assertEqual(1, p.returncode)
        self.assertEqual(b'', p.stderr)
        self.assertEqual('NO_ARGUMENTS', json.loads(p.stdout)['code'])

    def test_shared_readme_contract_is_only_two_exact_lines(self):
        self.assertTrue(VERIFY.is_file())
        spec = importlib.util.spec_from_file_location('a30_verify', VERIFY)
        v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
        self.assertTrue(hasattr(v, 'shared_contract'), 'A30 shared two-line contract missing')
        expected = b'one\ntwo\n'
        self.assertTrue(v.shared_contract(b'other lot\none\ntwo\nnew other lot\n', expected))
        self.assertFalse(v.shared_contract(b'one\ntwo\none\n', expected))
        self.assertFalse(v.shared_contract(b'one\ntwo\n', b'one\n'))

    def test_receipts_need_nonempty_unique_named_checks_and_zero_exit(self):
        self.assertTrue(VERIFY.is_file(), 'A30 no-argument package verifier missing')
        spec = importlib.util.spec_from_file_location('a30_verify', VERIFY)
        v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
        good = {'exit_code': 0, 'checks': [{'check': 'one', 'status': 'PASS'}]}
        self.assertTrue(v.receipt_valid(good))
        for bad in ({'exit_code': 0, 'checks': []}, {'exit_code': 0, 'checks': good['checks'] * 2},
                    {'exit_code': 1, 'checks': good['checks']}, {'exit_code': 0, 'checks': [{'check': 'one', 'status': 'FAIL'}]}):
            self.assertFalse(v.receipt_valid(bad))


if __name__ == '__main__':
    unittest.main(verbosity=2)
