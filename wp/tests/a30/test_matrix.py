"""Matrix evidence contracts; never execute Docker, WSL or native PHP."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from temp_support import temporary_directory

HERE = Path(__file__).resolve().parent


def matrix_module():
    spec = importlib.util.spec_from_file_location('a30_matrix_contract', HERE / 'matrix.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MatrixTests(unittest.TestCase):
    def test_clean_environment_discards_inherited_tmpdir_and_sets_windows_scratch(self):
        matrix = matrix_module()
        with temporary_directory('a30-matrix-env-') as scratch:
            with patch.dict(os.environ, {'TMPDIR': 'poison-inherited', 'TEMP': 'poison-temp', 'TMP': 'poison-tmp'}):
                env = matrix.clean_environment('cp1252', '0', scratch)
            self.assertFalse(any(key.upper() == 'TMPDIR' for key in env))
            self.assertEqual(str(Path(scratch).resolve()), env['TEMP'])
            self.assertEqual(env['TEMP'], env['TMP'])
            self.assertEqual(('cp1252', '0', '1'),
                             tuple(env[k] for k in ('PYTHONIOENCODING', 'PYTHONUTF8', 'PYTHONDONTWRITEBYTECODE')))

    def test_clean_environment_refuses_repository_before_any_write(self):
        matrix = matrix_module()
        with temporary_directory('a30-matrix-fake-') as scratch:
            repo = Path(scratch) / 'repo'; repo.mkdir()
            with self.assertRaisesRegex(RuntimeError, 'A30_TEST_TEMP_IN_REPOSITORY'):
                matrix.clean_environment('utf-8', '1', repo, repo=repo)
            self.assertEqual([], list(repo.iterdir()))

    def test_result_counts_come_from_exact_real_unittest_summary(self):
        matrix = matrix_module()
        good = 'test_case ... ok\r\n\r\nRan 37 tests in 0.018s\r\n\r\nOK\r\n'
        row = matrix.test_result(good, 0, 37)
        self.assertEqual(37, row['tests_run'])
        self.assertTrue(row['all_pass'])
        self.assertEqual((0, 0, 0), tuple(row[k] for k in ('failures', 'errors', 'skipped')))
        for text, code, discovered in [(good, 1, 37), (good, 0, 38), ('OK\n', 0, 37),
                                       (good + good, 0, 37),
                                       ('Ran 37 tests in 0.1s\n\nFAILED (errors=22)\n', 1, 37),
                                       ('Ran 37 tests in 0.1s\n\nOK (skipped=1)\n', 0, 37)]:
            with self.subTest(text=text, code=code, discovered=discovered):
                self.assertFalse(matrix.test_result(text, code, discovered)['all_pass'])

    def test_environment_requires_explicit_unset_real_console_and_standard_temp(self):
        matrix = matrix_module()
        with temporary_directory('a30-matrix-probe-') as scratch:
            env = {'platform': 'win32', 'stdout': 'cp1252', 'stderr': 'cp1252',
                   'utf8_mode': 0, 'TMPDIR_present': False, 'TMPDIR': None,
                   'TEMP': scratch, 'TMP': scratch, 'tempdir': scratch, 'suite_discovered': 33}
            self.assertTrue(matrix.environment_valid(env, 'cp1252', 0, scratch))
            for key, value in [('TMPDIR_present', True), ('TMPDIR', 'inherited'), ('stdout', 'utf-8'),
                               ('stderr', 'utf-8'), ('utf8_mode', 1), ('suite_discovered', 0),
                               ('TEMP', str(HERE)), ('TMP', str(HERE)), ('tempdir', str(HERE))]:
                with self.subTest(key=key):
                    self.assertFalse(matrix.environment_valid({**env, key: value}, 'cp1252', 0, scratch))


if __name__ == '__main__':
    unittest.main(verbosity=2)
