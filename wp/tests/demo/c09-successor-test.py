"""Focused regression tests for repaired C09 and exact successor baselines."""
from pathlib import Path
import importlib.util
import json
import sys
import unittest
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))


class SuccessorGatesTest(unittest.TestCase):
    def test_c17_does_not_require_historical_failure(self):
        text = (Path(__file__).with_name('c17-verifier.py')).read_text(encoding='utf-8')
        self.assertNotIn("assert native['failures']==reserve", text)
        self.assertIn('successor', text)

    def test_c18_does_not_require_historical_failure(self):
        text = (Path(__file__).with_name('c18-verifier.py')).read_text(encoding='utf-8')
        self.assertNotIn("assert c09['failures'] == ['A-PAPIER:action_native_planifiee_ou_absente_selon_statut']", text)
        self.assertIn('successor', text)

    def test_receipt_is_native_green(self):
        receipt = json.loads((ROOT / 'production/C-09/papier-restauration-V2.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['native_after']['total'], 382)
        self.assertEqual(receipt['native_after']['failures'], [])
        self.assertFalse(receipt['global_seed_replayed'])
        self.assertEqual(receipt['target_after']['scheduled'], receipt['target_after']['next_payment_timestamp'])


    def test_baseline_accepts_only_authorized_c18_bridge(self):
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        bridge = module.baseline_contract(receipt['before'], receipt['after'], receipt)
        self.assertFalse(bridge['historical_baseline_rewritten'])

    def test_baseline_accepts_c17_projection(self):
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        before = {k:v for k,v in receipt['before'].items() if k != 'native_fingerprints'}
        after = {k:v for k,v in receipt['after'].items() if k != 'native_fingerprints'}
        self.assertFalse(module.baseline_contract(before, after, receipt)['historical_baseline_rewritten'])

    def test_baseline_refuses_old_broken_current_state(self):
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        with self.assertRaises(AssertionError):
            module.baseline_contract(receipt['before'], receipt['before'], receipt)

    def test_baseline_refuses_other_order_drift(self):
        import copy
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        current = copy.deepcopy(receipt['after'])
        current['commandes']['100'] = 'drift'
        with self.assertRaises(AssertionError):
            module.baseline_contract(receipt['before'], current, receipt)

    def test_baseline_refuses_unrelated_action_drift(self):
        import copy
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        current = copy.deepcopy(receipt['after'])
        current['native_fingerprints']['actionscheduler_actions']['sha256'] = 'drift'
        with self.assertRaises(AssertionError):
            module.baseline_contract(receipt['before'], current, receipt)

    def test_baseline_refuses_unknown_historical_baseline(self):
        import copy
        module = __import__('importlib').import_module('c09-papier')
        receipt = json.loads(module.RECEIPT.read_text(encoding='utf-8'))
        baseline = copy.deepcopy(receipt['before'])
        baseline['options']['imagine_demo_calendrier'] = 'drift'
        with self.assertRaises(AssertionError):
            module.baseline_contract(baseline, receipt['after'], receipt)


if __name__ == '__main__':
    unittest.main()
