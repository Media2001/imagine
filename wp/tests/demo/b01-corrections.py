"""B01 independent regression tests; run in the isolated offline environment."""
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

class Corrections(unittest.TestCase):
    def test_home_exact_fixture_ids_and_order_reject_intruder_and_permutation(self):
        from b01_expectations import latest_article_ids, home_matches
        manifest = {'demo-2026-t4-ouvert': 45, 'demo-2026-t4-reserve-3': 44,
                    'demo-2026-t4-reserve-2': 43, 'demo-2026-t4-reserve-1': 42,
                    'demo-2026-hs-ouvert': 38}
        fixture = [dict(id=id, key=key, date='2026-01-01 12:00:00') for key,id in manifest.items()]
        expected = latest_article_ids(manifest, fixture)
        self.assertEqual(expected, [45,44,43,42,38])
        self.assertTrue(home_matches([45,44,43,42,38], expected))
        self.assertFalse(home_matches([1,44,43,42,38], expected))
        self.assertFalse(home_matches([44,45,43,42,38], expected))
        self.assertFalse(home_matches([45,44,43,42], expected))
        with self.assertRaises(ValueError):
            latest_article_ids(manifest, fixture + [dict(id=999,key='intruder',date='2026-11-23 12:00:00')])

    def test_semantics_localization_and_stable_navigation_source(self):
        theme = ROOT / 'wp/themes/imagine'
        functions = (theme/'functions.php').read_text(encoding='utf-8')
        self.assertIn("'accueil' =>", functions)
        self.assertIn("wp_date(", functions)
        self.assertIn('Aucun résultat pour votre recherche.', functions)
        self.assertIn('Partenariat', (theme/'archive-imagine_partenaire.php').read_text(encoding='utf-8'))
        self.assertIn('sponsored', functions)
        self.assertIn('Requires at least: 7.0', (theme/'style.css').read_text(encoding='utf-8'))

if __name__ == '__main__':
    unittest.main(verbosity=2)
