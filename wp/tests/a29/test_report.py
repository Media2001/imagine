"""Actual publication contracts, including valid final-process contamination."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a29_report', ROOT / 'wp/outils/bascule/a29/report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
CLOCK = '2026-11-26T12:00:00+00:00'


def fixture():
    return {'schema': 'imagine-a29-scheduled-tasks-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'failed_scope': 'action_scheduler_only',
            'window': 'eight_rolling_utc_weeks',
            'counts': {**{key: {'groups': [], 'autres': 0} for key in ('pending', 'overdue', 'failed', 'renewal_weeks')},
                       'other_tasks': 0, 'other_active_extensions': 0},
            'as_of_utc': CLOCK, 'audit_sha256': '0' * 64}


class ReportTests(unittest.TestCase):
    def test_nominal(self):
        self.assertTrue(hasattr(r, 'projection'), 'missing closed schema')
        self.assertTrue(r.projection(fixture(), '0' * 64, CLOCK))

    def test_k5_and_closed_family(self):
        for key in ('pending', 'overdue', 'failed'):
            for family in ('renouvellement', 'nouvelle_tentative', 'fin_abonnement', 'email',
                           'entretien_woocommerce', 'entretien_wordpress', 'autre', 'CANARY', 'wp_version_check'):
                for n in range(6):
                    d = fixture()
                    d['counts'][key]['groups'] = [{'family': family, 'count': n}]
                    self.assertEqual(r.projection(d, '0' * 64), family in r.FAMILIES and n == 5)

    def test_all_eight_relative_weeks_no_dates(self):
        for week in list(range(10)) + ['2026-12-01', True, None]:
            d = fixture()
            d['counts']['renewal_weeks']['groups'] = [{'week': week, 'count': 5}]
            self.assertEqual(r.projection(d, '0' * 64), type(week) is int and 1 <= week <= 8)

    def test_no_individual_or_extra_keys(self):
        for path in [(), ('counts',), ('counts', 'pending'), ('counts', 'renewal_weeks')]:
            d = fixture()
            o = d
            for key in path:
                o = o[key]
            o['CANARY'] = 'private name argument id date'
            self.assertFalse(r.projection(d, '0' * 64))

    def test_count_types_and_rare_scalars(self):
        for value in (-1, 2**53, True, 1.5, '5', None, [], {}):
            d = fixture()
            d['counts']['pending']['autres'] = value
            self.assertFalse(r.projection(d, '0' * 64))
        for key in ('other_tasks', 'other_active_extensions'):
            for n in (0, 1, 4, 5, 99, 'moins de cinq', 'attribution indéterminée'):
                d = fixture()
                d['counts'][key] = n
                expected = n in (0, 5, 99, 'moins de cinq') or key == 'other_active_extensions' and n == 'attribution indéterminée'
                self.assertEqual(r.projection(d, '0' * 64), expected)

    def test_all_neutralised_counts_unknown(self):
        d = fixture()
        d['neutralisation'] = r.UNKNOWN
        self.assertFalse(r.projection(d, '0' * 64))
        for key in r.COUNTS:
            d['counts'][key] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))
        for key in r.COUNTS:
            bad = copy.deepcopy(d)
            bad['counts'][key] = 0
            self.assertFalse(r.projection(bad, '0' * 64))

    def test_clock_exact_and_bound(self):
        for value in ('2026-02-30T12:00:00+00:00', CLOCK + 'CANARY', True, None,
                      '2026-11-26T12:00:00+01:00', '2026-11-26T12:00:00Z'):
            d = fixture()
            d['as_of_utc'] = value
            self.assertFalse(r.projection(d, '0' * 64))
        self.assertFalse(r.projection(fixture(), '0' * 64, '2026-11-27T12:00:00+00:00'))

    def test_duplicate_or_unsorted_cells(self):
        a = {'family': 'renouvellement', 'count': 5}
        b = {'family': 'autre', 'count': 5}
        for rows in ([a, a], [a, b]):
            d = fixture()
            d['counts']['pending']['groups'] = rows
            self.assertFalse(r.projection(d, '0' * 64))

    def test_duplicate_json_rejected(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.assertRaises(ValueError):
                r.read(raw)

    def make_report(self, base):
        audit = base / 'audit.json'
        audit.write_text(json.dumps({'generated_at_utc': CLOCK, 'sections': {'commerce': {'order_storage': 'classic'}}}), encoding='utf-8')
        data = fixture()
        data['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
        out = base / 'out'
        out.mkdir()
        self.publish(out, data)
        return out, audit, data

    def publish(self, out, data):
        raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
        (out / 'taches.json').write_bytes(raw)
        (out / 'taches.md').write_bytes(r.MARKDOWN.encode() + raw + b'```\n')

    def test_published_storage_bound_to_audit(self):
        with tempfile.TemporaryDirectory(prefix='a29-schema-', dir=os.environ.get('TMPDIR')) as tmp:
            out, audit, data = self.make_report(Path(tmp))
            self.assertTrue(r.complete_report(out, audit))
            data['storage'] = 'hpos'
            self.publish(out, data)
            self.assertFalse(r.complete_report(out, audit))

    def test_coherent_shutdown_counts_require_pre_shutdown_binding(self):
        with tempfile.TemporaryDirectory(prefix='a29-binding-', dir=os.environ.get('TMPDIR')) as tmp:
            out, audit, data = self.make_report(Path(tmp))
            digest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
            protocol = b'A29_OK taches.json taches.md\nA29_FINAL ' + json.dumps(digest).encode('ascii') + b'\n'
            self.assertTrue(r.final_binding(protocol, out))
            self.assertFalse(r.final_binding(b'A29_OK taches.json taches.md\n', out))
            self.assertFalse(r.final_binding(protocol + b'PRIVATE', out))
            data['counts']['pending']['autres'] = 7
            self.publish(out, data)
            self.assertTrue(r.complete_report(out, audit))
            self.assertFalse(r.final_binding(protocol, out))

    def test_canary_in_each_report_and_extra_file(self):
        for channel in ('taches.json', 'taches.md', 'extra.txt'):
            with self.subTest(channel=channel), tempfile.TemporaryDirectory(prefix='a29-files-', dir=os.environ.get('TMPDIR')) as tmp:
                out, audit, data = self.make_report(Path(tmp))
                self.assertTrue(r.complete_report(out, audit))
                with (out / channel).open('ab') as h:
                    h.write(b'CANARY')
                self.assertFalse(r.complete_report(out, audit))

    def test_missing_empty_and_noncanonical_files(self):
        for mode in ('missing', 'empty', 'noncanonical', 'directory'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='a29-file-', dir=os.environ.get('TMPDIR')) as tmp:
                out, audit, data = self.make_report(Path(tmp))
                if mode in ('missing', 'directory'):
                    (out / 'taches.md').unlink()
                    if mode == 'directory':
                        (out / 'taches.md').mkdir()
                elif mode == 'empty':
                    (out / 'taches.json').write_bytes(b'')
                else:
                    (out / 'taches.json').write_text(json.dumps(data), encoding='utf-8')
                self.assertFalse(r.complete_report(out, audit))


if __name__ == '__main__':
    unittest.main()
