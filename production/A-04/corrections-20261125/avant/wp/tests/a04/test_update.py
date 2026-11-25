"""A04 standard-library unit tests (no PHP on host, no site inputs)."""
import importlib.machinery
import importlib.util
import json
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

class StateTests(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader('a04_state_tests', str(ROOT / 'mettre-a-jour'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.module = importlib.util.module_from_spec(spec)
        loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory(prefix='a04-real-state-')
        self.addCleanup(self.temp.cleanup)
        self.directory = pathlib.Path(self.temp.name)
        self.state = {'schema': 'imagine-a04-state-v1', 'plan_sha256': 'a' * 64,
                      'site': '/fiction', 'config_sha256': 'b' * 64,
                      'steps': {'core': {'phase': 'verified'}}, 'events': []}

    def test_durable_state_roundtrip_preserves_verified_checkpoint(self):
        path = self.directory / 'etat.json'
        self.module.atomic_json(path, self.state)
        readback = self.module.load_json(path)
        self.assertEqual(readback, self.state)
        self.assertEqual(self.module.validate_state(readback, 'a' * 64, '/fiction', 'b' * 64), self.state)
        self.assertEqual(list(self.directory.iterdir()), [path])

    def test_failed_atomic_replace_keeps_existing_destination_and_cleans_temp(self):
        path = self.directory / 'etat.json'
        path.mkdir()
        sentinel = path / 'unchanged.txt'
        sentinel.write_text('existing checkpoint destination')
        with self.assertRaises(OSError):
            self.module.atomic_json(path, self.state)
        self.assertEqual(sentinel.read_text(), 'existing checkpoint destination')
        self.assertEqual(list(self.directory.iterdir()), [path])

    def test_resume_refuses_a_different_plan(self):
        with self.assertRaisesRegex(self.module.Refusal, '^A04_STATE$'):
            self.module.validate_state(self.state, 'c' * 64, '/fiction', 'b' * 64)

    def test_resume_refuses_a_different_site(self):
        with self.assertRaisesRegex(self.module.Refusal, '^A04_STATE$'):
            self.module.validate_state(self.state, 'a' * 64, '/other-fiction', 'b' * 64)

    def test_resume_refuses_a_changed_wp_config(self):
        with self.assertRaisesRegex(self.module.Refusal, '^A04_STATE$'):
            self.module.validate_state(self.state, 'a' * 64, '/fiction', 'c' * 64)

    def test_corrupt_checkpoint_is_not_silently_reinitialized(self):
        path = self.directory / 'etat.json'
        path.write_text('{interrupted')
        with self.assertRaises(json.JSONDecodeError):
            self.module.load_json(path)
        self.assertEqual(path.read_text(), '{interrupted')

if __name__ == '__main__':
    unittest.main(verbosity=2)
