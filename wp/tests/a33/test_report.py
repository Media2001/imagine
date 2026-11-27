"""A33 strict publication schema, executable without PHP on Windows."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


class ReportTests(unittest.TestCase):
    def test_schema_exists(self):
        self.assertTrue((ROOT / 'wp/outils/bascule/a33/report.py').is_file(), 'A33 publication validator is missing')


if __name__ == '__main__':
    unittest.main()
