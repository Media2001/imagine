"""Contrats C08 hors réseau : la portée est vérifiée avant tout téléversement."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c08


class C08Scope(unittest.TestCase):
    def test_reject_foreign_site_before_upload(self):
        with patch.object(c08.b00, 'request_api', return_value={'slug': 'site-interdit', 'status': 'running'}), \
             patch.object(c08.b00, 'upload') as upload:
            with self.assertRaises(ValueError):
                c08.run(seed=True)
            upload.assert_not_called()

    def test_reject_stopped_site_before_upload(self):
        with patch.object(c08.b00, 'request_api', return_value={'slug': c08.b00.SLUG, 'status': 'stopped'}), \
             patch.object(c08.b00, 'upload') as upload:
            with self.assertRaises(RuntimeError):
                c08.run(seed=True)
            upload.assert_not_called()

    def test_reject_production_environment_before_upload(self):
        with patch.object(c08.b00, 'request_api', return_value={'slug': c08.b00.SLUG, 'status': 'running'}), \
             patch.object(c08.b00, 'wp', return_value={'stdout': '{"environment":"production","demo":"imagine-test-demo"}'}), \
             patch.object(c08.b00, 'upload') as upload:
            with self.assertRaises(RuntimeError):
                c08.run(seed=True)
            upload.assert_not_called()

    def test_credentials_cannot_be_in_repository(self):
        with self.assertRaises(ValueError):
            c08.b00.validate_credentials_path(c08.ROOT / 'production/C-08/secret.json')
        self.assertNotEqual(c08.b00.validate_credentials_path(Path.home() / '.imagine-demo/c08-identifiants.json').parent, c08.ROOT)

    def test_fixture_is_separate_from_b00_manifest(self):
        text = (c08.ROOT / 'wp/outils/demo/c08-seed.php').read_text(encoding='utf-8')
        self.assertIn("update_option('imagine_c08_fixture'", text)
        self.assertNotIn("update_option('imagine_demo_manifest'", text)
        self.assertIn('wp_check_password(', text)
        self.assertIn('wp_update_user(', text)
        for field in ['_imagine_acces_grace_debut', '_imagine_acces_grace_fin', '_subscription_id']:
            self.assertIn(field, text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
