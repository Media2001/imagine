"""Owned replay contracts; no WSL, Docker, PHP, or network call here."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ReplayContracts(unittest.TestCase):
    def test_manifests_hash_real_sources(self):
        r = load('a26_runner_test', HERE / 'run.py')
        manifest = r.manifest(r.OWN)
        key = 'wp/outils/bascule/a26/Analysis.php'
        self.assertEqual(manifest[key], hashlib.sha256((ROOT / key).read_bytes()).hexdigest())
        self.assertIn('wp/outils/bascule/a16/Mapping.php', r.manifest(r.DEPS))
        self.assertIn('wp/outils/bascule/stream_guard.py', r.manifest(r.DEPS))

    def test_missing_and_empty_sources_are_not_a_green_empty_manifest(self):
        r = load('a26_missing_source_test', HERE / 'run.py')
        with tempfile.TemporaryDirectory(prefix='a26-manifest-', dir=os.environ.get('TMPDIR')) as tmp:
            r.ROOT = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, '^A26_MISSING_SOURCE_ROOT$'):
                r.manifest(['missing'])
            (r.ROOT / 'empty').mkdir()
            with self.assertRaisesRegex(RuntimeError, '^A26_EMPTY_SOURCE_ROOT$'):
                r.manifest(['empty'])

    def test_unittest_summary_crlf_and_zero_discovery(self):
        m = load('a26_matrix_test', HERE / 'matrix.py')
        self.assertEqual(m.python_summary('Ran 12 tests in 0.5s\r\n\r\nOK\r\n', 0), {'tests_run': 12, 'all_pass': True})
        self.assertFalse(m.python_summary('Ran 0 tests in 0.0s\n\nOK\n', 0)['all_pass'])
        self.assertFalse(m.python_summary('Ran 12 tests in 0.0s\n\nFAILED\n', 1)['all_pass'])

    def test_every_declared_native_channel_has_a_case(self):
        # A plan/discovery contract, never a claim that the native cases have run.
        text = (HERE / 'inside.py').read_text(encoding='utf-8')
        for case in ('direct_stdout', 'direct_stderr', 'display_early_exit', 'shutdown_display',
                     'shutdown_markdown', 'shutdown_extra_string', 'shutdown_valid_counts_and_markdown',
                     'actual_unchanged_import_executed', 'neutralised_all_tables_files_identical',
                     'last_ten_exact_no_oldest_no_orphans'):
            self.assertIn(case, text)
        self.assertIn("for mode in ('postmeta', 'post_parent', 'taxonomy'):", text)
        self.assertIn('red_green.py', (HERE / 'run.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
