"""Local B04 evidence-contract regressions; never contacts a site."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('b04_http_contract', Path(__file__).with_name('b04-http.py'))
b04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b04)

class MarkersTest(unittest.TestCase):
    def inventory(self, markers):
        return {'issues': {'witness': {'articles': [{'id': 1, 'markers': markers}]}}}

    def test_empty_catalogue_or_issue_cannot_pass(self):
        for inventory in [{'issues': {}}, {'issues': {'witness': {'articles': []}}}]:
            with self.assertRaises(AssertionError):
                b04.require_private_markers(inventory)

    def test_empty_markers_cannot_prove_sealing(self):
        with self.assertRaises(AssertionError):
            b04.require_private_markers(self.inventory([]))

    def test_blank_markers_cannot_prove_sealing(self):
        for value in ['', ' ', None, 0]:
            with self.subTest(marker=value), self.assertRaises(AssertionError):
                b04.require_private_markers(self.inventory([value]))

    def test_real_marker_required_for_every_article(self):
        inventory = self.inventory(['Private fictional body'])
        b04.require_private_markers(inventory)
        inventory['issues']['witness']['articles'].append({'id': 2, 'markers': []})
        with self.assertRaises(AssertionError):
            b04.require_private_markers(inventory)

if __name__ == '__main__':
    unittest.main(verbosity=2)
