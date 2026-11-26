"""Verifier boundary controls. Synthetic receipts below are tests, not evidence."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a29_verify_tests', ROOT / 'wp/tests/a29/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifyTests(unittest.TestCase):
    def test_closed_pass_receipt(self):
        self.assertTrue(v.receipt_valid({'exit_code': 0, 'checks': [{'check': 'synthetic_boundary', 'status': 'PASS'}]}))
        for data in ({'exit_code': False, 'checks': [{'check': 'x', 'status': 'PASS'}]},
                     {'exit_code': 0, 'checks': []}, {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'FAIL'}]},
                     {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'PASS'}] * 2},
                     {'exit_code': 0, 'checks': [{'check': '', 'status': 'PASS'}]}):
            self.assertFalse(v.receipt_valid(data))

    def test_mixed_receipt_family_refused_even_null(self):
        for other in (None, [], {'hidden': False}):
            self.assertFalse(v.receipt_valid({'exit_code': 0, 'checks': [{'check': 'x', 'status': 'PASS'}], 'tests': other}))

    def test_owned_lines_only_exact_once(self):
        expected = (ROOT / 'production/A-29/readme-ajout.txt').read_bytes()
        self.assertTrue(v.document_valid(expected, b'other lot before\n' + expected + b'other lot after\n'))
        for shared in (b'', expected + expected, expected.replace(b'\n', b'\r\n'), expected[:-1],
                       expected.splitlines(keepends=True)[0], expected.replace(b'A-29', b'A-28', 1)):
            self.assertFalse(v.document_valid(expected, shared))

    def test_unittest_summary_nonempty_and_final(self):
        self.assertEqual(v.log_summary('Ran 1 test in 0.1s\n\nOK\n'), (1, True))
        for text in ('OK\n', 'Ran 0 tests in 0.1s\n\nOK\n', 'Ran 1 test in 0.1s\n\nFAILED\n',
                     'Ran 1 test in 0.1s\n\nOK\nraw data', 'Ran 1 test in 1s\nRan 1 test in 2s\n\nOK\n'):
            self.assertFalse(v.log_summary(text)[1])

    def test_duplicate_or_nonfinite_receipts_refused(self):
        with tempfile.TemporaryDirectory(prefix='a29-receipt-', dir=os.environ.get('TMPDIR')) as tmp:
            path = Path(tmp) / 'synthetic.json'
            for raw in ('{"exit_code":0,"exit_code":1}', '{"x":NaN}', '{"x":Infinity}'):
                path.write_text(raw, encoding='utf-8')
                with self.assertRaises(ValueError):
                    v.read(path)

    def call(self, script, args):
        return subprocess.run([sys.executable, '-B', str(ROOT / 'wp/tests/a29' / script), *args], cwd=ROOT,
            capture_output=True, text=True, encoding='utf-8', errors='strict', timeout=30,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})

    def test_empty_packet_is_not_full_or_python_acceptance(self):
        with tempfile.TemporaryDirectory(prefix='a29-empty-packet-', dir=os.environ.get('TMPDIR')) as tmp:
            for flags in ([], ['--python-only']):
                p = self.call('verify.py', ['--evidence=' + tmp, *flags])
                self.assertEqual(p.returncode, 1)
                self.assertEqual(json.loads(p.stdout), {'exit_code': 1, 'code': 'A29_PACKET_INVALID', 'readiness_claimed': False})
                self.assertEqual(p.stderr, '')
                self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_native_entrypoints_require_parent_before_any_tool(self):
        with tempfile.TemporaryDirectory(prefix='a29-parent-gate-', dir=os.environ.get('TMPDIR')) as tmp:
            out = str(Path(tmp) / 'never-created')
            for script, args in [('run.py', ['--output=' + out]), ('style.py', ['--output=' + out]),
                                 ('gates.py', ['--output=' + out]),
                                 ('matrix.py', ['--include-native', '--output=' + out])]:
                p = self.call(script, args)
                self.assertEqual(p.returncode, 2)
                self.assertIn('--parent-serialized', p.stderr)
                self.assertFalse(Path(out).exists())

    def test_missing_expected_source_root_refuses(self):
        s = importlib.util.spec_from_file_location('a29_runner_contract', ROOT / 'wp/tests/a29/run.py')
        runner = importlib.util.module_from_spec(s)
        s.loader.exec_module(runner)
        with self.assertRaisesRegex(RuntimeError, '^A29_MISSING_SOURCE_ROOT$'):
            runner.manifest(['wp/outils/bascule/a29/missing-expected-source-root'])


if __name__ == '__main__':
    unittest.main()
