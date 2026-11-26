"""Closed supervisor contracts, real bytes/files only; no PHP on Windows."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'wp/outils/bascule/a20'
def load(name):
    spec=importlib.util.spec_from_file_location('a20_'+name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
r=load('report');c=load('confine')
class ReportTest(unittest.TestCase):
    def setUp(self):
        scratch=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch') if sys.platform=='win32' else Path('/scratch')
        self.tmp=tempfile.TemporaryDirectory(prefix='a20-contract-',dir=scratch);self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);self.audit=root/'audit.json';self.audit.write_text(json.dumps({'sections':{'commerce':{'order_storage':'classic'}}}),encoding='utf-8')
        self.out=root/'out';self.out.mkdir()
        self.data={'schema':r.CONTRACT['schema'],'read_only':True,'scope':r.CONTRACT['scope'],'storage':'classic','audit_sha256':r.hashlib.sha256(self.audit.read_bytes()).hexdigest()}
        v={key:0 for key in r.CONTRACT['count_keys']}
        v.update(products=[],countries=[],other_countries={'count':0,'with_shipping':0},unknown_country={'count':0,'with_shipping':0},definitions=copy.deepcopy(r.CONTRACT['definitions']))
        self.data['counts']=v;self.save()
    def save(self,raw=None):
        raw=json.dumps(self.data).encode('utf-8') if raw is None else raw
        (self.out/'tarifs.json').write_bytes(raw);(self.out/'tarifs.md').write_bytes(r.HEADER.encode('utf-8')+raw+b'```\n')
    def invalid(self):
        with self.assertRaisesRegex(RuntimeError,'^A20_REPORT_INVALID$'):r.validate(self.out,self.audit)
    def test_valid_closed_empty_report(self):r.validate(self.out,self.audit)
    def test_unknown_top_level_field(self):self.data['private']='PRIVATE_CANARY';self.save();self.invalid()
    def test_unknown_count_field(self):self.data['counts']['private']='PRIVATE_CANARY';self.save();self.invalid()
    def test_arbitrary_definition_refused(self):self.data['counts']['definitions']['products']='PRIVATE_CANARY';self.save();self.invalid()
    def test_invalid_scope(self):self.data['scope']='PRIVATE_CANARY';self.save();self.invalid()
    def test_boolean_is_not_count(self):self.data['counts']['live_subscriptions']=False;self.save();self.invalid()
    def test_negative_count(self):self.data['counts']['zero_recurring_total']=-1;self.save();self.invalid()
    def test_readonly_strict_boolean(self):self.data['read_only']=1;self.save();self.invalid()
    def test_storage_mismatch(self):self.data['storage']='hpos';self.save();self.invalid()
    def test_audit_binding(self):self.data['audit_sha256']='0'*64;self.save();self.invalid()
    def test_markdown_addition(self):
        with (self.out/'tarifs.md').open('ab') as f:f.write(b'PRIVATE_CANARY')
        self.invalid()
    def test_missing_report(self):(self.out/'tarifs.md').unlink();self.invalid()
    def test_extra_report(self):(self.out/'private').write_text('PRIVATE_CANARY');self.invalid()
    def test_duplicate_json_key(self):self.save(b'{"schema":"one","schema":"two"}');self.invalid()
    def test_invalid_json_utf8(self):self.save(b'\xff');self.invalid()
    def test_country_threshold(self):
        self.data['counts'].update(live_subscriptions=1,countries=[{'country':'BE','count':1,'with_shipping':0}]);self.save();self.invalid()
    def test_country_closed_list(self):
        self.data['counts'].update(live_subscriptions=5,countries=[{'country':'XY','count':5,'with_shipping':0}]);self.save();self.invalid()
    def test_country_sum(self):self.data['counts']['live_subscriptions']=1;self.save();self.invalid()
    def test_product_unknown_key(self):
        self.data['counts']['products']=[{'private':'PRIVATE_CANARY'}];self.save();self.invalid()
    def test_negative_process_signal_never_forwarded(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([], -9,b'',b'A20_USAGE\n')),'A20_PROCESS_OUTPUT_INVALID')
    def test_exact_closed_refusal(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],1,b'',b'A20_USAGE\n')),'A20_USAGE')
    def test_plausible_but_unknown_code_refused(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],1,b'',b'A20_PRIVATE_CANARY\n')),'A20_PROCESS_OUTPUT_INVALID')
    def test_closed_refusal_plus_private_bytes(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],1,b'',b'A20_USAGE\nPRIVATE_CANARY')),'A20_PROCESS_OUTPUT_INVALID')
    def test_refusal_with_stdout_refused(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],1,b'PRIVATE_CANARY',b'A20_USAGE\n')),'A20_PROCESS_OUTPUT_INVALID')
    def test_exit_zero_is_not_refusal(self):
        self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],0,b'',b'A20_USAGE\n')),'A20_PROCESS_OUTPUT_INVALID')
    def test_closed_dropin_not_site_name(self):
        for name in [*c.DROPINS,'PRIVATE_CANARY']:
            message='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))
            self.assertEqual(c.closed_refusal(subprocess.CompletedProcess([],1,b'',(message+'\n').encode())),message if name in c.DROPINS else 'A20_PROCESS_OUTPUT_INVALID')
if __name__=='__main__':unittest.main()
