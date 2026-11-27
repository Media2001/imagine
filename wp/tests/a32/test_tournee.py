"""A32 contracts: exact documented argv and closed orchestration."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


def load():
    path = ROOT / 'wp/outils/bascule/tournee/tournee.py'
    spec = importlib.util.spec_from_file_location('tournee', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TourneeTests(unittest.TestCase):
    def test_exact_commands_and_closed_inventory(self):
        self.assertTrue((ROOT / 'wp/outils/bascule/tournee/tournee.py').is_file(), 'A32 implementation absent')
        m = load()
        entries = m.entries()
        self.assertEqual([e['lot'] for e in entries], ['A10', 'A11', 'A12', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A23', 'A24', 'A25'])
        for entry in entries:
            self.assertIn(entry['command'], m.documented_commands(ROOT / entry['readme']))
            argv = m.command(entry, Path('/operator/site'), Path('/operator/report/audit/audit.json'), Path('/operator/map.json'), Path('/operator/report/out'))
            import shlex
            documented = shlex.split(entry['command'])
            self.assertEqual(len(argv), len(documented))
            self.assertEqual([x.split('=')[0] for x in argv[2:]], [x.split('=')[0] for x in documented[2:]])


if __name__ == '__main__':
    unittest.main()
