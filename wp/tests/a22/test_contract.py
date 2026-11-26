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

    def test_empty_wp_path_is_not_promoted_to_the_current_directory(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/a12/confine.py'),
                '--wp-path=','--audit='+str(Path(tmp)/'audit.json'),'--output='+str(Path(tmp)/'result')],
                cwd=ROOT,env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A12_USAGE\n'))

    def test_a20_invalid_final_basename_cannot_be_hidden_by_staging(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();reports=root/'reports';reports.mkdir()
            audit=reports/'audit';audit.mkdir();(audit/'audit.json').write_text('{}',encoding='utf-8')
            p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/a20/confine.py'),
                '--wp-path='+str(site),'--audit='+str(audit/'audit.json'),'--output='+str(reports/'invalid.name')],
                env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A20_OUTPUT_UNSAFE\n'))
            self.assertFalse((reports/'invalid.name').exists())

    def test_legacy_php_path_refusals_are_preserved_by_the_proxy(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            root=Path(tmp)
            for tool,extra,want in [('A03','--config=none','A03_PATH_UNSAFE_OR_EXISTS'),
                                    ('A11','--audit=none','A11_PATH_INVALID')]:
                with self.subTest(tool=tool):
                    p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/stream_guard.py'),tool,
                        '--wp-path='+str(root/'missing'),'--output='+str(root/'out'),extra],
                        env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                        capture_output=True,text=True,encoding='utf-8',timeout=30)
                    self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'',want+'\n'))

    def test_legacy_php_basename_and_exists_codes_are_preserved(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();reports=root/'reports';reports.mkdir();(reports/'existing').mkdir()
            for tool,extra,badname,exists in [('A03','--config=none','A03_PATH_UNSAFE_OR_EXISTS','A03_PATH_UNSAFE_OR_EXISTS'),
                                            ('A11','--audit=none','A11_PATH_INVALID','A11_OUTPUT_EXISTS')]:
                for name,want in [('invalid.name',badname),('existing',exists)]:
                    with self.subTest(tool=tool,name=name):
                        p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/stream_guard.py'),tool,
                            '--wp-path='+str(site),'--output='+str(reports/name),extra],
                            env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                            capture_output=True,text=True,encoding='utf-8',timeout=30)
                        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'',want+'\n'))

    def test_a14_legacy_generic_refusal_is_preserved(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            p=subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/rapprocher-contacts'),
                '--wp-path='+str(Path(tmp)/'missing'),'--output='+str(Path(tmp)/'out'),
                '--audit=none','--contacts=none','--correspondance=none'],
                env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'},
                capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A14_FAILED\n'))

    def test_nonexistent_python_banks_are_declared_not_reported_green(self):
        verifier=load(ROOT/'wp/tests/a22/verify.py','applicability_verifier')
        matrix=verifier.m
        self.assertEqual(set(matrix.NO_PYTHON),{'A03','A11'})
        self.assertEqual(matrix.PYTHON_LOTS,[lot for lot in matrix.LOTS if lot not in matrix.NO_PYTHON]+['A22'])
        for lot in matrix.LOTS:
            files=list((ROOT/'wp/tests'/matrix.DIRS[lot]).rglob('test_*.py'))
            self.assertEqual(bool(files),lot not in matrix.NO_PYTHON)

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
