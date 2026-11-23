"""C09 : tests locaux sans transport ni accès à d'autres sites."""
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[2] / 'outils/demo'
sys.path.insert(0, str(TOOLS))


class C09Scope(unittest.TestCase):
    def test_cible_exacte_et_prefixe(self):
        self.assertTrue((TOOLS / 'profils.py').is_file(), 'Le script C09 manque')
        spec = importlib.util.spec_from_file_location('profils', TOOLS / 'profils.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.validate_target('imagine-test-demo')
        for slug in ['production', 'imagine-test-autre', 'imagine-test-demo-x', 'IMAGINE-test-demo', '', '../imagine-test-demo']:
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                module.validate_target(slug)

    def test_identifiants_fusion_sans_ecraser_b00_c08(self):
        import profils
        self.assertTrue(hasattr(profils, 'merge_credentials'), 'Fusion privée manquante')
        original = {'admin_password': 'fictif-test-non-secret', 'c08_accounts': {'actif': {'login': 'imagine-c08-actif'}}}
        merged = profils.merge_credentials(original)
        self.assertEqual(original['admin_password'], merged['admin_password'])
        self.assertEqual(original['c08_accounts'], merged['c08_accounts'])
        self.assertEqual(27, len(merged['c09_accounts']))
        again = profils.merge_credentials(merged)
        self.assertEqual(merged, again)
        self.assertNotIn('c09_accounts', original)
        for code, account in merged['c09_accounts'].items():
            self.assertEqual(code.lower(), account['login'])
            self.assertGreaterEqual(len(account['password']), 24)

    def test_identifiants_dans_depot_refuses(self):
        import profils
        with self.assertRaises(ValueError):
            profils.b00.validate_credentials_path(profils.b00.ROOT / 'production/C-09/identifiants.json')

    def test_catalogue_trente_sans_faux_comptes_visiteurs(self):
        import profils
        self.assertTrue(hasattr(profils, 'catalogue'), 'Catalogue C09 manquant')
        rows = profils.catalogue()
        self.assertEqual(30, len(rows))
        self.assertEqual(30, len({row['code'] for row in rows}))
        for row in rows:
            self.assertIn(row['etat'], ['créé', 'partiel', 'impossible'])
            self.assertEqual(row['login'], row['code'].lower() if row['compte'] else None)
            self.assertTrue(row['limite'] if row['etat'] != 'créé' else True)
        self.assertEqual({'V-ANON', 'V-ROBOT', 'V-FAUX'}, {row['code'] for row in rows if not row['compte']})


if __name__ == '__main__':
    unittest.main()
