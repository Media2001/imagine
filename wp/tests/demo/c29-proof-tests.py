"""C29 proof-reader counterexamples; no demo, browser or network."""
import sys
sys.dont_write_bytecode=True
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('c29_proof',ROOT/'production/C-29/verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class ProofTests(unittest.TestCase):
    def native(self):return copy.deepcopy(v.load('native-reception-V2.json'))
    def http(self):return copy.deepcopy(v.load('http-reception-V2.json'))
    def alter(self,change):
        r=self.native();d=json.loads(r['native']['stdout']);change(d);r['native']['stdout']=json.dumps(d);return r
    def test_real_native(self):self.assertEqual(27,len(v.native_receipt(self.native())['profils']))
    def test_missing_profile(self):
        r=self.alter(lambda d:d['profils'].pop('A-CARTE'))
        with self.assertRaisesRegex(AssertionError,'PROFILES'):v.native_receipt(r)
    def test_no_positive_consent_witness(self):
        r=self.alter(lambda d:d['mutation'].update(positive=[]))
        with self.assertRaisesRegex(AssertionError,'CONSENT_WITNESS'):v.native_receipt(r)
    def test_blocked_attempt_is_not_zero(self):
        r=self.alter(lambda d:d['outgoing'].append('blocked'))
        with self.assertRaisesRegex(AssertionError,'NATIVE_ZERO'):v.native_receipt(r)
    def test_native_restoration_required(self):
        r=self.native();r['business_preserved']=False
        with self.assertRaisesRegex(AssertionError,'NATIVE_RESTORATION'):v.native_receipt(r)
    def test_real_http(self):self.assertEqual(73,v.http_receipt(self.http())['total'])
    def test_http_observer_must_enter_callback(self):
        r=self.http();r['observations'][0]['entered']=False
        with self.assertRaisesRegex(AssertionError,'HTTP_ZERO'):v.http_receipt(r)
    def test_http_write_cannot_hide_under_all_true_checks(self):
        r=self.http();r['observations'][0]['sql']=['UPDATE']
        with self.assertRaisesRegex(AssertionError,'HTTP_ZERO'):v.http_receipt(r)
    def test_sessions_must_restore(self):
        r=self.http();r['sessions_restored']=False
        with self.assertRaisesRegex(AssertionError,'HTTP_RESTORATION'):v.http_receipt(r)
if __name__=='__main__':unittest.main(verbosity=2)
