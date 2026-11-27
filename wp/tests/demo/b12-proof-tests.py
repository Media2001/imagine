"""B12 proof-reader counterexamples, no site or network."""
import sys
sys.dont_write_bytecode=True
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('b12_verify',ROOT/'wp/tests/demo/b12-verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class ProofTests(unittest.TestCase):
    def green(self):return copy.deepcopy(v.load('native-reception-V2.json'))
    def test_reference_native(self):self.assertFalse(v.native(self.green(),False)['mutant'])
    def test_attempt_even_blocked_is_not_zero(self):
        r=self.green();d=json.loads(r['native']['stdout']);d['events']=[{'blocked':True,'phase':'save_0'}];r['native']['stdout']=json.dumps(d)
        with self.assertRaisesRegex(AssertionError,'ZERO_ATTEMPTS'):v.native(r,False)
    def test_empty_checks_not_success(self):
        r=self.green();d=json.loads(r['native']['stdout']);d['checks']={};d['total']=0;r['native']['stdout']=json.dumps(d)
        with self.assertRaisesRegex(AssertionError,'CHECKS'):v.native(r,False)
    def test_missing_matrix_not_success(self):
        r=self.green();d=json.loads(r['native']['stdout']);del d['checks']['matrix_apercu_lien_1_1'];d['total']-=1;r['native']['stdout']=json.dumps(d)
        with self.assertRaisesRegex(AssertionError,'MATRIX_INCOMPLETE'):v.native(r,False)
    def test_restoration_required(self):
        r=self.green();r['business_preserved']=False
        with self.assertRaisesRegex(AssertionError,'RESTORATION'):v.native(r,False)
    def test_mutant_without_render_attempt_is_not_witness(self):
        r=copy.deepcopy(v.load('mutation-reception-V2.json'));d=json.loads(r['native']['stdout']);d['events']=[e for e in d['events'] if not e['phase'].startswith('render')];r['native']['stdout']=json.dumps(d)
        with self.assertRaisesRegex(AssertionError,'MUTATION_SURFACES'):v.native(r,True)
if __name__=='__main__':unittest.main(verbosity=2)
