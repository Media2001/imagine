"""C12 : contrat des profils, sans réseau ni accès à des secrets."""
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[3]


class C12Profiles(unittest.TestCase):
    def test_profils_decouverte_raccordes_sans_faux_email(self):
        rows = json.loads((ROOT / 'wp/outils/demo/c09-profils.json').read_text(encoding='utf-8'))
        rows = {r['code']: r for r in rows}
        for code in ['V-DEC', 'V-DEC-FIN']:
            with self.subTest(code=code):
                self.assertEqual('créé', rows[code]['etat'])
                self.assertEqual('C12', rows[code].get('decouverte'))
                self.assertIn('fictif', rows[code]['limite'].lower())
        self.assertIn('c12-profils.php', (ROOT / 'wp/outils/demo/c09-seed.php').read_text(encoding='utf-8'))
        self.assertIn('c12-profils.php', (ROOT / 'wp/outils/demo/profils.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
