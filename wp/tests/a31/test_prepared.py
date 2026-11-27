"""Prepared-bank syntax/closed contracts; these do not execute native PHP."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class PreparedTests(unittest.TestCase):
    def test_nested_red_command_compiles(self):
        tree = ast.parse((HERE / 'run.py').read_text(encoding='utf-8'))
        value = next(ast.literal_eval(node.value) for node in ast.walk(tree)
                     if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'mutation' for t in node.targets))
        compile(value, '<prepared-red>', 'exec')

    def test_expected_native_oracles_valid_closed_projection(self):
        e = load('a31_expected_contract', HERE / 'expected.py')
        r = load('a31_report_contract', ROOT / 'wp/outils/bascule/a31/report.py')
        for count in (1, 5):
            data = {'schema': 'imagine-a31-history-v1', 'read_only': True, 'storage': 'classic',
                    'neutralisation': 'observe', 'audit_sha256': '0' * 64, 'counts': e.expected(count)}
            self.assertTrue(r.projection(data, '0' * 64))
            self.assertEqual(sum(row['count'] for row in data['counts']['years']['groups']) + data['counts']['years']['autres'], 10 * count)

    def test_a31_native_guard_codes_not_predecessor(self):
        s = (HERE / 'inside.py').read_text(encoding='utf-8')
        self.assertNotIn("A(?:27|12)", s)

    def test_php_source_nonexecution_marker(self):
        self.assertTrue((HERE / 'unit.php').is_file())
        for file in (ROOT / 'wp/outils/bascule/a31').glob('*.php'):
            self.assertIn('declare(strict_types=1);', file.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
