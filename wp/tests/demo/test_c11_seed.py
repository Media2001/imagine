"""Contrat anti-réintroduction de l'adresse publique au rejeu B00."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class ProtectedSeed(unittest.TestCase):
    def test_pdf_sources_use_private_transport(self):
        source = (ROOT / 'wp/outils/demo/construire.py').read_text(encoding='utf-8')
        self.assertTrue("remote('pdf-source', name=issue['slug'] + '.pdf'" in source, 'Transport PDF privé manquant')
        self.assertFalse("upload('imagine-demo-build/assets/' + issue['slug'] + '.pdf'" in source, 'Source PDF exposée dans les assets')


if __name__ == '__main__':
    unittest.main()
