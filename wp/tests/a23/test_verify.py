"""Verification helpers fail closed on empty, mixed or red receipts."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


def subject():
    path = ROOT / 'wp/tests/a23/verify.py'
    if not path.is_file():
        raise AssertionError('A23 verifier is missing')
    spec = importlib.util.spec_from_file_location('a23_verify', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class VerifyTests(unittest.TestCase):
    def test_green_receipt(self):
        self.assertTrue(subject().receipt_valid({'exit_code': 0, 'checks': [{'check': 'one', 'status': 'PASS'}]}))

    def test_red_receipt(self):
        self.assertFalse(subject().receipt_valid({'exit_code': 0, 'checks': [{'check': 'one', 'status': 'FAIL'}]}))

    def test_empty_receipt(self):
        self.assertFalse(subject().receipt_valid({'exit_code': 0, 'checks': []}))

    def test_mixed_families_even_null(self):
        for extra in (None, [], [{'ok': False}]):
            self.assertFalse(subject().receipt_valid({'exit_code': 0, 'checks': [{'check': 'one', 'status': 'PASS'}], 'tests': extra}))

    def test_duplicate_assertion_names(self):
        self.assertFalse(subject().receipt_valid({'exit_code': 0, 'checks': [{'check': 'one', 'status': 'PASS'}] * 2}))

    def test_windows_crlf_python_summary(self):
        path = ROOT / 'wp/tests/a23/matrix.py'
        spec = importlib.util.spec_from_file_location('a23_matrix', path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertTrue(hasattr(m, 'python_summary'), 'matrix must parse real Windows CRLF output')
        self.assertEqual(m.python_summary('Ran 23 tests in 0.4s\r\n\r\nOK\r\n', 0),
                         {'tests_run': 23, 'all_pass': True})
        self.assertFalse(m.python_summary('Ran 23 tests in 0.4s\r\nFAILED\r\n', 1)['all_pass'])

    def test_shared_lines_not_whole_readme(self):
        lines = b'own line one\nown line two\n'
        m = subject()
        self.assertTrue(m.shared_contract(b'previous lot\n' + lines + b'next lot\n', lines))
        self.assertFalse(m.shared_contract(lines + b'own line one\n', lines))
        self.assertFalse(m.shared_contract(b'own line one\n', lines))
        self.assertFalse(m.shared_contract(b'own line one\nown line two', lines))


if __name__ == '__main__':
    unittest.main()
