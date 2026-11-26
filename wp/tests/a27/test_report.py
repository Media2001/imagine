"""Public report schema and byte-for-byte publication gates; synthetic only."""
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
spec = importlib.util.spec_from_file_location('a27_report', ROOT / 'wp/outils/bascule/a27/report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
CLOCK = '2026-11-26T12:00:00+00:00'


def fixture():
    return {'schema': 'imagine-a27-saved-payments-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'counts': {key: {'groups': [], 'autres': 0} for key in r.COUNTS},
            'as_of_utc': CLOCK, 'audit_sha256': '0' * 64}


class ReportTests(unittest.TestCase):
    def test_nominal(self):
        self.assertTrue(r.projection(fixture(), '0' * 64, CLOCK))

    def test_visible_five_and_rare_four(self):
        for field, key, value in [('automatic', 'type', 'carte'), ('cards', 'expiry', 'expired'),
                                  ('relations', 'metric', 'subscriptions_unlinked')]:
            for n in range(6):
                d = fixture()
                d['counts'][field]['groups'] = [{'gateway': 'stripe', key: value, 'count': n}]
                self.assertEqual(r.projection(d, '0' * 64), n == 5)

    def test_no_open_gateway_even_syntactically_technical(self):
        for gateway in ('A27_PRIVATE_CANARY', 'a27_private_canary', 'pm_123', 'cus_example', '', 'stripe\n'):
            d = fixture()
            d['counts']['automatic']['groups'] = [{'gateway': gateway, 'type': 'carte', 'count': 5}]
            self.assertFalse(r.projection(d, '0' * 64))

    def test_closed_types_and_expiries(self):
        for field, key, allowed in [('automatic', 'type', r.TYPES), ('cards', 'expiry', r.EXPIRIES),
                                     ('relations', 'metric', r.METRICS)]:
            for value in list(allowed) + ['absent', 'A27_PRIVATE_CANARY', None, True, 42]:
                d = fixture()
                d['counts'][field]['groups'] = [{'gateway': 'stripe', key: value, 'count': 5}]
                self.assertEqual(r.projection(d, '0' * 64), value in allowed)

    def test_no_individual_or_extra_keys(self):
        for path in [(), ('counts',), ('counts', 'automatic'), ('counts', 'cards'), ('counts', 'relations')]:
            d = fixture()
            o = d
            for key in path:
                o = o[key]
            o['A27_PRIVATE_CANARY'] = 'A27_PRIVATE_CANARY'
            self.assertFalse(r.projection(d, '0' * 64))

    def test_count_types(self):
        for value in (-1, 2**53, True, 1.5, '5', None, [], {}):
            d = fixture()
            d['counts']['cards']['autres'] = value
            self.assertFalse(r.projection(d, '0' * 64))

    def test_all_neutralised_counts_unknown(self):
        d = fixture()
        d['neutralisation'] = r.UNKNOWN
        self.assertFalse(r.projection(d, '0' * 64))
        for key in r.COUNTS:
            d['counts'][key] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))
        for key in r.COUNTS:
            bad = copy.deepcopy(d)
            bad['counts'][key] = {'groups': [], 'autres': 0}
            self.assertFalse(r.projection(bad, '0' * 64))

    def test_clock_exact_and_bound(self):
        for value in ('2026-02-30T12:00:00+00:00', CLOCK + 'A27_PRIVATE_CANARY', True, None,
                      '2026-11-26T12:00:00+01:00', '2026-11-26T12:00:00Z'):
            d = fixture()
            d['as_of_utc'] = value
            self.assertFalse(r.projection(d, '0' * 64))
        self.assertFalse(r.projection(fixture(), '0' * 64, '2026-11-27T12:00:00+00:00'))

    def test_duplicate_or_unsorted_cells(self):
        a = {'gateway': 'stripe', 'type': 'carte', 'count': 5}
        b = {'gateway': 'paypal', 'type': 'accord_paypal', 'count': 5}
        for rows in ([a, a], [a, b]):
            d = fixture()
            d['counts']['automatic']['groups'] = rows
            self.assertFalse(r.projection(d, '0' * 64))

    def test_audit_hash_binding(self):
        self.assertFalse(r.projection(fixture(), '1' * 64))

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
        (out / 'paiements.json').write_bytes(raw)
        (out / 'paiements.md').write_bytes(r.MARKDOWN.encode() + raw + b'```\n')

    def test_published_storage_bound_to_audit(self):
        with tempfile.TemporaryDirectory(prefix='a27-schema-', dir=os.environ.get('TMPDIR')) as tmp:
            out, audit, data = self.make_report(Path(tmp))
            self.assertTrue(r.complete_report(out, audit))
            data['storage'] = 'hpos'
            self.publish(out, data)
            self.assertFalse(r.complete_report(out, audit))

    def test_canary_in_each_report_and_extra_file(self):
        for channel in ('paiements.json', 'paiements.md', 'extra.txt'):
            with self.subTest(channel=channel), tempfile.TemporaryDirectory(prefix='a27-files-', dir=os.environ.get('TMPDIR')) as tmp:
                out, audit, data = self.make_report(Path(tmp))
                self.assertTrue(r.complete_report(out, audit))
                with (out / channel).open('ab') as h:
                    h.write(b'A27_PRIVATE_CANARY')
                self.assertFalse(r.complete_report(out, audit))

    def test_missing_empty_and_noncanonical_files(self):
        for mode in ('missing', 'empty', 'noncanonical', 'directory'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='a27-file-', dir=os.environ.get('TMPDIR')) as tmp:
                out, audit, data = self.make_report(Path(tmp))
                if mode in ('missing', 'directory'):
                    (out / 'paiements.md').unlink()
                    if mode == 'directory':
                        (out / 'paiements.md').mkdir()
                elif mode == 'empty':
                    (out / 'paiements.json').write_bytes(b'')
                else:
                    (out / 'paiements.json').write_text(json.dumps(data), encoding='utf-8')
                self.assertFalse(r.complete_report(out, audit))


if __name__ == '__main__':
    unittest.main()
