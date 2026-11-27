"""Correction contracts only: PHP/native execution remains a separate parent gate."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def runner():
    spec = importlib.util.spec_from_file_location('a26_corrections_runner', HERE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CorrectionsTests(unittest.TestCase):
    def test_native_attribute_reader_no_html_regex_fallback(self):
        source = (ROOT / 'wp/outils/bascule/a26/Analysis.php').read_text(encoding='utf-8')
        method = source.split('public static function htmlUrls(', 1)[1].split('public static function emptyCounts(', 1)[0]
        self.assertIn('new \\WP_HTML_Tag_Processor(', method)
        self.assertIn('->get_attribute(', method)
        self.assertNotIn('$resourcePattern', method)
        self.assertNotIn('$attributePattern', method)

    def test_form_policy_is_mandatory_frozen_dependency(self):
        r = runner()
        key = 'wp/outils/staging/form-policy.json'
        self.assertIn(key, r.DEPS)
        self.assertIn(key, r.manifest(r.DEPS))

    def test_document_points_to_explicit_root_relative_readme(self):
        lines = (ROOT / 'production/A-26/readme-ajout.txt').read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('wp/outils/bascule/a26/README.md', lines[0])
        self.assertEqual(lines[0].count('wp/outils/bascule/a26/README.md'), 1)


if __name__ == '__main__':
    unittest.main()
