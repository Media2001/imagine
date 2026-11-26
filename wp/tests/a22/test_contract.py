"""Final verifier/documentation/closed-message regressions, no PHP on Windows."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[3]


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


class ContractTest(unittest.TestCase):
    def test_both_receipt_arrays_checked(self):
        v=load(ROOT/'wp/tests/a22/verify.py','a22_verify_test')
        self.assertFalse(v.green({'exit_code':0,'tests':[{'status':'PASS'}],'checks':[{'status':'FAIL'}]}))
        self.assertFalse(v.green({'exit_code':0,'tests':[{'status':'FAIL'}],'checks':[{'status':'PASS'}]}))
        self.assertTrue(v.green({'exit_code':0,'checks':[{'ok':True}]}))
        self.assertFalse(v.green({'exit_code':0,'checks':[]}))

    def test_legacy_receipt_shapes_are_explicit_and_complete(self):
        v=load(ROOT/'wp/tests/a22/verify.py','legacy_verify_test')
        self.assertTrue(v.green({'exit_code':0,'tests':{'legacy_case':True}}))
        self.assertFalse(v.green({'exit_code':0,'tests':{'legacy_case':False},'checks':[{'check':'new','status':'PASS'}]}))
        old={'checks':[{'check':'old','status':'PASS'}]}
        self.assertFalse(v.green(old))
        self.assertTrue(v.green(old,legacy=True))

    def test_documented_commands_are_exact_source_lines(self):
        docs=json.loads((ROOT/'wp/tests/a22/documented.json').read_text(encoding='utf-8'))
        for tool,command in docs.items():
            path=ROOT/('wp/outils/bascule/non-regression.md' if tool=='A03' else 'wp/outils/bascule/'+tool.lower()+'/README.md')
            text=path.read_text(encoding='utf-8').replace('\\\n',' ')
            self.assertIn(command,' '.join(text.split()),tool)

    def test_a20_a21_call_same_function_not_copies(self):
        g=load(ROOT/'wp/outils/bascule/stream_guard.py','shared')
        a21=load(ROOT/'wp/outils/bascule/a21/confine.py','a21_test')
        self.assertEqual(a21.supervise.__code__.co_filename,g.supervise.__code__.co_filename)
        a20=(ROOT/'wp/outils/bascule/a20/confine.py').read_text(encoding='utf-8')
        self.assertIn('guard.supervise(',a20)
        self.assertNotIn('subprocess.run(',a20)
        self.assertNotIn('def supervise(',a20)

    def test_closed_refusal_never_accepts_prefix_or_site_names(self):
        guard=load(ROOT/'wp/outils/bascule/stream_guard.py','guard_codes')
        values=guard.allowed_messages()
        for bad in [b'A11_SYMLINK_UNSUPPORTED /PRIVATE_CANARY\n',b'A11_PRIVATE_CANARY\n',
                    b'A11_DROPIN_UNSUPPORTED {"file":"PRIVATE_CANARY"}\n',b'A11_SYMLINK_UNSUPPORTED\nLATE']:
            self.assertEqual(guard.closed_refusal(1,b'',bad,values,'CLOSED'),'CLOSED')
        good='A16_MAPPING_KEY_ABSENT {"field":"pdf_cle"}'
        self.assertEqual(guard.closed_refusal(1,b'',(good+'\n').encode(),values,'CLOSED'),good)

    def test_partial_report_is_not_complete(self):
        guard=load(ROOT/'wp/outils/bascule/stream_guard.py','guard_files')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            p=Path(tmp)
            (p/'contenus.json').write_text('{}',encoding='utf-8')
            self.assertFalse(guard.complete(p,guard.FILES['A12']))
            (p/'contenus.md').write_text('report',encoding='utf-8')
            self.assertTrue(guard.complete(p,guard.FILES['A12']))
            (p/'extra').write_text('private',encoding='utf-8')
            self.assertFalse(guard.complete(p,guard.FILES['A12']))

if __name__=='__main__':unittest.main()
