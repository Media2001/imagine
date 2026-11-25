import importlib.util, pathlib, tempfile, time, json, unittest
P=pathlib.Path('/subject/a04/update.py') if pathlib.Path('/subject').exists() else pathlib.Path(__file__).resolve().parents[2]/'outils/bascule/a04/update.py'
s=importlib.util.spec_from_file_location('a04_go',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class GoTests(unittest.TestCase):
    def test_production_without_go_refused(self):
        with self.assertRaisesRegex(m.Refusal,'A04_PRODUCTION_GO_REQUIRED'):m.authorize('frozen-production','/fiction','a'*64,None)
    def test_expired_go_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'go.json';p.write_text(json.dumps({'author':'Ced','task':'A-04-mise-a-jour','go':True,'site':'/fiction','plan_sha256':'a'*64,'expires_at':int(time.time())-1}))
            with self.assertRaisesRegex(m.Refusal,'A04_PRODUCTION_GO_INVALID'):m.authorize('frozen-production','/fiction','a'*64,p)
    def test_go_bound_to_plan_and_site(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'go.json';p.write_text(json.dumps({'author':'Ced','task':'A-04-mise-a-jour','go':True,'site':'/fiction','plan_sha256':'a'*64,'expires_at':int(time.time())+3600}))
            self.assertEqual(m.authorize('frozen-production','/fiction','a'*64,p),'production')
            with self.assertRaisesRegex(m.Refusal,'A04_PRODUCTION_GO_INVALID'):m.authorize('frozen-production','/other','a'*64,p)
            with self.assertRaisesRegex(m.Refusal,'A04_PRODUCTION_GO_INVALID'):m.authorize('frozen-production','/fiction','b'*64,p)
if __name__=='__main__':unittest.main(verbosity=2)
