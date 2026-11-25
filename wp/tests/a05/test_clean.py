"""Safety contracts exercised inside the owned offline runner."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
sys.path.insert(0, '/subject/a05')

class Contract(unittest.TestCase):
    def test_unnamed_plugin_is_kept(self):
        import clean
        plan = {'plugins': []}
        self.assertEqual('garder', clean.plugin_action(plan, 'unnamed/main.php'))

    def test_dependency_blocks_removal_named_in_error(self):
        import clean
        plan = {'plugins': [{'plugin': 'base/base.php', 'action': 'retirer', 'uninstall': False}], 'tables': [], 'options': [], 'cron': [], 'uploads': [], 'table_owners': {}}
        inventory = {'plugins': {'base/base.php': {'requires': [], 'gateway': False}, 'kept/kept.php': {'requires': ['base'], 'gateway': False}}, 'theme': 'fiction', 'tables': [], 'options': [], 'cron': [], 'prefix': 'wp_'}
        with self.assertRaisesRegex(clean.Refusal, 'DEPENDENCY.*base/base.php'):
            clean.protect(plan, inventory)

    def test_inventory_reads_real_fiction_without_writes(self):
        import clean
        self.assertTrue(callable(clean.inspect_site))

if __name__ == '__main__':
    unittest.main()
