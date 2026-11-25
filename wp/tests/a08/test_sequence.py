"""Contract tests: doubles cover orchestration only, never native proof."""
import importlib.util
import pathlib
import sys
import unittest
sys.dont_write_bytecode = True


def subject():
    path = pathlib.Path('/subject/a08/sequence.py')
    if not path.exists():
        raise AssertionError('A08 implementation missing')
    spec = importlib.util.spec_from_file_location('sequence', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SequenceTest(unittest.TestCase):
    def test_exact_existing_tools_order_and_no_guard_overrides(self):
        m = subject()
        commands = m.commands(pathlib.Path('/subject'), pathlib.Path('/site'), pathlib.Path('/work'),
                              pathlib.Path('/settings'), pathlib.Path('/update'), pathlib.Path('/clean'),
                              pathlib.Path('/backup'), None, None, 1)
        self.assertEqual(list(commands), ['audit', 'avant', 'mise-a-jour', 'nettoyage', 'apres', 'comparaison'])
        self.assertEqual(commands['audit'], ['php', '/subject/audit', '--wp-path=/site', '--output=/work/audit-1'])
        self.assertIn('--state=/work/a04', commands['mise-a-jour'])
        self.assertIn('--state=/work/a05', commands['nettoyage'])
        self.assertIn('/work/avant-1/non-regression.json', commands['comparaison'])
        self.assertNotIn('--renewal-test', str(commands))
        self.assertNotIn('--skip', str(commands))


if __name__ == '__main__':
    unittest.main()
