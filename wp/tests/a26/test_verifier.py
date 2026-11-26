"""Verifier contracts, including exact two-line ownership without a shared-file hash."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def verifier():
    spec = importlib.util.spec_from_file_location('a26_verifier_test', HERE / 'verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifierTests(unittest.TestCase):
    def test_empty_or_failed_native_checks_rejected(self):
        v = verifier()
        for receipt in ({}, {'exit_code': 0, 'checks': []}, {'exit_code': 1, 'checks': [{'status': 'PASS'}]},
                        {'exit_code': 0, 'checks': [{'status': 'FAIL'}]}):
            self.assertFalse(v.passed(receipt))
        self.assertTrue(v.passed({'exit_code': 0, 'checks': [{'check': 'real', 'status': 'PASS'}]}))

    def test_required_names_not_just_zero_exit(self):
        v = verifier()
        receipt = {'exit_code': 0, 'checks': [{'check': 'first', 'status': 'PASS'}]}
        self.assertTrue(v.named(receipt, ['first']))
        self.assertFalse(v.named(receipt, ['second']))
        receipt['checks'] *= 2
        self.assertFalse(v.named(receipt, ['first']))

    def test_exact_owned_lines_allow_other_lots_but_not_duplicate_mutated_missing(self):
        v = verifier()
        with tempfile.TemporaryDirectory(prefix='a26-shared-doc-', dir=os.environ.get('TMPDIR')) as tmp:
            v.ROOT = Path(tmp)
            expected = v.ROOT / 'production/A-26/readme-ajout.txt'
            shared = v.ROOT / 'wp/outils/bascule/README.md'
            expected.parent.mkdir(parents=True)
            shared.parent.mkdir(parents=True)
            expected.write_bytes(b'A26-FIRST\nA26-SECOND\n')
            for good in (b'A26-FIRST\nA26-SECOND\n', b'earlier\nA26-FIRST\nA26-SECOND\nlater\n'):
                shared.write_bytes(good)
                self.assertTrue(v.shared_document_valid())
            for bad in (b'A26-FIRST\n', b'A26-FIRST\nA26-SECOND\nA26-FIRST\n',
                        b'A26-FIRST\nA26-SECOND\r\n', b'A26-FIRST\nA26-SECOND-mutant\n'):
                shared.write_bytes(bad)
                self.assertFalse(v.shared_document_valid())

    def test_local_packet_cannot_satisfy_native_gate(self):
        # Real local evidence is consumed by the command, not manufactured here.
        source = (HERE / 'verify.py').read_text(encoding='utf-8')
        self.assertIn("matrix['native_executed'] is not (not python_only)", source)
        self.assertIn("len(rows) != (2 if python_only else 5)", source)


if __name__ == '__main__':
    unittest.main()
