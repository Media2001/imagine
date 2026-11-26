"""Exercise publication as data, never load WordPress on Windows."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a25_report', ROOT / 'wp/outils/bascule/a25/report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    pool = lambda n: {'groups': [], 'autres': n}
    return {'schema': 'imagine-a25-visitor-retention-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'counts': {'comments': {key: pool(n) for key, n in [('all', 3), ('email', 2), ('ip', 2), ('account', 1)]},
            'forms': pool(4), 'guests': pool(2)}, 'forms': {'listed_extensions': ['Fluent Forms'], 'other_tables': 1,
            'clear_messages_after_import': True, 'coverage': 'heuristique bornée',
            'clear_messages_after_import_label': 'avertissement éditorial permanent, non mesuré sur la copie inspectée'},
            'audit_sha256': '0' * 64}


class ProjectionTests(unittest.TestCase):
    def test_editorial_warning_label_is_mandatory_and_literal(self):
        d = fixture()
        d['forms']['coverage'] = 'heuristique bornée'
        d['forms']['clear_messages_after_import_label'] = 'avertissement éditorial permanent, non mesuré sur la copie inspectée'
        self.assertTrue(r.projection(d, '0' * 64))
        for value in (None, '', 'A25_PRIVATE_CANARY', True):
            d['forms']['clear_messages_after_import_label'] = value
            self.assertFalse(r.projection(d, '0' * 64))

    def test_ambiguous_coverage_forbids_a_numeric_total(self):
        d = fixture()
        d['forms']['coverage'] = 'couverture indéterminée'
        d['forms']['clear_messages_after_import_label'] = 'avertissement éditorial permanent, non mesuré sur la copie inspectée'
        d['counts']['forms'] = 'couverture indéterminée'
        self.assertTrue(r.projection(d, '0' * 64))
        for value in ({'groups': [], 'autres': 0}, {'groups': [], 'autres': 9}, 'A25_PRIVATE_CANARY'):
            d['counts']['forms'] = value
            self.assertFalse(r.projection(d, '0' * 64))

    def test_coverage_and_editorial_fields_cannot_be_omitted(self):
        for key in ('coverage', 'clear_messages_after_import_label'):
            d = fixture()
            del d['forms'][key]
            self.assertFalse(r.projection(d, '0' * 64))

    def test_coverage_is_a_closed_value(self):
        for value in (None, True, 0, [], {}, '', 'A25_PRIVATE_CANARY'):
            d = fixture()
            d['forms']['coverage'] = value
            self.assertFalse(r.projection(d, '0' * 64))

    def test_ambiguous_total_cannot_claim_bounded_coverage(self):
        d = fixture()
        d['counts']['forms'] = 'couverture indéterminée'
        self.assertFalse(r.projection(d, '0' * 64))

    def test_neutralisation_has_priority_over_ambiguous_total(self):
        d = fixture()
        d['neutralisation'] = r.UNKNOWN
        d['forms']['coverage'] = 'couverture indéterminée'
        for key in ('email', 'ip'):
            d['counts']['comments'][key] = r.UNKNOWN
        d['counts']['forms'] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))
        d['counts']['forms'] = 'couverture indéterminée'
        self.assertFalse(r.projection(d, '0' * 64))

    def test_nominal(self):
        self.assertTrue(r.projection(fixture(), '0' * 64))

    def test_reject_free_strings_every_boundary(self):
        for path in [('schema',), ('storage',), ('neutralisation',), ('counts', 'forms'),
                     ('forms', 'listed_extensions'), ('forms', 'clear_messages_after_import')]:
            d = fixture()
            o = d
            for k in path[:-1]:
                o = o[k]
            o[path[-1]] = 'A25_PRIVATE_CANARY'
            self.assertFalse(r.projection(d, '0' * 64), path)

    def test_reject_extra_keys_recursively(self):
        for path in [(), ('counts',), ('counts', 'comments'), ('counts', 'forms'), ('forms',)]:
            d = fixture()
            o = d
            for k in path:
                o = o[k]
            o['A25_PRIVATE_CANARY'] = 'A25_PRIVATE_CANARY'
            self.assertFalse(r.projection(d, '0' * 64), path)

    def test_reject_small_visible_cell(self):
        d = fixture()
        for n in range(5):
            d['counts']['guests'] = {'groups': [{'year': 2023, 'state': 'guest', 'count': n}], 'autres': 0}
            self.assertFalse(r.projection(d, '0' * 64))

    def test_five_visible_cell(self):
        d = fixture()
        d['counts']['guests'] = {'groups': [{'year': 2023, 'state': 'guest', 'count': 5}], 'autres': 0}
        self.assertTrue(r.projection(d, '0' * 64))

    def test_unsafe_years_and_types(self):
        for year in (-1, 999, 10000, True, '2023', 'A25_PRIVATE_CANARY'):
            d = fixture()
            d['counts']['guests'] = {'groups': [{'year': year, 'state': 'guest', 'count': 5}], 'autres': 0}
            self.assertFalse(r.projection(d, '0' * 64))

    def test_unknown_date_closed_zero(self):
        d = fixture()
        d['counts']['guests'] = {'groups': [{'year': 0, 'state': 'guest', 'count': 5}], 'autres': 0}
        self.assertTrue(r.projection(d, '0' * 64))

    def test_reject_private_state_and_duplicate_cell(self):
        for state in ('A25_PRIVATE_CANARY', 'wc-completed'):
            d = fixture()
            d['counts']['guests'] = {'groups': [{'year': 2023, 'state': state, 'count': 5}], 'autres': 0}
            self.assertFalse(r.projection(d, '0' * 64))
        row = {'year': 2023, 'state': 'guest', 'count': 5}
        d['counts']['guests'] = {'groups': [row, row], 'autres': 0}
        self.assertFalse(r.projection(d, '0' * 64))

    def test_invalid_counts(self):
        for value in (-1, 1.5, True, 2**53, '7'):
            d = fixture()
            d['counts']['forms']['autres'] = value
            self.assertFalse(r.projection(d, '0' * 64))

    def test_neutralisation_never_fabricates_zero(self):
        d = fixture()
        d['neutralisation'] = r.UNKNOWN
        self.assertFalse(r.projection(d, '0' * 64))
        d['counts']['forms'] = r.UNKNOWN
        d['counts']['comments']['email'] = r.UNKNOWN
        d['counts']['comments']['ip'] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))

    def test_absent_adapter_explicit(self):
        d = fixture()
        d['forms']['listed_extensions'] = []
        self.assertTrue(r.projection(d, '0' * 64))

    def test_report_strict_bytes_and_set(self):
        with tempfile.TemporaryDirectory(prefix='a25-projection-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            audit = base / 'audit.json'
            audit.write_bytes(b'{}\n')
            d = fixture()
            d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
            out = base / 'report'
            out.mkdir()
            raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'visiteurs.json').write_bytes(raw)
            (out / 'visiteurs.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            self.assertTrue(r.complete_report(out, audit))
            (out / 'extra.txt').write_text('A25_PRIVATE_CANARY', encoding='utf-8')
            self.assertFalse(r.complete_report(out, audit))
            (out / 'extra.txt').unlink()
            (out / 'visiteurs.md').write_bytes(raw)
            self.assertFalse(r.complete_report(out, audit))


if __name__ == '__main__':
    unittest.main()
