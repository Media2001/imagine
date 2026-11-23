"""Tests B-00 uniquement, sans toucher aux sites de la voie 1."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'wp/outils/demo/construire.py'


def builder():
    spec = importlib.util.spec_from_file_location('b00_builder', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class B00Scope(unittest.TestCase):
    def test_b00_fixed_target_and_outside_credentials(self):
        self.assertTrue(SCRIPT.is_file(), 'Le constructeur B-00 doit exister')
        m = builder()
        self.assertEqual(m.SLUG, 'imagine-test-demo')
        self.assertRaises(ValueError, m.validate_target, 'imagine-autre')
        self.assertRaises(ValueError, m.validate_credentials_path, ROOT / 'secret.json')
        m.validate_credentials_path(Path.home() / '.imagine-demo/identifiants.json')

    def test_b00_busy_retries_three_times_five_minutes(self):
        m = builder()
        self.assertTrue(hasattr(m, 'retry_busy'), 'Les refus de concurrence doivent être gérés')
        calls, delays = [], []
        def operation():
            calls.append(1)
            if len(calls) < 4:
                raise m.StagingBusy()
            return 'created'
        self.assertEqual(m.retry_busy(operation, delays.append), 'created')
        self.assertEqual(delays, [300, 300, 300])
        self.assertEqual(len(calls), 4)
        self.assertRaises(m.StagingBusy, m.retry_busy, lambda: (_ for _ in ()).throw(m.StagingBusy()), delays.append)

    def test_b00_creation_uses_normal_api_and_reuses_exact_target(self):
        m = builder()
        self.assertTrue(hasattr(m, 'ensure_site'), 'Création normale obligatoire')
        calls = []
        def api(method, path, payload=None):
            calls.append((method, path, payload))
            if len(calls) == 1:
                raise HTTPError(path, 404, 'absent', {}, None)
            return {'slug': m.SLUG, 'status': 'running', 'url': 'http://localhost:7999'}
        result = m.ensure_site(api, lambda _: None)
        self.assertEqual(result['slug'], m.SLUG)
        self.assertEqual(calls[1], ('POST', '/api/sites', {'name': m.SLUG, 'template_slug': 'sandbox-wp-minimal', 'php_version': '8.3', 'client_name': None, 'target_domain': None}))
        calls.clear()
        def existing(method, path, payload=None):
            calls.append((method, path))
            return {'slug': m.SLUG, 'status': 'running'}
        m.ensure_site(existing, lambda _: None)
        self.assertEqual(calls, [('GET', '/api/sites/imagine-test-demo')])

    def test_b00_fixture_calendar_and_generated_assets(self):
        m = builder()
        self.assertTrue(hasattr(m, 'fixture_data'), 'Fixture B-00 reproductible obligatoire')
        data = m.fixture_data()
        self.assertEqual(data, m.fixture_data())
        self.assertEqual(len(data['calendar']), 15)
        self.assertEqual(len(data['issues']), 5)
        self.assertEqual([sum(row['sortie'].startswith(str(year)) for row in data['calendar']) for year in [2026, 2027, 2028]], [5, 5, 5])
        self.assertTrue(all(row['cloture'] < row['sortie'] for row in data['calendar']))
        self.assertEqual(m.cover_png('1', '#336699'), m.cover_png('1', '#336699'))
        self.assertTrue(m.cover_png('1', '#336699').startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertTrue(m.dummy_pdf('1').startswith(b'%PDF-1.4'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
