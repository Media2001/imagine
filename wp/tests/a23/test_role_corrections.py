"""A23 correction contracts; PHP execution is a separate, real parent gate.

These source contracts do not claim to execute WordPress or the PHP adapter.
The independent role-probe.php bank and native receipts provide that proof.
"""
import ast
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


def source(relative):
    return (ROOT / relative).read_text(encoding='utf-8')


class RoleCorrectionTests(unittest.TestCase):
    def test_role_definitions_used_before_user_capabilities(self):
        php = source('wp/outils/bascule/a23/Inventory.php')
        self.assertIn('foreach (wp_roles()->roles as $role => $definition)', php)
        self.assertIn('\\Imagine\\AccountSecurity\\Inventory::management($definition[\'capabilities\'])', php)
        self.assertIn('array_intersect($user->roles, $managementRoles)', php)
        self.assertIn('\\Imagine\\AccountSecurity\\Inventory::management($user->allcaps)', php)
        self.assertLess(php.index('foreach (wp_roles()->roles'), php.index('new \\WP_User'))

    def test_unsafe_management_role_has_closed_refusal(self):
        php = source('wp/outils/bascule/a23/Inventory.php')
        self.assertIn("'/\\A[a-zA-Z_][a-zA-Z0-9_-]{0,99}\\z/D'", php)
        self.assertIn("throw new \\RuntimeException('A23_ROLE_IDENTIFIER_UNSAFE')", php)
        allowed = json.loads(source('wp/outils/bascule/a23/refusals.json'))
        self.assertIn('A23_ROLE_IDENTIFIER_UNSAFE', allowed)

    def test_native_seed_proves_masked_and_multiple_roles(self):
        seed = source('wp/tests/a23/seed.php')
        self.assertIn("add_cap('edit_users', false)", seed)
        self.assertIn("add_role('a23_operator')", seed)
        self.assertIn('A23_ROLE_FIXTURES ', seed)
        self.assertIn("'negative_override'", seed)
        self.assertIn("'multi_role'", seed)
        inside = source('wp/tests/a23/inside.py')
        for name in ('role_negative_override_fixture', 'role_multi_management_fixture',
                     'role_negative_override_excluded', 'role_multi_management_excluded',
                     'role_private_values_absent'):
            self.assertIn("':" + name + "'", inside)

    def test_verifier_requires_new_native_cases(self):
        spec = importlib.util.spec_from_file_location('a23_verify_roles', ROOT / 'wp/tests/a23/verify.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        # Inspect the actual required list consumed for each console/storage.
        tree = ast.parse(source('wp/tests/a23/verify.py'))
        literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        for name in ('role_negative_override_fixture', 'role_multi_management_fixture',
                     'role_negative_override_excluded', 'role_multi_management_excluded',
                     'role_private_values_absent'):
            self.assertIn(name, literals)
        self.assertIn('unsafe_management_role', verifier.CHANNELS)

    def test_role_bank_is_run_without_wordpress_in_own_process(self):
        runner = source('wp/tests/a23/run.py')
        self.assertIn("'/opt/a23/role-probe.php'", runner)
        self.assertIn("'role-definitions.json'", runner)
        self.assertIn("'role_definitions_pure'", runner)


if __name__ == '__main__':
    unittest.main()
