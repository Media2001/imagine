"""Small contract counterexamples through the real readers; no disk mutation/network."""
import sys
sys.dont_write_bytecode = True
import contextlib
import copy
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('finish_contract', ROOT/'wp/outils/demo/b11-c29-contract.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
c = f.contract
LOT = sys.argv.pop() if sys.argv[-1] in ['B11','C29'] else None


class ContractCases:
    def setUp(self):
        self.m = f.manifest(self.lot)
        self.v = f.reader(self.lot)
        self.raw = (ROOT/c.BOOT).read_bytes()
        self.text = c.README.read_text(encoding='utf-8')
        self.owner, self.folder, self.heading, _ = c.config(self.lot)

    def verify(self, manifest=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.v.verify(False, manifest or self.m, False)

    def bytes(self, path, raw):
        original = Path.read_bytes
        return patch.object(Path,'read_bytes',lambda p: raw if p == path else original(p))

    def readme(self, text):
        original = Path.read_text
        return patch.object(Path,'read_text',lambda p,*a,**kw: text if p == c.README else original(p,*a,**kw))

    def test_actual_offline_reader(self):
        self.verify()

    def test_owned_file_mutation_rejected(self):
        path = ROOT/'wp'/self.owner.FILES[0]
        with self.bytes(path,path.read_bytes()+b'\n// OWN MUTATION\n'):
            with self.assertRaisesRegex(AssertionError,'OWNED_SOURCES'):self.verify()

    def test_missing_own_block_rejected(self):
        with self.bytes(ROOT/c.BOOT,self.raw.replace(self.owner.BLOCK.encode(),b'',1)):
            with self.assertRaisesRegex(AssertionError,'BOOTSTRAP_CONTRACT'):self.verify()

    def test_duplicate_own_block_rejected(self):
        with self.bytes(ROOT/c.BOOT,self.raw+self.owner.BLOCK.encode()):
            with self.assertRaisesRegex(AssertionError,'BOOTSTRAP_CONTRACT'):self.verify()

    def test_changed_own_block_rejected(self):
        block = self.owner.BLOCK.encode()
        with self.bytes(ROOT/c.BOOT,self.raw.replace(block,block.replace(b'::register();',b'::register(1);'),1)):
            with self.assertRaisesRegex(AssertionError,'BOOTSTRAP_CONTRACT'):self.verify()

    def test_foreign_registration_does_not_expire_receipt(self):
        foreign = b"\n// FUTURE LOT\nrequire_once __DIR__ . '/FutureLot.php';\nFutureLot::register();\n"
        with self.bytes(ROOT/c.BOOT,self.raw+foreign):self.verify()

    def test_own_readme_mutation_rejected(self):
        with self.readme(self.text.replace(self.heading,self.heading+'\nOWN MUTATION',1)):
            with self.assertRaisesRegex(AssertionError,'README_SECTION'):self.verify()

    def test_missing_readme_section_rejected(self):
        with self.readme(self.text.replace(self.heading,'## FOREIGN HEADING',1)):
            with self.assertRaisesRegex(AssertionError,'README_UNIQUE'):self.verify()

    def test_duplicate_readme_section_rejected(self):
        with self.readme(self.text+'\n'+self.heading+'\nduplicate\n'):
            with self.assertRaisesRegex(AssertionError,'README_UNIQUE'):self.verify()

    def test_foreign_readme_section_does_not_expire_receipt(self):
        with self.readme(self.text+'\n## FUTURE LOT\nforeign section\n'):self.verify()

    def test_no_neighbor_receipt_or_pret_readiness_dependency(self):
        original = Path.read_text
        def read(p,*a,**kw):
            if p.is_relative_to(ROOT/'production') and not p.is_relative_to(ROOT/'production'/self.folder):
                raise AssertionError('NEIGHBOR_READ: '+str(p))
            return original(p,*a,**kw)
        with patch.object(Path,'read_text',read):self.verify()

    def test_evidence_mutation_rejected(self):
        name = next(iter(self.m['evidence']))
        path = ROOT/'production'/self.folder/name
        with self.bytes(path,path.read_bytes()+b' evidence mutation'):
            with self.assertRaisesRegex(AssertionError,'EVIDENCE'):self.verify()


class B11(ContractCases,unittest.TestCase):lot='B11'
class C29(ContractCases,unittest.TestCase):lot='C29'

if __name__ == '__main__':
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in [B11,C29] if LOT in [None,cls.lot])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
