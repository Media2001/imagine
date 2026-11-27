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


class SafetyTests(CoreTests):
    def config(self):
        return {'version': 1, 'types': {'papier': 910001},
                'paiements': {'virement': 'virement'},
                'options': dict.fromkeys(('importer_echus', 'resoudre_doublons',
                                         'calculer_prochaine_echeance'), False)}

    def test_five_issues_k5_and_no_values_in_public_reports(self):
        self.assertTrue(hasattr(self.core, 'public_reports'), 'A30 closed report reconstruction missing')
        rows = []
        issues = ['compte_a_creer'] * 5 + ['compte_existant'] * 5 + ['sans_email'] * 5 + ['type_a_decider'] * 4 + ['refuse_a13']
        for line, issue in enumerate(issues, 2):
            rows.append({'line': line, 'issue': issue, 'product': 910001 if line < 17 else None,
                         'payment': 'virement' if line < 17 else 'autre'})
        observation = {'schema': 'imagine-a30-private-v1', 'storage': 'classic',
                       'neutralised': False, 'rows': rows}
        summary, lines = self.core.public_reports(observation)
        self.assertEqual({'groups': [{'key': 'compte_a_creer', 'count': 5},
                                     {'key': 'compte_existant', 'count': 5},
                                     {'key': 'sans_email', 'count': 5}], 'autres': 5}, summary['issues'])
        self.assertEqual(list(range(2, 7)), lines['issues']['compte_a_creer'])
        self.assertEqual([21], lines['issues']['refuse_a13'])
        self.assertEqual(20, summary['total'])
        self.assertEqual(5, len(lines['issues']))

    def test_neutralisation_never_reports_zero_or_guesses_account_match(self):
        self.assertTrue(hasattr(self.core, 'public_reports'), 'A30 neutralised result reconstruction missing')
        observation = {'schema': 'imagine-a30-private-v1', 'storage': 'hpos', 'neutralised': True,
                       'rows': [{'line': 2, 'issue': None, 'product': 910001, 'payment': 'virement'}]}
        summary, lines = self.core.public_reports(observation)
        self.assertEqual(self.core.UNKNOWN, summary['accounts'])
        self.assertEqual(self.core.UNKNOWN, lines['issues']['compte_existant'])
        self.assertEqual(self.core.UNKNOWN, lines['issues']['compte_a_creer'])
        self.assertEqual([2], lines['rapprochement_inconnu'])

    def test_configuration_is_strict_and_all_business_options_are_off(self):
        self.assertTrue(hasattr(self.core, 'validate_config'), 'A30 strict type configuration missing')
        self.assertEqual(self.config(), self.core.validate_config(self.config()))
        for key in self.config()['options']:
            config = self.config(); config['options'][key] = True
            with self.assertRaisesRegex(RuntimeError, 'A30_OPTION_UNSUPPORTED'):
                self.core.validate_config(config)
        for mutate in (lambda c: c.update(extra='PRIVATE'),
                       lambda c: c['types'].update(papier=True),
                       lambda c: c['types'].update(papier=-1),
                       lambda c: c['paiements'].update(virement='PRIVATE')):
            config = self.config(); mutate(config)
            with self.assertRaisesRegex(RuntimeError, 'A30_CONFIG_INVALID'):
                self.core.validate_config(config)

    def test_exact_a13_refusal_code_and_message_no_outputs(self):
        import subprocess
        for name, content in [('iban', (FIXTURES / 'a13-export-iban-fictif.csv').read_bytes()),
                              ('encoding', (FIXTURES / 'a13-export-propre-fictif.csv').read_text(encoding='utf-8').encode('cp1252')),
                              ('ragged', b'Nom;Email\nx\n'), ('broken', b'Nom;Email\n"bad\n')]:
            with self.subTest(name=name):
                folder = self.work / name; folder.mkdir()
                source = folder / 'export.csv'; source.write_bytes(content)
                p = subprocess.run([sys.executable, str(ROOT / 'wp/outils/bascule/controler-export'),
                                    str(source), '--correspondance', str(MAPPING), '--au', '2026-11-25'],
                                   capture_output=True, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=20)
                try:
                    self.core.prepare(source, MAPPING, date(2026, 11, 25), self.config())
                    self.fail('A30 did not refuse an A13-refused file')
                except self.core.A13.Refus as error:
                    self.assertEqual(2, p.returncode)
                    self.assertEqual(('REFUS : ' + str(error) + '\n').encode(), p.stderr.replace(b'\r\n', b'\n'))
                self.assertEqual(['export.csv'], sorted(x.name for x in folder.iterdir()))
                self.assertEqual(content, source.read_bytes())

    def test_dirty_a13_fixture_exact_rejected_physical_lines(self):
        source = self.work / 'dirty.csv'
        source.write_bytes((FIXTURES / 'a13-export-defauts-fictif.csv').read_bytes())
        result = self.core.prepare(source, MAPPING, date(2026, 11, 25), self.config())
        self.assertEqual(1, result['a13_code'])
        self.assertEqual([2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27],
                         [r['line'] for r in result['rows'] if r['rejected']])
        self.assertTrue(all(not r['email'] for r in result['rows'] if r['rejected']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
