"""A31 closed numbers-only publication; no PHP substitution."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a31_report', ROOT / 'wp/outils/bascule/a31/report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    return {'schema': 'imagine-a31-history-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'audit_sha256': '0' * 64,
            'counts': {**{k: {'groups': [], 'autres': 0} for k in
                         ('years', 'statuses', 'natures')},
                       **dict.fromkeys(r.LINKS, 0),
                       'refunds': {'total': 0, 'groups': [], 'autres': 0},
                       'oldest_year': None}}


class ReportTests(unittest.TestCase):
    def test_nominal(self):
        self.assertTrue(hasattr(r, 'projection'), 'A31 projection validator missing')
        self.assertTrue(r.projection(fixture(), '0' * 64))

    def test_threshold_all_dimensions(self):
        fields = {'years': {'year': 2020}, 'statuses': {'year': 2020, 'status': 'completed'},
                  'natures': {'nature': 'renewal'}, 'refunds': {'year': 2020}}
        for key, fields in fields.items():
            for n in range(7):
                d = fixture()
                d['counts'][key]['groups'] = [{**fields, 'count': n}]
                if key == 'refunds':
                    d['counts'][key]['total'] = n
                if key == 'years':
                    d['counts']['oldest_year'] = 2020
                self.assertEqual(r.projection(d, '0' * 64), n >= 5, (key, n))

    def test_five_natures_plus_illisible(self):
        for nature in ('parent', 'renewal', 'switch', 'resubscribe', 'none', 'illisible', 'CANARY', '', None):
            d = fixture()
            d['counts']['natures']['groups'] = [{'nature': nature, 'count': 5}]
            self.assertEqual(r.projection(d, '0' * 64), nature in r.NATURES)

    def test_closed_status_even_technical(self):
        for status in ('pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed',
                       'checkout-draft', 'autre', 'wc-completed', 'private_canary', 'CANARY'):
            d = fixture()
            d['counts']['statuses']['groups'] = [{'year': 2020, 'status': status, 'count': 5}]
            self.assertEqual(r.projection(d, '0' * 64), status in r.STATUSES)

    def test_no_amount_id_fine_date_or_open_key(self):
        for key, value in [('amount', '12.34'), ('order_id', 123), ('date', '2020-01-01'), ('CANARY', 'CANARY')]:
            for path in ((), ('counts',), ('counts', 'years')):
                d = fixture()
                target = d
                for part in path:
                    target = target[part]
                target[key] = value
                self.assertFalse(r.projection(d, '0' * 64))
        for year in (True, 0, 999, 10000, '2020', '2020-01-01', 'CANARY'):
            d = fixture()
            d['counts']['years']['groups'] = [{'year': year, 'count': 5}]
            self.assertFalse(r.projection(d, '0' * 64))

    def test_exact_neutral_unknown_not_false_zero(self):
        d = fixture()
        d['neutralisation'] = r.UNKNOWN
        self.assertFalse(r.projection(d, '0' * 64))
        for key in r.UNREADABLE_AFTER_IMPORT:
            d['counts'][key] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))
        for key in r.READABLE_AFTER_IMPORT:
            bad = copy.deepcopy(d)
            bad['counts'][key] = r.UNKNOWN
            self.assertFalse(r.projection(bad, '0' * 64))

    def test_neutral_native_renewal_ids_remain_readable(self):
        d = fixture()
        d['neutralisation'] = 'inconnu après neutralisation'
        d['counts']['natures'] = 'inconnu après neutralisation'
        self.assertTrue(r.projection(d, '0' * 64), 'import preserves standard numeric renewal links; do not hide them')

    def test_numeric_strict_and_sorted_unique(self):
        for value in (-1, 2**53, True, 1.5, '5', None):
            d = fixture()
            d['counts']['years']['autres'] = value
            self.assertFalse(r.projection(d, '0' * 64))
        for years in ([2021, 2020], [2020, 2020]):
            d = fixture()
            d['counts']['years']['groups'] = [{'year': y, 'count': 5} for y in years]
            self.assertFalse(r.projection(d, '0' * 64))

    def test_oldest_consistent_and_k5(self):
        d = fixture()
        d['counts']['oldest_year'] = 2020
        self.assertFalse(r.projection(d, '0' * 64))
        d['counts']['years']['groups'] = [{'year': 2020, 'count': 5}]
        self.assertTrue(r.projection(d, '0' * 64))
        d['counts']['oldest_year'] = 2021
        self.assertFalse(r.projection(d, '0' * 64))

    def test_duplicate_json(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                r.read(raw)

    def publish(self, out, d):
        raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
        (out / 'commandes.json').write_bytes(raw)
        (out / 'commandes.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')

    def test_report_channels_shutdown_and_coherent_tampering(self):
        with tempfile.TemporaryDirectory(prefix='a31-report-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            audit = base / 'audit.json'
            audit.write_text(json.dumps({'sections': {'commerce': {'order_storage': 'classic'}}}), encoding='utf-8')
            out = base / 'result'
            out.mkdir()
            d = fixture()
            d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
            self.publish(out, d)
            binding = b'A31_OK commandes.json commandes.md\nA31_FINAL ' + json.dumps(
                {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}).encode() + b'\n'
            self.assertTrue(r.complete_report(out, audit))
            self.assertTrue(r.final_binding(binding, out))
            d['counts']['years']['autres'] = 7
            d['counts']['oldest_year'] = 'fusionne'
            self.publish(out, d)
            self.assertTrue(r.complete_report(out, audit))
            self.assertFalse(r.final_binding(binding, out))
            d['storage'] = 'hpos'
            self.publish(out, d)
            self.assertFalse(r.complete_report(out, audit))
            d['storage'] = 'classic'
            for name in ('commandes.json', 'commandes.md', 'extra.json'):
                self.publish(out, d)
                (out / name).write_bytes(b'CANARY')
                self.assertFalse(r.complete_report(out, audit))
                if name == 'extra.json':
                    (out / name).unlink()


if __name__ == '__main__':
    unittest.main()
