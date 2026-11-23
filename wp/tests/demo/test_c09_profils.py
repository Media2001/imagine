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

    def test_fusion_refuse_identifiants_corrompus_sans_reparation(self):
        import profils
        for account in [{'login': 'AUTRE', 'password': 'x' * 32}, {'login': 'a-carte', 'password': 'court'}]:
            with self.subTest(account=account['login']), self.assertRaises(ValueError):
                profils.merge_credentials({'c09_accounts': {'A-CARTE': account}})

    def test_refus_cible_avant_tout_transport(self):
        import profils
        from unittest.mock import patch
        with patch.object(profils.b00, 'request_api', side_effect=AssertionError('Transport interdit')) as transport:
            for target in ['imagine-test-autre', 'production', None, 'imagine-test-demo/../autre']:
                with self.assertRaises(ValueError):
                    profils.run(slug=target)
            transport.assert_not_called()

    def test_http_interdit_redirections_hors_demo(self):
        spec = importlib.util.spec_from_file_location('http_c09', Path(__file__).with_name('c09-http.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for url in ['https://example.org', 'http://192.168.129.32:8086/', 'http://localhost:7000/', 'https://192.168.129.32:8085/']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                module.OnlyDemoRedirect().redirect_request(None, None, 302, '', {}, url)
        with self.assertRaises(ValueError):
            module.fetch(None, '//example.org/')

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
