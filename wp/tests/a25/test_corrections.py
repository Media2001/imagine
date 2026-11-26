"""Correction wiring contracts only; real PHP/SQL assertions run in parent matrix."""
from pathlib import Path
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

    def test_php_assertion_bank_exercises_roles_not_python_translation(self):
        source = (ROOT / 'wp/tests/a25/unit.php').read_text(encoding='utf-8')
        for name in ('submission_pk_is_entry', 'own_id_submission_reference_is_child',
                     'composite_submission_pk_is_ambiguous', 'unkeyed_submission_is_ambiguous'):
            self.assertIn(name, source)


if __name__ == '__main__':
    unittest.main()
