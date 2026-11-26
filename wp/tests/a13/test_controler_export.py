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

    def run_cli(self, fixture='a13-export-propre-fictif.csv', content=None, config=None, extra=(), work=None):
        work = work or self.work
        source = work / 'export.csv'
        source.write_bytes((FIXTURES / fixture).read_bytes() if content is None else content)
        mapping = CONFIG
        if config is not None:
            mapping = work / 'correspondance.json'
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
                                capture_output=True, encoding='utf-8',
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'},
                                timeout=20)
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

    def test_dirty_fixture_each_defect_is_reported_on_exact_source_line(self):
        expected = {
            2: 'Champ obligatoire absent : nom',
            3: 'Date d’échéance illisible', 4: 'Date d’échéance passée',
            5: 'Nombre de numéros dus illisible', 6: 'Nombre de numéros dus négatif',
            7: 'Adresse postale incomplète', 8: 'Adresse électronique mal formée',
            9: 'Mode de paiement non déclaré', 10: 'Mandat papier sans référence',
            12: 'Doublon d’adresse électronique', 13: 'Doublon d’adresse électronique',
            14: 'Doublon de nom et adresse postale', 15: 'Doublon de nom et adresse postale',
            16: 'Référence de mandat en double', 17: 'Référence de mandat en double',
            18: 'Champ obligatoire absent : type_abonnement',
            19: 'Champ obligatoire absent : echeance', 20: 'Champ obligatoire absent : numeros_dus',
            21: 'Adresse postale incomplète', 22: 'Adresse postale incomplète', 23: 'Adresse postale incomplète',
            24: 'Champ obligatoire absent : cooperateur', 25: 'Champ obligatoire absent : mode_paiement',
            26: 'Nombre de numéros dus illisible', 27: 'Date d’échéance illisible',
        }
        result, source = self.run_cli(fixture='a13-export-defauts-fictif.csv')
        self.assertEqual(1, result.returncode, result.stderr)
        actual = self.rejects(source)
        self.assertEqual([{'ligne': str(line), 'motif': motif} for line, motif in expected.items()], actual)
        summary = self.summary(source)
        for text in ('Lignes contrôlées : 30', 'Lignes sans défaut : 5', 'Lignes rejetées : 25',
                     'Lignes sans adresse électronique : 1', 'Lignes en doublon : 6'):
            self.assertIn(text, summary)
        self.assertIn('Adresse postale incomplète : 4', summary)
        self.assertIn('Date d’échéance illisible : 2', summary)
        outputs = summary + str(actual) + result.stdout + result.stderr
        for forbidden in ('example.org', 'Licorne', 'Éléphant', 'MANDAT-FICTIF', 'illisible-fictif'):
            self.assertNotIn(forbidden, outputs)

    def test_without_email_is_clean_and_counted(self):
        text = self.clean_bytes().decode().replace('a13-fictif-01@example.org', '')
        result, source = self.run_cli(content=text.encode())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Lignes sans adresse électronique : 1', self.summary(source))
        self.assertEqual([], self.rejects(source))

    def test_optional_absent_email_column_never_invents_addresses(self):
        config = self.config()
        config['colonnes']['email'] = None
        rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))
        for row in rows:
            del row[6]
        stream = io.StringIO(newline='')
        csv.writer(stream, delimiter=';').writerows(rows)
        result, source = self.run_cli(content=stream.getvalue().encode(), config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Lignes sans adresse électronique : 30', self.summary(source))
        self.assertEqual([], self.rejects(source))

    def test_due_today_and_zero_issues_are_not_rejected(self):
        text = self.clean_bytes().replace(b';2099-12-31;', b';2026-11-25;').replace(b';4;', b';0;')
        result, source = self.run_cli(content=text)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], self.rejects(source))

    def test_date_format_is_declared_not_guessed(self):
        config = self.config()
        config['format_date'] = '%d/%m/%Y'
        text = self.clean_bytes().replace(b'2099-12-31', b'31/12/2099')
        result, source = self.run_cli(content=text, config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], self.rejects(source))

    def test_optional_subscription_type_filter_is_off_by_default(self):
        result, source = self.run_cli(content=self.clean_bytes().replace(b';papier;', b';type-fictif-inconnu;'))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], self.rejects(source))

    def test_subscription_type_filter_without_mapped_column_is_refused(self):
        config = self.config()
        config['colonnes']['type_abonnement'] = None
        config['obligatoires'].remove('type_abonnement')
        config['types_abonnement_autorises'] = ['numerique']
        result, source = self.run_cli(config=config)
        self.assert_refused(result, source,
                            'Correspondance : types_abonnement_autorises exige une colonne type_abonnement mappée')
        self.assertNotIn('Traceback', result.stderr)

    def test_empty_subscription_type_filter_allows_unmapped_optional_column(self):
        config = self.config()
        config['colonnes']['type_abonnement'] = None
        config['obligatoires'].remove('type_abonnement')
        self.assertEqual([], config['types_abonnement_autorises'])
        result, source = self.run_cli(config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], self.rejects(source))

    def test_optional_subscription_type_filter_when_enabled(self):
        config = self.config()
        config['types_abonnement_autorises'] = ['numerique']
        result, source = self.run_cli(config=config)
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual(30, len(self.rejects(source)))
        self.assertEqual('Type d’abonnement non déclaré', self.rejects(source)[0]['motif'])

    def test_source_line_number_remains_physical_with_quoted_multiline_cells(self):
        text = self.clean_bytes().decode().replace(';1 rue Imaginaire;', ';"1 rue\nImaginaire";')
        text = text.replace('a13-fictif-02@example.org', 'email-invalide')
        result, source = self.run_cli(content=text.encode())
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual([{'ligne': '4', 'motif': 'Adresse électronique mal formée'}], self.rejects(source))

    def test_missing_mandatory_postal_field_has_only_specific_reason(self):
        for field, index in (('rue', 2), ('code_postal', 3), ('ville', 4), ('pays', 5)):
            with self.subTest(field=field):
                config = self.config()
                config['obligatoires'].append(field)
                rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))
                rows[1][index] = ''
                stream = io.StringIO(newline='')
                csv.writer(stream, delimiter=';').writerows(rows)
                work = self.work / field
                work.mkdir()
                result, source = self.run_cli(content=stream.getvalue().encode(), config=config, work=work)
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertEqual([{'ligne': '2', 'motif': 'Champ obligatoire absent : ' + field}],
                                 self.rejects(source))
                self.assertIn('Lignes rejetées : 1', self.summary(source))

    def test_other_missing_postal_field_keeps_generic_reason(self):
        config = self.config()
        config['obligatoires'].append('rue')
        rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))
        rows[1][2] = rows[1][4] = ''
        stream = io.StringIO(newline='')
        csv.writer(stream, delimiter=';').writerows(rows)
        result, source = self.run_cli(content=stream.getvalue().encode(), config=config)
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual([{'ligne': '2', 'motif': 'Champ obligatoire absent : rue'},
                          {'ligne': '2', 'motif': 'Adresse postale incomplète'}], self.rejects(source))
        self.assertIn('Lignes rejetées : 1', self.summary(source))

    def test_multiple_defects_count_one_rejected_row(self):
        text = self.clean_bytes().decode().replace('a13-fictif-01@example.org', 'email-invalide').replace('1 rue Imaginaire;', ';', 1)
        result, source = self.run_cli(content=text.encode())
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn('Lignes rejetées : 1', self.summary(source))
        self.assertEqual(2, len(self.rejects(source)))
        self.assertEqual({'2'}, {item['ligne'] for item in self.rejects(source)})

    def test_iban_column_identification_with_quoted_csv_cells(self):
        text = (FIXTURES / 'a13-export-iban-fictif.csv').read_text(encoding='utf-8')
        text = text.replace('Fictif Licorne 01;', '"Fictif Licorne 01";', 1)
        result, source = self.run_cli(content=text.encode())
        self.assert_refused(result, source, 'IBAN suspect : colonne 14')

    def test_iban_suspicious_header_even_with_empty_values(self):
        text = (FIXTURES / 'a13-export-iban-fictif.csv').read_text(encoding='utf-8')
        text = text.replace('IBAN fictif', 'Compte I B A N').replace('ZZ00 0000 0000 0000 0000', '')
        result, source = self.run_cli(content=text.encode())
        self.assert_refused(result, source, 'IBAN suspect : colonne 14')

    def test_iban_inside_invalid_quoted_csv_is_refused_without_leak(self):
        text = self.clean_bytes() + b'"cassure-fictive;ZZ00000000000000000000\n'
        result, source = self.run_cli(content=text)
        self.assert_refused(result, source, 'IBAN suspect')
        self.assertNotIn('ZZ00', result.stdout + result.stderr)

    def test_duplicate_json_keys_are_refused_without_traceback(self):
        # Le fichier de config de ce test est lui aussi hors dépôt.
        config = self.work / 'double.json'
        config.write_text('{"version":1,"version":1}', encoding='utf-8')
        result, source = self.run_cli(extra=('--correspondance', str(config)))
        self.assert_refused(result, source, 'clé en double')
        self.assertNotIn('Traceback', result.stderr)

    def test_invalid_configuration_types_are_refused_without_traceback(self):
        config = self.config()
        config['colonnes'] = []
        result, source = self.run_cli(config=config)
        self.assert_refused(result, source, 'Correspondance')
        self.assertNotIn('Traceback', result.stderr)

    def test_iban_typographic_variants_in_one_unmapped_cell(self):
        for index, marker in enumerate(('ZZ00.0000.0000.0000.0000', 'ZZ00\u200b0000\u200b0000\u200b0000\u200b0000',
                       'ZZ00\u202f0000\u202f0000\u202f0000\u202f0000', 'ZZ00·0000·0000·0000·0000',
                       'ＺＺ００.００００.００００.００００.００００')):
            with self.subTest(marker_type=ascii(marker)[:20]):
                rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))
                rows[0].append('Note')
                for row in rows[1:]: row.append('')
                rows[-1][-1] = marker
                stream = io.StringIO(newline=''); csv.writer(stream, delimiter=';').writerows(rows)
                content = stream.getvalue().encode()
                work = self.work / str(index); work.mkdir()
                result, source = self.run_cli(content=content, work=work)
                self.assert_refused(result, source, 'IBAN suspect : colonne 14')
                self.assertNotIn('ZZ00', result.stdout + result.stderr)
                self.assertEqual(content, source.read_bytes())

    def test_iban_scan_never_joins_two_columns(self):
        rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))
        rows[0].extend(['Note A', 'Note B'])
        for row in rows[1:]: row.extend(['ZZ00', '0000000000000000'])
        stream = io.StringIO(newline=''); csv.writer(stream, delimiter=';').writerows(rows)
        result, _ = self.run_cli(content=stream.getvalue().encode())
        self.assertEqual(0, result.returncode, result.stderr)

    def duplicate_name_address(self):
        rows = list(csv.reader(io.StringIO(self.clean_bytes().decode()), delimiter=';'))[:3]
        rows[2][0] = rows[1][0]; rows[2][2:6] = rows[1][2:6]
        rows[2][1] = 'Autre prenom fictif'
        stream = io.StringIO(newline=''); csv.writer(stream, delimiter=';').writerows(rows)
        return stream.getvalue().encode()

    def test_same_name_address_different_firstname_duplicate_by_default(self):
        result, source = self.run_cli(content=self.duplicate_name_address())
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual([{'ligne': str(n), 'motif': 'Doublon de nom et adresse postale'} for n in (2,3)], self.rejects(source))

    def test_same_name_address_missing_firstname_duplicate_by_default(self):
        rows = list(csv.reader(io.StringIO(self.duplicate_name_address().decode()), delimiter=';'))
        rows[2][1] = ''
        stream = io.StringIO(newline='')
        csv.writer(stream, delimiter=';').writerows(rows)
        result, source = self.run_cli(content=stream.getvalue().encode())
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertEqual([{'ligne': str(n), 'motif': 'Doublon de nom et adresse postale'}
                          for n in (2, 3)], self.rejects(source))

    def test_explicit_firstname_duplicate_option_is_off_by_default(self):
        config = self.config(); config['doublon_prenom_identique'] = True
        result, source = self.run_cli(content=self.duplicate_name_address(), config=config)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], self.rejects(source))

    def test_console_cp1252_or_ascii_does_not_fail_after_outputs(self):
        for encoding in ('cp1252', 'ascii'):
            with self.subTest(encoding=encoding):
                work = self.work / encoding; work.mkdir()
                source = work / 'export.csv'; source.write_bytes(self.clean_bytes())
                result = subprocess.run([sys.executable, str(TOOL), str(source), '--correspondance', str(CONFIG), '--au', '2026-11-25'],
                    capture_output=True, env={**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONDONTWRITEBYTECODE':'1'}, timeout=20)
                self.assertEqual(0, result.returncode, result.stderr.decode(encoding))
                self.assertEqual(b'', result.stderr)
                self.assertNotIn(b'Traceback', result.stdout + result.stderr)
                self.assertIn('Lignes contrôlées : 30', self.summary(source))
                self.assertEqual([], self.rejects(source))

    def test_console_cp1252_or_ascii_refusal_without_traceback_or_outputs(self):
        for encoding in ('cp1252', 'ascii'):
            with self.subTest(encoding=encoding):
                work = self.work / encoding
                work.mkdir()
                source = work / 'export.csv'
                before = (FIXTURES / 'a13-export-iban-fictif.csv').read_bytes()
                source.write_bytes(before)
                result = subprocess.run(
                    [sys.executable, str(TOOL), str(source), '--correspondance', str(CONFIG)],
                    capture_output=True, encoding=encoding,
                    env={**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONDONTWRITEBYTECODE': '1'},
                    timeout=20)
                self.assert_refused(result, source, 'IBAN suspect : colonne 14')
                expected = 'à contrôler'.encode(encoding, errors='backslashreplace').decode(encoding)
                self.assertIn(expected, result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertNotIn('ZZ00', result.stdout + result.stderr)
                self.assertEqual(before, source.read_bytes())

    def test_clean_file_returns_zero_and_thirty_clean_rows(self):
        result, source = self.run_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Lignes contrôlées : 30', self.summary(source))
        self.assertIn('Lignes sans défaut : 30', self.summary(source))
        self.assertEqual([], self.rejects(source))
        self.assertEqual('', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
