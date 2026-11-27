"""Scratch-only regression contracts, independent of the four fixture classes."""
import ast
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class TempSupportTests(unittest.TestCase):
    def helper(self):
        return importlib.import_module('temp_support')

    def test_unset_tmpdir_uses_real_python_standard_temp(self):
        helper = self.helper()
        env = os.environ.copy()
        env.pop('TMPDIR', None)
        # These are real fresh Python processes; tempfile's cache is not inherited.
        for encoding, mode in [('utf-8', '1'), ('cp1252', '0')]:
            with self.subTest(encoding=encoding):
                env.update(PYTHONIOENCODING=encoding, PYTHONUTF8=mode,
                           PYTHONDONTWRITEBYTECODE='1')
                probe = ("import os,json,tempfile;from pathlib import Path;"
                         "from temp_support import temporary_directory;"
                         "t=temporary_directory('a30-temp-probe-');"
                         "print(json.dumps({'unset':'TMPDIR' not in os.environ,"
                         "'standard':tempfile.gettempdir(),'actual':str(Path(t.name).parent)}));"
                         "t.cleanup()")
                p = subprocess.run([sys.executable, '-B', '-c', probe], cwd=HERE,
                                   env=env, capture_output=True, timeout=30)
                self.assertEqual(0, p.returncode, p.stderr)
                result = json.loads(p.stdout.decode(encoding))
                self.assertTrue(result['unset'])
                self.assertEqual(Path(result['standard']).resolve(), Path(result['actual']).resolve())
                helper.assert_outside_repo(result['actual'])

    def test_optional_tmpdir_override_and_empty_fallback(self):
        helper = self.helper()
        from unittest.mock import patch
        with helper.temporary_directory('a30-override-root-') as outside:
            with patch.dict(os.environ, {'TMPDIR': outside}):
                with helper.temporary_directory('a30-override-child-') as child:
                    self.assertEqual(Path(outside).resolve(), Path(child).resolve().parent)
            with patch.dict(os.environ, {'TMPDIR': ''}):
                with helper.temporary_directory('a30-empty-') as child:
                    self.assertEqual(Path(tempfile.gettempdir()).resolve(), Path(child).resolve().parent)

    def test_repository_root_and_descendant_refused_before_creation(self):
        helper = self.helper()
        from unittest.mock import patch
        with helper.temporary_directory('a30-fake-repo-') as outside:
            fake_repo = Path(outside) / 'repo'; fake_repo.mkdir()
            nested = fake_repo / 'nested'; nested.mkdir()
            before = sorted(p.relative_to(fake_repo).as_posix() for p in fake_repo.rglob('*'))
            for candidate in (fake_repo, nested, nested / '..'):
                with self.subTest(candidate=str(candidate)):
                    with self.assertRaisesRegex(RuntimeError, 'A30_TEST_TEMP_IN_REPOSITORY'):
                        helper.assert_outside_repo(candidate, repo=fake_repo)
                    with patch.dict(os.environ, {'TMPDIR': str(candidate)}):
                        with self.assertRaisesRegex(RuntimeError, 'A30_TEST_TEMP_IN_REPOSITORY'):
                            helper.temporary_directory('must-not-exist-', repo=fake_repo)
            self.assertEqual(before, sorted(p.relative_to(fake_repo).as_posix() for p in fake_repo.rglob('*')))

    def test_all_four_fixture_classes_use_one_helper(self):
        for name in ('test_core.py', 'test_cli.py', 'test_boundary.py', 'test_verify.py'):
            with self.subTest(name=name):
                tree = ast.parse((HERE / name).read_text(encoding='utf-8'))
                imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                           and n.module == 'temp_support']
                self.assertTrue(any(a.name == 'temporary_directory' for n in imports for a in n.names))
                calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
                self.assertTrue(any(isinstance(n.func, ast.Name) and n.func.id == 'temporary_directory' for n in calls))
                self.assertFalse(any(isinstance(n.func, ast.Attribute) and n.func.attr == 'TemporaryDirectory' for n in calls))


if __name__ == '__main__':
    unittest.main(verbosity=2)
