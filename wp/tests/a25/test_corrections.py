"""Correction wiring contracts only; real PHP/SQL assertions run in parent matrix."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[3]


class CorrectionWiringTests(unittest.TestCase):
    def test_column_role_not_column_name_drives_unknown_tables(self):
        source = (ROOT / 'wp/outils/bascule/a25/Inventory.php').read_text(encoding='utf-8')
        self.assertIn('SELECT COLUMN_NAME,COLUMN_KEY FROM information_schema.COLUMNS', source)
        self.assertIn('self::formStructure($metadata)', source)
        self.assertNotIn("&& !in_array('submission_id', $columns, true)", source)

    def test_native_primary_key_and_real_child_fixtures_are_wired(self):
        source = (ROOT / 'wp/tests/a25/seed.php').read_text(encoding='utf-8')
        self.assertIn('a25_submission_entries (submission_id bigint PRIMARY KEY', source)
        self.assertIn('a25_submission_details (id bigint PRIMARY KEY, submission_id bigint', source)
        self.assertIn('for ($i = 1; $i <= 5; $i++)', source)
        inside = (ROOT / 'wp/tests/a25/inside.py').read_text(encoding='utf-8')
        self.assertIn(':submission_pk_five_child_excluded', inside)
        self.assertIn(':ambiguous_coverage_never_zero', inside)

    def test_official_quote_and_date_row_are_not_invented_prose(self):
        evidence = json.loads((ROOT / 'production/A-25/fluentforms-source.json').read_text(encoding='utf-8'))
        sources = (ROOT / 'production/A-25/SOURCES.md').read_text(encoding='utf-8')
        self.assertEqual(evidence['url'], 'https://developers.fluentforms.com/database/')
        self.assertEqual(evidence['section'], 'fluentform_submissions')
        self.assertEqual(evidence['exact_sentence'], 'Storing the form submissions')
        self.assertEqual(evidence['exact_date_row'], 'created_at\ttimestamp NULL\t')
        self.assertIn(evidence['exact_sentence'], sources)
        self.assertIn('created_at\\ttimestamp NULL', sources)

    def test_native_neutralisation_setup_keeps_the_new_fixture_tables_explicitly(self):
        source = (ROOT / 'wp/tests/a25/neutralise.php').read_text(encoding='utf-8')
        for name in ('wp_a25_submission_entries', 'wp_a25_submission_details'):
            self.assertIn("'" + name + "' => ['action' => 'garder']", source)
        for name in ('submission_pk_messages_preserved', 'submission_child_rows_preserved'):
            self.assertIn(name, source)

    def test_php_assertion_bank_exercises_roles_not_python_translation(self):
        source = (ROOT / 'wp/tests/a25/unit.php').read_text(encoding='utf-8')
        for name in ('submission_pk_is_entry', 'own_id_submission_reference_is_child',
                     'composite_submission_pk_is_ambiguous', 'unkeyed_submission_is_ambiguous'):
            self.assertIn(name, source)


if __name__ == '__main__':
    unittest.main()
