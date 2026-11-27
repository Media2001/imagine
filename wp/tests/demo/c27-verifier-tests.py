"""C27 : contre-exemples du vérificateur, sans site ni réseau, copies sous TMPDIR."""
import sys
sys.dont_write_bytecode=True
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('c27_verify',ROOT/'production/C-27/verifier.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='c27-verifier-',dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.packet=copy.deepcopy(verify.load(ROOT/'production/C-27/final-V2.json'))
        paths=set(self.packet['sources'])|set(self.packet['artifacts'])|{'wp/plugins/imagine-site/imagine-site.php','wp/plugins/imagine-site/README.md'}
        for name in paths:
            out=self.root/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,out)
    def resign(self,name,data):
        path=self.root/'production/C-27'/name
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        self.packet['artifacts']['production/C-27/'+name]=verify.digest(path.read_bytes())
    def recipe(self):return verify.load(self.root/'production/C-27'/self.packet['receipts']['recipe'])
    def reject(self,pattern):
        with self.assertRaisesRegex(AssertionError,pattern):verify.validate(self.root,self.packet)
    def test_reference(self):
        result=verify.validate(self.root,self.packet)
        self.assertEqual(result['unit_tests'],7)
        self.assertEqual(result['native_checks'],47)
    def test_scope(self):
        self.packet['scope']='autre-site';self.reject('SCHEMA')
    def test_drop_check_even_resigned(self):
        data=self.recipe();del data['checks']['POST_signe_avant_paiement_refuse'];self.resign(self.packet['receipts']['recipe'],data);self.reject('HTTP_CONTROLES_EXACTS')
    def test_false_check_even_resigned(self):
        data=self.recipe();data['checks']['effacement_preserve_tiers']=False;self.resign(self.packet['receipts']['recipe'],data);self.reject('HTTP_CONTROLES_EXACTS')
    def test_payment_mutation_must_really_write(self):
        data=self.recipe();data['mutation_pas_avant_paiement']['mutant_observed']['response_written']=False;self.resign(self.packet['receipts']['recipe'],data);self.reject('PAIEMENT_MUTATION_REELLE')
    def test_source_drift(self):
        p=self.root/verify.CORE[0];p.write_bytes(p.read_bytes()+b'\n// drift\n');self.reject('EMPREINTE')
    def test_declared_counts(self):
        self.packet['counts']['unit_assertions']+=1;self.reject('TOTAUX_RECALCULES')
    def test_actions_restoration_cannot_be_omitted(self):
        data=self.recipe();del data['restoration']['actionscheduler_actions'];self.resign(self.packet['receipts']['recipe'],data);self.reject('HTTP_RESTAURATION')
    def test_artifact_must_be_sealed(self):
        del self.packet['artifacts']['production/C-27/'+self.packet['receipts']['native']];self.reject('PREUVE_NON_SCELLEE')
    def test_foreign_failure_is_not_hidden(self):
        name=self.packet['receipts']['regression'];data=verify.load(self.root/'production/C-27'/name)
        data['results'][0]['packets']['failures'].append({'lot':'A-INCONNU','control':'INCONNU'})
        self.resign(name,data);self.reject('PAQUET_HORS_SCOPE_INATTENDU')


if __name__=='__main__':unittest.main(verbosity=2)
