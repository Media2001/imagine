"""A-13 : preuves CLI hors dépôt, données exclusivement fictives."""
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / 'wp/outils/bascule/controler-export'
CONFIG = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
FIXTURES = ROOT / 'wp/tests/fixtures'
SCRATCH = Path(os.environ.get('TMPDIR', tempfile.gettempdir()))


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a13-test-', dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def run_cli(self, fixture='a13-export-propre-fictif.csv', content=None, config=None, extra=()):
        source = self.work / 'export.csv'
        source.write_bytes((FIXTURES / fixture).read_bytes() if content is None else content)
        mapping = CONFIG
        if config is not None:
            mapping = self.work / 'correspondance.json'
            mapping.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(TOOL), str(source), '--correspondance', str(mapping),
             '--au', '2026-11-25', *extra], capture_output=True, encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'},
            timeout=20,
        )
        return result, source

    def summary(self, source):
        return source.with_name(source.stem + '.controle-resume.txt').read_text(encoding='utf-8')

    def rejects(self, source):
        path = source.with_name(source.stem + '.controle-rejets.csv')
        return list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')), delimiter=';'))

    def assert_refused(self, result, source, message):
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertEqual('', result.stdout)
        self.assertFalse(source.with_name(source.stem + '.controle-resume.txt').exists())
        self.assertFalse(source.with_name(source.stem + '.controle-rejets.csv').exists())

    def clean_bytes(self):
        return (FIXTURES / 'a13-export-propre-fictif.csv').read_bytes()

    def test_iban_header_refused_without_values_or_output(self):
        result, source = self.run_cli(fixture='a13-export-iban-fictif.csv')
        self.assert_refused(result, source, 'IBAN suspect : colonne 14')
        self.assertNotIn('ZZ00', result.stdout + result.stderr)
        self.assertNotIn('Fictif', result.stdout + result.stderr)

    def test_iban_content_at_end_in_unmapped_column_precedes_all_analysis(self):
        text = self.clean_bytes().decode('utf-8').replace(';Reference mandat', ';Reference mandat;Note')
        lines = text.splitlines()
        lines[1:] = [line + ';' for line in lines[1:]]
        lines[1] = lines[1].replace(';2099-12-31;', ';date-invalide;')
        secret = 'ZZ00 0000 0000 0000 0000'
        lines[-1] += secret
        result, source = self.run_cli(content=('\n'.join(lines) + '\n').encode())
        self.assert_refused(result, source, 'IBAN suspect : colonne 14')
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertNotIn('date-invalide', result.stdout + result.stderr)

    def test_iban_in_header_value_is_not_echoed(self):
        text = self.clean_bytes().decode().replace(';Reference mandat', ';ZZ00000000000000000000')
        result, source = self.run_cli(content=text.encode())
        self.assert_refused(result, source, 'IBAN suspect : colonne 13')
        self.assertNotIn('ZZ00', result.stdout + result.stderr)

    def test_repository_output_refused_without_touching_fixture(self):
        # Clone minimal en scratch : même le test RED n'écrit rien dans le dépôt.
        clone = self.work / 'depot/wp/outils/bascule/controler-export'
        clone.parent.mkdir(parents=True)
        clone.write_bytes(TOOL.read_bytes())
        source = self.work / 'depot/export.csv'
        before = self.clean_bytes()
        source.write_bytes(before)
        result = subprocess.run([sys.executable, str(clone), str(source), '--correspondance', str(CONFIG)],
                                capture_output=True, encoding='utf-8', timeout=20)
        self.assert_refused(result, source, 'dépôt')
        self.assertEqual(before, source.read_bytes())

    def test_existing_output_is_not_overwritten(self):
        source = self.work / 'export.csv'
        output = source.with_name('export.controle-rejets.csv')
        output.write_text('GARDE FICTIF', encoding='utf-8')
        result, source = self.run_cli()
        self.assertEqual(2, result.returncode)
        self.assertIn('existent déjà', result.stderr)
        self.assertEqual('GARDE FICTIF', output.read_text(encoding='utf-8'))
        self.assertFalse(source.with_name('export.controle-resume.txt').exists())

    def config(self):
        return json.loads(CONFIG.read_text(encoding='utf-8'))

    def test_legacy_encoding_requires_explicit_declaration(self):
        result, source = self.run_cli(content=self.clean_bytes().decode().encode('cp1252'))
        self.assert_refused(result, source, 'Encodage indéterminé')

    def test_declared_cp1252_is_accepted_and_reported(self):
        config = self.config()
        config['encodage'] = 'cp1252'
        result, source = self.run_cli(content=self.clean_bytes().decode().encode('cp1252'), config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Encodage : cp1252 (déclaré)', self.summary(source))

    def test_utf16_bom_is_detected(self):
        result, source = self.run_cli(content=self.clean_bytes().decode().encode('utf-16'))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Encodage : utf-16 (BOM)', self.summary(source))

    def test_utf8_bom_is_detected(self):
        result, source = self.run_cli(content=b'\xef\xbb\xbf' + self.clean_bytes())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Encodage : utf-8-sig (BOM)', self.summary(source))

    def test_conflicting_bom_and_declared_encoding_is_refused(self):
        config = self.config()
        config['encodage'] = 'cp1252'
        result, source = self.run_cli(content=b'\xef\xbb\xbf' + self.clean_bytes(), config=config)
        self.assert_refused(result, source, 'BOM incompatible')

    def test_comma_delimiter_is_detected_and_reported(self):
        result, source = self.run_cli(content=self.clean_bytes().replace(b';', b','))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Séparateur : virgule (détecté)', self.summary(source))

    def test_tab_delimiter_is_detected(self):
        result, source = self.run_cli(content=self.clean_bytes().replace(b';', b'\t'))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Séparateur : tabulation (détecté)', self.summary(source))

    def test_ambiguous_delimiter_is_refused(self):
        text = self.clean_bytes().decode().replace('Nom;', 'Nom,X;').replace('Fictif Licorne ', 'Fictif, Licorne ')
        result, source = self.run_cli(content=text.encode())
        self.assert_refused(result, source, 'Séparateur ambigu')

    def test_declared_delimiter_resolves_ambiguity(self):
        config = self.config()
        config['separateur'] = ';'
        config['colonnes']['nom'] = 'Nom,X'
        text = self.clean_bytes().decode().replace('Nom;', 'Nom,X;').replace('Fictif Licorne ', 'Fictif, Licorne ')
        result, source = self.run_cli(content=text.encode(), config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('point-virgule (déclaré)', self.summary(source))

    def test_ragged_csv_refused_without_output(self):
        result, source = self.run_cli(content=self.clean_bytes() + b'incomplet;oui\n')
        self.assert_refused(result, source, 'CSV')

    def test_iban_after_ragged_row_still_prevents_output(self):
        result, source = self.run_cli(content=self.clean_bytes() + b'incomplet;oui\nZZ00000000000000000000\n')
        self.assert_refused(result, source, 'IBAN suspect')
        self.assertNotIn('ZZ00', result.stderr)

    def test_duplicate_header_is_refused(self):
        result, source = self.run_cli(content=self.clean_bytes().replace(b';Prenom;', b';Nom;'))
        self.assert_refused(result, source, 'En-têtes')

    def test_missing_mapped_header_is_refused(self):
        result, source = self.run_cli(content=self.clean_bytes().replace(b';Email;', b';Courriel;'))
        self.assert_refused(result, source, 'colonne configurée absente')

    def test_unknown_configuration_key_is_refused(self):
        config = self.config()
        config['separateurr'] = ';'
        result, source = self.run_cli(config=config)
        self.assert_refused(result, source, 'Correspondance')

    def test_email_cannot_be_mandatory(self):
        config = self.config()
        config['obligatoires'].append('email')
        result, source = self.run_cli(config=config)
        self.assert_refused(result, source, 'email ne peut pas être obligatoire')

    def test_clean_file_returns_zero_and_thirty_clean_rows(self):
        result, source = self.run_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Lignes contrôlées : 30', self.summary(source))
        self.assertIn('Lignes sans défaut : 30', self.summary(source))
        self.assertEqual([], self.rejects(source))
        self.assertEqual('', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
