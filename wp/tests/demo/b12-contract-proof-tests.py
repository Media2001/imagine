"""16h30 B12 contract: own source equality, exact block, no neighbor seals."""
import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('v', ROOT/'wp/tests/demo/b12-verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
b12 = v.b12

class Contract(unittest.TestCase):
    def test_owned_sources_exclude_whole_shared_bootstrap(self):
        own = b12.contract_sources()
        self.assertNotIn(v.BOOT, own)
        self.assertIn('wp/plugins/imagine-site/IntegrationsCorps.php', own)
        self.assertGreater(len(own), 10)
    def test_current_block_exact(self): self.assertEqual(b12.contract_block()['occurrences'], 1)
    def test_successor_registration_does_not_invalidate_own_block(self):
        raw = (ROOT/v.BOOT).read_bytes()
        self.assertEqual(b12.contract_block(raw + b'\n// Unrelated future lot bootstrap addition.\n'), b12.contract_block(raw))
    def test_removed_own_registration_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes().replace(b12.BLOCK.encode(), b'', 1)
        with self.assertRaisesRegex(AssertionError, 'B12_BOOTSTRAP_CONTRACT'): b12.contract_block(raw)
    def test_changed_own_registration_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes().replace(b'IntegrationsCorps::register();', b'//IntegrationsCorps::register();')
        with self.assertRaisesRegex(AssertionError, 'B12_BOOTSTRAP_CONTRACT'): b12.contract_block(raw)
    def test_duplicated_own_registration_rejected(self):
        raw = (ROOT/v.BOOT).read_bytes() + b12.BLOCK.encode()
        with self.assertRaisesRegex(AssertionError, 'B12_BOOTSTRAP_CONTRACT'): b12.contract_block(raw)
    def test_wrong_owned_source_rejected(self):
        m = {'scope':'imagine-test-demo','ready':True,'sources':copy.deepcopy(b12.contract_sources())}
        m['sources']['wp/plugins/imagine-site/IntegrationsCorps.php'] = '0'*64
        with self.assertRaisesRegex(AssertionError, 'SOURCES'): v.verify_contract(False,m,False)

if __name__ == '__main__': unittest.main(verbosity=2)
