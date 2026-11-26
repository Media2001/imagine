"""Closed A24 report publication: real filesystem, adversarial keys and strings."""
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
HERE = ROOT / 'wp/outils/bascule/a24'
FIELDS = ['first_name', 'last_name', 'company', 'country', 'address_1', 'address_2', 'city', 'state', 'postcode', 'phone']


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (HERE / 'report.py').is_file():
            raise AssertionError('mandatory closed publication validator is missing')
        spec = importlib.util.spec_from_file_location('a24_report_test', HERE / 'report.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def data(self, neutral=False):
        counts = {'subscriptions': 5, 'shipping_empty': 0, 'empty_with_billing': 0, 'missing_any': 0,
                  'missing_required': {'shipping_' + f: 0 for f in FIELDS}, 'country_absent': 0,
                  'country_unknown': 0, 'different_from_account': 0, 'account_unavailable': 0}
        if neutral:
            for key in ('shipping_empty', 'empty_with_billing', 'missing_any', 'different_from_account'):
                counts[key] = self.module.UNKNOWN
            for key in counts['missing_required']:
                if key != 'shipping_country':
                    counts['missing_required'][key] = self.module.UNKNOWN
        return {'schema': 'imagine-a24-shipping-addresses-v1', 'read_only': True, 'storage': 'classic',
                'neutralisation': self.module.UNKNOWN if neutral else 'observe',
                'counts': {'overall': counts, 'countries': [{'country': 'BE', 'counts': copy.deepcopy(counts)}]},
                'audit_sha256': '0' * 64}

    def test_valid_observed_and_neutralised(self):
        for neutral in (False, True):
            self.assertTrue(self.module.projection(self.data(neutral), '0' * 64))

    def test_every_free_string_and_extra_key_refused(self):
        paths = [('country',), ('schema',), ('extra',), ('metric',), ('field',)]
        for path in paths:
            d = self.data()
            if path[0] == 'country':
                d['counts']['countries'][0]['country'] = 'A24_PRIVATE_CANARY'
            elif path[0] == 'schema':
                d['schema'] = 'A24_PRIVATE_CANARY'
            elif path[0] == 'extra':
                d['address'] = 'A24_PRIVATE_CANARY'
            elif path[0] == 'metric':
                d['counts']['overall']['subscriptions'] = 'A24_PRIVATE_CANARY'
            else:
                d['counts']['overall']['missing_required']['shipping_A24_PRIVATE_CANARY'] = 1
            self.assertFalse(self.module.projection(d, '0' * 64), path)

    def test_bad_numbers_and_partition_refused(self):
        for value in (-1, True, 1.0, None, 2**53):
            d = self.data()
            d['counts']['overall']['subscriptions'] = value
            self.assertFalse(self.module.projection(d, '0' * 64), value)
        for value in (4, 6):
            d = self.data()
            d['counts']['countries'][0]['counts']['subscriptions'] = value
            self.assertFalse(self.module.projection(d, '0' * 64))

    def test_unknown_is_mandatory_after_neutralisation(self):
        d = self.data(True)
        d['counts']['overall']['shipping_empty'] = 0
        self.assertFalse(self.module.projection(d, '0' * 64))

    def test_full_directory_requires_exact_canonical_files(self):
        with tempfile.TemporaryDirectory(prefix='a24-report-', dir=os.environ.get('TMPDIR')) as tmp:
            root = Path(tmp)
            audit = root / 'audit.json'
            audit.write_bytes(b'{}')
            output = root / 'out'
            output.mkdir()
            d = self.data()
            d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
            raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (output / 'expedition.json').write_bytes(raw)
            (output / 'expedition.md').write_bytes(self.module.MARKDOWN.encode('utf-8') + raw + b'```\n')
            self.assertTrue(self.module.complete_report(output, audit))
            (output / 'expedition.md').write_bytes(b'A24_PRIVATE_CANARY')
            self.assertFalse(self.module.complete_report(output, audit))
            (output / 'expedition.md').write_bytes(self.module.MARKDOWN.encode('utf-8') + raw + b'```\n')
            (output / 'extra').write_bytes(b'A24_PRIVATE_CANARY')
            self.assertFalse(self.module.complete_report(output, audit))


if __name__ == '__main__':
    unittest.main()
