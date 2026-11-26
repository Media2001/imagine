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


if __name__ == '__main__':
    unittest.main()
