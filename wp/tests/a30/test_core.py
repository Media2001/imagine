"""A30: synthetic data only; A13 is imported read-only."""
import csv
from datetime import date
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/bascule/a30'
FIXTURES = ROOT / 'wp/tests/fixtures'
MAPPING = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
sys.path.insert(0, str(TOOLS))


def load_core():
    if not (TOOLS / 'core.py').is_file():
        return None
    spec = importlib.util.spec_from_file_location('a30_core', TOOLS / 'core.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a30-python-', dir=os.environ['TMPDIR'])
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.core = load_core()

    def test_a13_clean_fixture_is_parsed_without_a13_outputs(self):
        self.assertIsNotNone(self.core, 'A30 read-only A13 adapter is missing')
        source = self.work / 'export.csv'
        before = (FIXTURES / 'a13-export-propre-fictif.csv').read_bytes()
        source.write_bytes(before)
        config = {'version': 1, 'types': {'papier': 910001},
                  'paiements': {'virement': 'virement'},
                  'options': {'importer_echus': False, 'resoudre_doublons': False,
                              'calculer_prochaine_echeance': False}}
        result = self.core.prepare(source, MAPPING, date(2026, 11, 25), config)
        self.assertEqual(0, result['a13_code'])
        self.assertEqual(30, len(result['rows']))
        self.assertEqual(list(range(2, 32)), [r['line'] for r in result['rows']])
        self.assertTrue(all(not r['rejected'] and r['product'] == 910001 for r in result['rows']))
        self.assertEqual(before, source.read_bytes())
        self.assertEqual(['export.csv'], sorted(p.name for p in self.work.iterdir()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
