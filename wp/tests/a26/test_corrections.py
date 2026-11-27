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

    def test_missing_form_policy_cannot_silently_shrink_staging_freeze(self):
        r = runner()
        with tempfile.TemporaryDirectory(prefix='a26-form-freeze-', dir=os.environ.get('TMPDIR')) as tmp:
            r.ROOT = Path(tmp)
            (r.ROOT / 'wp/outils/staging').mkdir(parents=True)
            (r.ROOT / 'wp/outils/staging/lib.php').write_bytes(b'fixture-only')
            with self.assertRaisesRegex(RuntimeError, '^A26_MISSING_SOURCE_ROOT$'):
                r.manifest(['wp/outils/staging', 'wp/outils/staging/form-policy.json'])

    def test_legacy_method_mutation_is_exact_and_preserves_other_methods(self):
        spec = importlib.util.spec_from_file_location('a26_html_mutation_test', HERE / 'html_mutation.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        source = (ROOT / 'wp/outils/bascule/a26/Analysis.php').read_bytes()
        legacy = (HERE / 'html-regex-before.txt').read_bytes()
        mutant = m.replace_html_method(source, legacy)
        start, end = source.index(m.START), source.index(m.END)
        self.assertEqual(mutant, source[:start] + legacy + source[end:])
        self.assertNotEqual(mutant, source)
        self.assertIn(b'$resourcePattern', mutant)
        with self.assertRaisesRegex(RuntimeError, '^A26_HTML_MUTATION_TARGET_INVALID$'):
            m.replace_html_method(b'no PHP target', legacy)

    def test_native_counterexamples_are_required_for_both_stores_and_all_selections(self):
        inside = (HERE / 'inside.py').read_text(encoding='utf-8')
        verify = (HERE / 'verify.py').read_text(encoding='utf-8')
        html = (HERE / 'html-unit.php').read_text(encoding='utf-8')
        for name in ('html_quoted_gt_real_youtube', 'html_title_src_no_phantom_vimeo'):
            self.assertIn(name, html)
            self.assertIn(name, inside)
            self.assertIn(name, verify)
        for name in ('html_report_two_counterexamples_red', 'html_last_ten_two_counterexamples_red',
                     'html_last_ten_quoted_gt_and_no_phantom', 'html_source_restored_exactly'):
            self.assertIn(name, inside)
            self.assertIn(name, verify)
        self.assertIn("for storage in ('classic', 'hpos'):", verify)
        self.assertIn("for mode in ('postmeta', 'post_parent', 'taxonomy'):", inside)

    def test_document_points_to_explicit_root_relative_readme(self):
        lines = (ROOT / 'production/A-26/readme-ajout.txt').read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('wp/outils/bascule/a26/README.md', lines[0])
        self.assertEqual(lines[0].count('wp/outils/bascule/a26/README.md'), 1)


if __name__ == '__main__':
    unittest.main()
