"""Closed evidence contracts, including future parent-owned PRET."""
import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a25_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class EvidenceTests(unittest.TestCase):
    def test_corrected_native_form_observations_are_required(self):
        self.assertTrue(callable(getattr(v, 'form_observation_valid', None)), 'missing corrected observation validator')
        forms = {'listed_extensions': [], 'other_tables': 1, 'coverage': 'heuristique bornée',
                 'clear_messages_after_import': True,
                 'clear_messages_after_import_label': 'avertissement éditorial permanent, non mesuré sur la copie inspectée'}
        data = {'forms': forms, 'counts': {'forms': {
            'groups': [{'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 0}}}
        self.assertTrue(v.form_observation_valid(data, 'pk-only'))
        for n in (0, 10, 15):
            bad = copy.deepcopy(data)
            bad['counts']['forms'] = {'groups': [], 'autres': n}
            self.assertFalse(v.form_observation_valid(bad, 'pk-only'))
        data['forms']['coverage'] = 'couverture indéterminée'
        data['counts']['forms'] = 'couverture indéterminée'
        self.assertTrue(v.form_observation_valid(data, 'ambiguous'))
        data['counts']['forms'] = {'groups': [], 'autres': 0}
        self.assertFalse(v.form_observation_valid(data, 'ambiguous'))

    def test_genuine_receipt(self):
        self.assertTrue(v.receipt_valid({'exit_code': 0, 'checks': [{'check': 'x', 'status': 'PASS'}]}))

    def test_empty_red_duplicate_and_mixed_fail_closed(self):
        values = [None, {}, {'exit_code': 0, 'checks': []},
                  {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'FAIL'}]},
                  {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'PASS'}] * 2},
                  {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'PASS'}], 'tests': None}]
        for value in values:
            self.assertFalse(v.receipt_valid(value))

    def test_shared_lines_only_not_entire_document(self):
        expected = b'A25 one\nA25 two\n'
        self.assertTrue(v.shared_contract(b'earlier\n' + expected + b'other lot\n', expected))
        for shared in (b'A25 one\n', expected + b'A25 one\n', expected.replace(b'one', b'changed'),
                       expected.replace(b'\n', b'\r\n'), expected[:-1]):
            self.assertFalse(v.shared_contract(shared, expected))

    def test_future_pret_excluded_and_owned_sources_included(self):
        original = v.ROOT
        with tempfile.TemporaryDirectory(prefix='a25-seal-contract-') as tmp:
            v.ROOT = Path(tmp)
            try:
                p = v.ROOT / 'production/A-25'
                p.mkdir(parents=True)
                (p / 'report.md').write_bytes(b'owned\n')
                before = v.inventory(['production/A-25'])
                # Synthetic path only: no readiness marker is created in the real repository.
                (p / 'PRET').write_bytes(b'future parent marker\n')
                self.assertEqual(before, v.inventory(['production/A-25']))
                (p / 'report.md').write_bytes(b'changed\n')
                self.assertNotEqual(before, v.inventory(['production/A-25']))
            finally:
                v.ROOT = original


if __name__ == '__main__':
    unittest.main()
