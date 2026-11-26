"""Fusion 17:53 regressions; all mutation targets are disposable scratch copies."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')

def load(relative,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

class CorrectionsTest(unittest.TestCase):
    def test_private_completion_binds_every_final_byte(self):
        guard=load('wp/outils/bascule/stream_guard.py','binding_fusion')
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            out=Path(tmp)/'result';shutil.copytree(ROOT/'production/A-22/preuves/final/utf8/A03/classic-a22-documented',out)
            hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
            message=guard.SUCCESS['A03'].encode()+b'A22_FINAL '+json.dumps(hashes,separators=(',',':')).encode()+b'\n'
            self.assertTrue(guard.final_binding('A03',message,out))
            p=out/'non-regression.json';data=json.loads(p.read_bytes());data['samples'][next(iter(data['samples']))]+=1
            p.write_text(json.dumps(data),encoding='utf-8')
            self.assertFalse(guard.final_binding('A03',message,out))
            self.assertFalse(guard.final_binding('A03',guard.SUCCESS['A03'].encode(),out))

    def test_private_binding_refuses_oversized_file_before_publication(self):
        guard=load('wp/outils/bascule/stream_guard.py','bounded_binding_fusion')
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            out=Path(tmp);file=out/'non-regression.json'
            file.write_bytes(b'x'*16777217)
            message=guard.SUCCESS['A03'].encode()+b'A22_FINAL '+json.dumps({file.name:hashlib.sha256(file.read_bytes()).hexdigest()},separators=(',',':')).encode()+b'\n'
            self.assertFalse(guard.final_binding('A03',message,out))

    def test_every_historical_invalid_final_name(self):
        guard=load('wp/outils/bascule/stream_guard.py','codes_fusion')
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();out=root/'out';out.mkdir()
            for tool in ['A12','A14','A15','A16','A17','A18','A19']:
                with self.subTest(tool=tool):
                    expected='A12_PATH_INVALID' if tool=='A12' else tool+'_OUTPUT_UNSAFE'
                    with self.assertRaisesRegex(RuntimeError,'^'+expected+'$'):
                        guard.inventory(tool,Path('unused'),{'--wp-path':str(site),'--output':str(out/'invalid.name')})

    def test_historical_invalid_names_at_real_python_entrypoints(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();out=root/'reports';out.mkdir()
            mapping=root/'map.json';mapping.write_text(json.dumps({'version':1,'encodage':'utf-8','separateur':';','colonnes':{'email':'email','statut':'statut'},'statuts':{'inscrit':['yes'],'desinscrit':['no'],'bloque':['blocked']}}),encoding='utf-8')
            contacts=root/'contacts.csv';contacts.write_text('email;statut\nfictive@example.org;yes\n',encoding='utf-8')
            for tool in ['A12','A14','A15','A16','A17','A18','A19']:
                command=[sys.executable,'-B',str(ROOT/('wp/outils/bascule/rapprocher-contacts' if tool=='A14' else 'wp/outils/bascule/'+tool.lower()+'/confine.py')),'--wp-path='+str(site),'--output='+str(out/'invalid.name'),'--audit=none']
                if tool=='A14':command+=['--correspondance='+str(mapping),'--contacts='+str(contacts)]
                if tool=='A16':command+=['--correspondance='+str(mapping)]
                p=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30,
                    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
                expected='A12_PATH_INVALID' if tool=='A12' else tool+'_OUTPUT_UNSAFE'
                with self.subTest(tool=tool):self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'',expected+'\n'))
                self.assertFalse((out/'invalid.name').exists())

    def test_a03_source_roots_are_present_and_required(self):
        matrix=load('wp/tests/a22/matrix.py','roots_fusion')
        values=matrix.sources()
        for file in ['Policy.php','Report.php','Site.php']:
            self.assertIn('wp/outils/bascule/a03/'+file,values)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            with patch.object(matrix,'ROOT',Path(tmp)):
                with self.assertRaisesRegex(RuntimeError,'A22_SOURCE_ROOT_MISSING'):
                    matrix.sources()

    def test_a03_policy_mutation_changes_executed_source_snapshot(self):
        matrix=load('wp/tests/a22/matrix.py','mutation_fusion')
        baseline=matrix.sources()
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            mirror=Path(tmp)/'mirror';mirror.mkdir()
            for name in baseline:
                target=mirror/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,target)
            with patch.object(matrix,'ROOT',mirror):
                self.assertEqual(matrix.sources(),baseline)
                policy=mirror/'wp/outils/bascule/a03/Policy.php'
                policy.write_bytes(policy.read_bytes()+b'\n// disposable source-drift witness\n')
                self.assertNotEqual(matrix.sources(),baseline)

    def test_json_numeric_slots_cannot_be_replaced_by_site_text(self):
        guard=load('wp/outils/bascule/stream_guard.py','counts_fusion')
        packet=ROOT/'production/A-22/preuves/final/utf8'
        def corrupt(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    if type(item) is int:value[key]='PRIVATE_COUNT';return True
                    if corrupt(item):return True
            elif isinstance(value,list):
                return any(corrupt(item) for item in value)
            return False
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            for tool in guard.FILES:
                dest=Path(tmp)/tool;shutil.copytree(packet/tool/'classic-a22-documented',dest)
                file=next(dest.glob('*.json'));data=json.loads(file.read_bytes())
                self.assertTrue(corrupt(data));file.write_text(json.dumps(data),encoding='utf-8')
                with self.subTest(tool=tool):self.assertFalse(guard.complete(dest,guard.FILES[tool]))

    def test_final_reports_contract_rejects_silent_shutdown_contamination(self):
        guard=load('wp/outils/bascule/stream_guard.py','reports_fusion')
        packet=ROOT/'production/A-22/preuves/final/utf8'
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            for tool in guard.FILES:
                original=packet/tool/'classic-a22-documented'
                with self.subTest(tool=tool):
                    dest=Path(tmp)/tool;shutil.copytree(original,dest)
                    self.assertTrue(guard.complete(dest,guard.FILES[tool]),tool+' nominal')
                    for file in dest.iterdir():
                        raw=file.read_bytes()
                        if file.suffix in {'.md','.csv'}:
                            file.write_bytes(raw+b'\nA22_PRIVATE_FLOW_CANARY\n')
                        else:
                            data=json.loads(raw);data['A22_PRIVATE_FLOW_CANARY']='private/path'
                            file.write_text(json.dumps(data),encoding='utf-8')
                        self.assertFalse(guard.complete(dest,guard.FILES[tool]),tool+':'+file.name)
                        file.write_bytes(raw)
                    self.assertTrue(guard.complete(dest,guard.FILES[tool]))

if __name__=='__main__':unittest.main()
