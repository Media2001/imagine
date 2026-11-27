"""B12 correction proof-reader counterexamples; never touches a site."""
import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('b12v', ROOT/'wp/tests/demo/b12-verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class Corrections(unittest.TestCase):
    def green(self): return copy.deepcopy(v.load('correction-green-route-V2.json'))
    def test_current_native_matrix(self): self.assertEqual(v.routes(self.green())['total'], 52)
    def test_pre_fix_red_has_cache_leak_and_attempts(self): self.assertEqual(len(v.routes(v.load('correction-red-route-V2.json'), True)['events']), 2)
    def test_no_restoration_rejected(self):
        r = self.green(); r['business_preserved'] = False
        with self.assertRaisesRegex(AssertionError, 'ROUTE_RESTORATION'): v.routes(r)
    def test_missing_case_rejected(self):
        r = self.green(); d = json.loads(r['native']['stdout']); d['cases'].pop(); r['native']['stdout'] = json.dumps(d)
        with self.assertRaisesRegex(AssertionError, 'ROUTE_MATRIX'): v.routes(r)
    def test_blocked_attempt_not_zero(self):
        r = self.green(); d = json.loads(r['native']['stdout']); d['events'] = [{'blocked': True}]; r['native']['stdout'] = json.dumps(d)
        with self.assertRaisesRegex(AssertionError, 'ROUTE_ZERO'): v.routes(r)
    def test_cached_iframe_not_link(self):
        r = self.green(); d = json.loads(r['native']['stdout']); d['cases'][3]['data']['html'] = '<iframe>stale</iframe>'; r['native']['stdout'] = json.dumps(d)
        with self.assertRaisesRegex(AssertionError, 'ROUTE_LINK_ONLY'): v.routes(r)
    def test_thumbnail_not_link(self):
        r = self.green(); d = json.loads(r['native']['stdout']); d['cases'][3]['data']['thumbnail_url'] = 'https://example.invalid/a.jpg'; r['native']['stdout'] = json.dumps(d)
        with self.assertRaisesRegex(AssertionError, 'ROUTE_LINK_ONLY'): v.routes(r)
    def test_exact_bootstrap_current(self): self.assertTrue(v.bootstrap()['B12_registration_exact'])
    def test_unrelated_bootstrap_byte_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes()
        with self.assertRaisesRegex(AssertionError, 'CURRENT_BOOTSTRAP'): v.bootstrap(raw + b'\n')
    def test_C29_block_changed_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes().replace(b'ContactBrevo::register();', b'//ContactBrevo::register();')
        with self.assertRaisesRegex(AssertionError, 'C29_EXACT_BLOCK'): v.bootstrap(raw)
    def test_B12_registration_changed_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes().replace(b'IntegrationsCorps::register();', b'//IntegrationsCorps::register();')
        with self.assertRaisesRegex(AssertionError, 'B12_EXACT_REGISTRATION'): v.bootstrap(raw)

if __name__ == '__main__': unittest.main(verbosity=2)
