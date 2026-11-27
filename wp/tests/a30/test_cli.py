"""A30 CLI tests use real Windows Python, never PHP."""
import json
import os
from pathlib import Path
import subprocess
import sys
from temp_support import temporary_directory
import unittest

ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / 'wp/outils/bascule/a30/confine.py'
MAPPING = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
FIX = ROOT / 'wp/tests/fixtures'


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = temporary_directory('a30-cli-')
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

    def test_strict_arguments_no_unknown_duplicate_empty_or_invalid_date(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('a30_cli_arguments', CLI)
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        valid = ['--wp-path=/site', '--fichier=/input.csv', '--correspondance=/mapping.json',
                 '--types=/types.json', '--audit=/audit.json', '--au=2026-11-25']
        self.assertEqual(6, len(cli.arguments(valid)[0]))
        for args in (valid + ['--unknown=yes'], valid + [valid[0]], valid[:-1],
                     ['--wp-path='] + valid[1:], valid[:-1] + ['--au=20261125'],
                     valid[:-1] + ['--au=2026-02-30'], ['--wp-path', '/site'] + valid[1:]):
            with self.subTest(args=args), self.assertRaisesRegex(RuntimeError, 'A30_USAGE'):
                cli.arguments(args)

    def test_same_invalid_files_have_exact_a13_cli_exit_streams(self):
        clean = (FIX / 'a13-export-propre-fictif.csv').read_bytes()
        header = clean.splitlines()[0]
        for label, content in [('ragged', header + b'\nx\n'),
                               ('broken', header + b'\n"bad\n'),
                               ('iban_broken', header + b';IBAN\n"bad\n'),
                               ('encoding', clean.decode('utf-8').encode('cp1252'))]:
            with self.subTest(label=label):
                folder = self.work / label; folder.mkdir()
                source = folder / 'input.csv'; source.write_bytes(content)
                common = ['--correspondance=' + str(MAPPING), '--au=2026-11-25']
                ref = subprocess.run([sys.executable, '-B', str(ROOT / 'wp/outils/bascule/controler-export'),
                                      str(source), *common], capture_output=True,
                                     env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=20)
                got = subprocess.run([sys.executable, '-B', str(CLI), '--fichier=' + str(source),
                                      '--wp-path=' + str(folder / 'missing-site'),
                                      '--types=' + str(ROOT / 'wp/outils/bascule/a30/types.exemple.json'),
                                      '--audit=' + str(folder / 'missing-audit.json'), *common], capture_output=True,
                                     env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=20)
                self.assertEqual(2, ref.returncode)
                self.assertEqual((ref.returncode, ref.stdout, ref.stderr), (got.returncode, got.stdout, got.stderr))
                self.assertEqual(content, source.read_bytes())
                self.assertEqual(['input.csv'], [p.name for p in folder.iterdir()])

    @unittest.skipUnless(os.name == 'nt', 'Windows-only fail-closed platform gate')
    def test_windows_success_path_refuses_without_php_execution(self):
        self.assertTrue(CLI.is_file(), 'A30 guarded launcher missing')
        p = self.call('a13-export-propre-fictif.csv')
        self.assertEqual((1, b'', b'A30_CONFINEMENT_REQUIRED\r\n'), (p.returncode, p.stdout, p.stderr))
        self.assertEqual(['input.csv'], [p.name for p in self.work.iterdir()])


if __name__ == '__main__':
    unittest.main(verbosity=2)
