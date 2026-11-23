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
