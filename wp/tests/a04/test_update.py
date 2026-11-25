"""A04 standard-library unit tests (no PHP on host, no site inputs)."""
import importlib.machinery
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path('/subject') if pathlib.Path('/subject').is_dir() else pathlib.Path(__file__).resolve().parents[2] / 'outils/bascule'

class PlanTests(unittest.TestCase):
    def test_missing_updater_is_not_a_valid_plan(self):
        path = ROOT / 'mettre-a-jour'
        self.assertTrue(path.is_file(), 'A04_UPDATER_MISSING')
        loader = importlib.machinery.SourceFileLoader('a04_update', str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        with self.assertRaisesRegex(module.Refusal, 'A04_PLAN'):
            module.validate_plan({})

if __name__ == '__main__':
    unittest.main(verbosity=2)
