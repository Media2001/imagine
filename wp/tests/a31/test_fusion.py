"""Fusion scalar contract: exact anomalies, rare dimensional years hidden."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('a31_fusion_report', ROOT / 'wp/outils/bascule/a31/report.py')
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)
METRICS = ('orphan_renewals', 'living_without_parent', 'orders_missing_account', 'orders_link_unknown')


def payload():
    return {'schema': 'imagine-a31-history-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'audit_sha256': '0' * 64,
            'counts': {**dict.fromkeys(METRICS, 0),
                       **{key: {'groups': [], 'autres': 0} for key in ('years', 'statuses', 'natures')},
                       'refunds': {'total': 0, 'groups': [], 'autres': 0}, 'oldest_year': None}}


class FusionTests(unittest.TestCase):
    def test_exact_scalar_zero_one_four_five_alone_and_mixed(self):
        for storage in ('classic', 'hpos'):
            for metric in METRICS:
                for count in (0, 1, 4, 5):
                    for mixed in (False, True):
                        with self.subTest(storage=storage, metric=metric, count=count, mixed=mixed):
                            data = payload()
                            data['storage'] = storage
                            for key in METRICS:
                                data['counts'][key] = count if key == metric else (4 if mixed else 0)
                            self.assertTrue(r.projection(data, '0' * 64))
                            bad = copy.deepcopy(data)
                            bad['counts'][metric] = {'groups': [], 'autres': count}
                            self.assertFalse(r.projection(bad, '0' * 64))

    def test_refund_total_exact_but_rare_year_hidden(self):
        for count in (0, 1, 4, 5):
            data = payload()
            data['counts']['refunds'] = {'total': count, 'autres': count if count < 5 else 0,
                                         'groups': [] if count < 5 else [{'year': 2021, 'count': count}]}
            self.assertTrue(r.projection(data, '0' * 64))
            data['counts']['refunds']['total'] += 1
            self.assertFalse(r.projection(data, '0' * 64))

    def test_scalars_closed_numeric_contract(self):
        for metric in METRICS:
            for value in (-1, True, 2**53, 1.5, '1', None, 'inconnu après neutralisation'):
                data = payload()
                data['counts'][metric] = value
                self.assertFalse(r.projection(data, '0' * 64))


if __name__ == '__main__':
    unittest.main()
