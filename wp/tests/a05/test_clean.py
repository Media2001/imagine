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

if __name__ == '__main__':
    unittest.main()
