"""Synthetic unit counterexamples, not runtime/site receipts."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('guard', Path(__file__).with_name('b03-preservation.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class PreservationGuard(unittest.TestCase):
    def setUp(self):
        self.assets = ['themes/imagine/assets/reading.css', 'themes/imagine/assets/reading.js']
        self.c15 = {p: 'c15-final' for p in g.C15_PATHS}
        old = {p: 'old' for p in self.assets + g.C15_PATHS + g.TABLES}
        new = {**old, **self.c15, **{p: 'changed' for p in self.assets + g.TABLES}}
        self.baseline = {'remote': old, 'local': {k: v for k, v in old.items() if '/' in k}}
        self.start = {'remote': new, 'local': {k: v for k, v in new.items() if '/' in k}}
        self.end = copy.deepcopy(self.start)

    def compare(self):
        return g.compare(self.baseline, self.start, self.end, self.assets, self.c15)

    def test_stable_run_with_documented_source_delta(self):
        checks, evidence = self.compare()
        self.assertTrue(all(checks.values()))
        self.assertFalse(evidence['historical_whole_tables_unchanged'])
        self.assertEqual(len(evidence['historical_table_deltas']), 4)
        self.assertIn('NON prouvee', evidence['historical_table_classification'])

    def test_current_table_drift_rejected(self):
        self.end['remote']['wp_posts'] = 'unexpected'
        self.assertFalse(self.compare()[0]['snapshot_courant_distant_exact_stable'])

    def test_current_c15_drift_not_exempt(self):
        self.end['remote'][g.C15_PATHS[0]] = 'unexpected'
        self.assertFalse(self.compare()[0]['snapshot_courant_distant_exact_stable'])
        self.assertFalse(self.compare()[0]['sources_C15_exactes_recu_final_local_distant'])

    def test_unrelated_historical_source_rejected(self):
        self.start['remote']['plugins/other/file.php'] = 'unexpected'
        self.end = copy.deepcopy(self.start)
        self.assertFalse(self.compare()[0]['sources_historiques_deltas_exactement_B03_et_C15'])

    def test_missing_c15_change_rejected(self):
        key = g.C15_PATHS[0]
        self.baseline['remote'][key] = self.end['remote'][key]
        self.baseline['local'][key] = self.end['local'][key]
        self.assertFalse(self.compare()[0]['sources_historiques_deltas_exactement_B03_et_C15'])

    def test_final_c15_digest_required(self):
        self.c15[g.C15_PATHS[0]] = 'wrong-receipt'
        self.assertFalse(self.compare()[0]['sources_C15_exactes_recu_final_local_distant'])

    def test_local_change_rejected(self):
        self.end['local'][self.assets[0]] = 'unexpected'
        self.assertFalse(self.compare()[0]['snapshot_courant_local_exact_stable'])

    def test_local_only_c15_document_requires_exact_receipt(self):
        key = g.C15_LOCAL_DOCUMENT
        self.baseline['local'][key] = 'old-doc'
        self.start['local'][key] = self.end['local'][key] = 'final-doc'
        self.assertFalse(self.compare()[0]['sources_historiques_deltas_exactement_B03_et_C15'])
        checks, evidence = g.compare(self.baseline, self.start, self.end, self.assets, self.c15, {key: 'final-doc'})
        self.assertTrue(all(checks.values()))
        self.assertIn(key, evidence['C15_local_only_document_deltas'])
        checks, _ = g.compare(self.baseline, self.start, self.end, self.assets, self.c15, {key: 'wrong-doc'})
        self.assertFalse(checks['documents_C15_locaux_exactement_lies_livraison'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
