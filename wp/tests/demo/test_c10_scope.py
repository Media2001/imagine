"""Garde C10 : ne jamais déployer sur un autre site ou une autre URL."""
import importlib.util
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10


class ScopeTest(unittest.TestCase):
    def run_guard(self, slug='imagine-test-demo', status='running', url='http://192.168.129.32:8085', env='local', demo='imagine-test-demo'):
        import json
        with patch.object(c10.b00, 'request_api', return_value={'slug':slug,'status':status,'url':url}), patch.object(c10.b00, 'wp', return_value={'stdout':json.dumps({'environment':env,'demo':demo})}):
            return c10.guard()

    def test_guard_exists(self):
        self.assertTrue(hasattr(c10, 'guard'), 'C10 doit vérifier sa propre URL exacte avant chaque écriture')

    def test_expected_target(self):
        if not hasattr(c10, 'guard'): self.skipTest('garde absente')
        self.assertEqual(self.run_guard()[0]['slug'], 'imagine-test-demo')

    def test_denials(self):
        if not hasattr(c10, 'guard'): self.skipTest('garde absente')
        for override in [{'slug':'imagine-test-autre'},{'status':'stopped'},{'url':'https://autre.invalid'},
                         {'env':'production'},{'demo':'autre'}]:
            with self.subTest(override=override), self.assertRaises((ValueError,RuntimeError)):
                self.run_guard(**override)

    def test_deployment_allowlist(self):
        self.assertEqual(len(c10.FILES), 6)
        self.assertEqual([name for name in c10.FILES if not name.startswith('plugins/imagine-pilotage/')],
                         ['plugins/imagine-site/Paywall.php'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
