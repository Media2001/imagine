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

    def test_role_receipt_refuses_unrelated_green_placeholder(self):
        m = subject()
        validate = getattr(m, 'role_receipt_valid', m.receipt_valid)
        self.assertFalse(validate({'suite': 'A23-role-definitions-boundary-doubles', 'exit_code': 0,
                                   'checks': [{'check': 'unrelated', 'status': 'PASS'}]}))

    def test_role_receipt_named_cases_and_omissions(self):
        m = subject()
        cases = ['role_negative_override_excluded', 'role_multi_management_excluded',
                 'management_without_commerce_excluded', 'no_false_published_family', 'private_values_absent',
                 'authoritative_storage', 'false_capability_keeps_reader', 'unsafe_non_management_role_ignored']
        cases += ['unsafe_management_role_closed:' + str(i) for i in range(4)]
        cases += ['valid_role_boundary:' + str(i) for i in range(2)]
        rows = [{'check': storage + ':' + name, 'status': 'PASS'}
                for storage in ('classic', 'hpos') for name in cases]
        d = {'suite': 'A23-role-definitions-boundary-doubles', 'exit_code': 0, 'checks': rows}
        self.assertTrue(m.role_receipt_valid(d))
        for i in range(len(rows)):
            with self.subTest(omitted=rows[i]['check']):
                self.assertFalse(m.role_receipt_valid({**d, 'checks': rows[:i] + rows[i + 1:]}))
        self.assertFalse(m.role_receipt_valid({**d, 'suite': 'wrong-suite'}))
        self.assertFalse(m.role_receipt_valid({**d, 'tests': None}))
        self.assertFalse(m.role_receipt_valid({**d, 'checks': rows + [rows[0]]}))
        self.assertFalse(m.role_receipt_valid({**d, 'checks': rows + [{'check': 'extra', 'status': 'FAIL'}]}))

    def test_shared_lines_not_whole_readme(self):
        lines = b'own line one\nown line two\n'
        m = subject()
        self.assertTrue(m.shared_contract(b'previous lot\n' + lines + b'next lot\n', lines))
        self.assertFalse(m.shared_contract(lines + b'own line one\n', lines))
        self.assertFalse(m.shared_contract(b'own line one\n', lines))
        self.assertFalse(m.shared_contract(b'own line one\nown line two', lines))


if __name__ == '__main__':
    unittest.main()
