"""A30 CLI tests use real Windows Python, never PHP."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / 'wp/outils/bascule/a30/confine.py'
MAPPING = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
FIX = ROOT / 'wp/tests/fixtures'


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a30-cli-', dir=os.environ['TMPDIR'])
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def call(self, fixture, encoding='utf-8'):
        source = self.work / 'input.csv'; source.write_bytes((FIX / fixture).read_bytes())
        return subprocess.run([sys.executable, str(CLI), '--wp-path=' + str(self.work / 'missing-site'),
                               '--fichier=' + str(source), '--correspondance=' + str(MAPPING),
                               '--types=' + str(ROOT / 'wp/outils/bascule/a30/types.exemple.json'),
                               '--audit=' + str(self.work / 'audit.json'), '--au=2026-11-25'],
                              capture_output=True, env={**os.environ, 'PYTHONIOENCODING': encoding,
                                                       'PYTHONDONTWRITEBYTECODE': '1'}, timeout=20)

    def test_cli_a13_refusal_precedes_site_php_and_has_same_exit_code(self):
        self.assertTrue(CLI.is_file(), 'A30 guarded launcher missing')
        p = self.call('a13-export-iban-fictif.csv')
        self.assertEqual(2, p.returncode, p.stderr)
        self.assertEqual(b'', p.stdout)
        self.assertEqual('REFUS : IBAN suspect : colonne 14. Aucun fichier produit ; retirer cette colonne de la copie à contrôler.\n',
                         p.stderr.decode('utf-8').replace('\r\n', '\n'))
        self.assertEqual(['input.csv'], [p.name for p in self.work.iterdir()])

    def test_console_cp1252_and_ascii_a13_refusal_never_traceback(self):
        self.assertTrue(CLI.is_file(), 'A30 guarded launcher missing')
        for encoding in ('cp1252', 'ascii'):
            p = self.call('a13-export-iban-fictif.csv', encoding)
            self.assertEqual(2, p.returncode)
            self.assertEqual(b'', p.stdout)
            self.assertIn(b'IBAN suspect', p.stderr)
            self.assertNotIn(b'Traceback', p.stderr)

    @unittest.skipUnless(os.name == 'nt', 'Windows-only fail-closed platform gate')
    def test_windows_success_path_refuses_without_php_execution(self):
        self.assertTrue(CLI.is_file(), 'A30 guarded launcher missing')
        p = self.call('a13-export-propre-fictif.csv')
        self.assertEqual((1, b'', b'A30_CONFINEMENT_REQUIRED\r\n'), (p.returncode, p.stdout, p.stderr))
        self.assertEqual(['input.csv'], [p.name for p in self.work.iterdir()])


if __name__ == '__main__':
    unittest.main(verbosity=2)
