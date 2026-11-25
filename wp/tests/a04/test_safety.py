import hashlib, importlib.machinery, importlib.util, json, pathlib, tempfile, time, unittest, zipfile
ROOT=pathlib.Path('/subject') if pathlib.Path('/subject').is_dir() else pathlib.Path(__file__).resolve().parents[2]/'outils/bascule'
loader=importlib.machinery.SourceFileLoader('a04_update',str(ROOT/'mettre-a-jour'));spec=importlib.util.spec_from_loader(loader.name,loader);a04=importlib.util.module_from_spec(spec);loader.exec_module(a04)
def plan():
    steps=[{'component':k,'main_file':None if k=='core' else k+'.php','before':'1.0','after':'2.0','archive':'/package.zip','sha256':'a'*64,'adapter':k,'hooks':[]} for k in ['core','woocommerce','woocommerce-subscriptions','woocommerce-memberships']]
    steps[0].update(before='6.9.1',after='7.0.9')
    return {'schema':'imagine-a04-v1','site_status':'verified-staging','steps':steps}
class SafetyTests(unittest.TestCase):
    def test_valid_plan(self):self.assertEqual(a04.validate_plan(plan()),plan())
    def test_order(self):
        p=plan();p['steps'].reverse()
        with self.assertRaisesRegex(a04.Refusal,'A04_ORDER'):a04.validate_plan(p)
    def test_adapter(self):
        p=plan();p['steps'][1]['adapter']='shell'
        with self.assertRaisesRegex(a04.Refusal,'A04_ADAPTER'):a04.validate_plan(p)
    def test_downgrade(self):
        p=plan();p['steps'][1]['after']='0.1'
        with self.assertRaisesRegex(a04.Refusal,'A04_DOWNGRADE'):a04.validate_plan(p)
    def test_payment_hook(self):
        p=plan();p['steps'][2]['hooks']=['woocommerce_scheduled_subscription_payment']
        with self.assertRaisesRegex(a04.Refusal,'A04_HOOK'):a04.validate_plan(p)
    def test_extra_field(self):
        p=plan();p['shell']='bad'
        with self.assertRaisesRegex(a04.Refusal,'A04_PLAN'):a04.validate_plan(p)
class FileTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='a04-unit-');self.root=pathlib.Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def archive(self,entries):
        p=self.root/'package.zip'
        with zipfile.ZipFile(p,'w') as z:
            for k,v in entries.items():z.writestr(k,v)
        return p
    def test_traversal(self):
        p=self.archive({'woocommerce/../../escape':'bad'})
        with self.assertRaisesRegex(a04.Refusal,'A04_ARCHIVE_PATH'):a04.archive_entries(p,'woocommerce')
    def test_case_collision(self):
        p=self.archive({'woocommerce/A.php':'a','woocommerce/a.php':'b'})
        with self.assertRaisesRegex(a04.Refusal,'A04_ARCHIVE_COLLISION'):a04.archive_entries(p,'woocommerce')
    def test_core_exclusions(self):
        p=self.archive({'wordpress/wp-includes/version.php':'version','wordpress/wp-content/themes/x/style.css':'bad','wordpress/wp-config.php':'bad'})
        self.assertEqual([v[1] for v in a04.archive_entries(p,'core')],['wp-includes/version.php'])
    def test_no_deletion(self):
        site=self.root/'site';site.mkdir();(site/'old.php').write_text('keep');p=self.archive({'woocommerce/woocommerce.php':'new'});a04.overlay(p,site,'woocommerce')
        self.assertEqual((site/'old.php').read_text(),'keep');self.assertEqual((site/'wp-content/plugins/woocommerce/woocommerce.php').read_text(),'new')
    def test_symlink_destination(self):
        site=self.root/'site';site.mkdir();outside=self.root/'outside';outside.mkdir()
        try:(site/'wp-content').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('Linux fixture proves symlink refusal')
        p=self.archive({'woocommerce/woocommerce.php':'x'})
        with self.assertRaisesRegex(a04.Refusal,'A04_SYMLINK'):a04.overlay(p,site,'woocommerce')
        self.assertEqual(list(outside.iterdir()),[])
    def backup(self):
        files=[]
        for name in ['db.sql','content.tar']:
            p=self.root/name;p.write_text('fiction');files.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        return {'site':'/fiction','created_at':int(time.time()),'database':files[0],'files':files[1]}
    def test_backup_recent(self):a04.check_backup(self.backup(),'/fiction')
    def test_backup_old(self):
        b=self.backup();b['created_at']-=21601
        with self.assertRaisesRegex(a04.Refusal,'A04_BACKUP_AGE'):a04.check_backup(b,'/fiction')
    def test_backup_wrong_hash(self):
        b=self.backup();b['database']['sha256']='0'*64
        with self.assertRaisesRegex(a04.Refusal,'A04_BACKUP_HASH'):a04.check_backup(b,'/fiction')
    def test_backup_other_site(self):
        with self.assertRaisesRegex(a04.Refusal,'A04_BACKUP_SITE'):a04.check_backup(self.backup(),'/other')
    def test_atomic_state(self):
        p=self.root/'state.json';a04.atomic_json(p,{'status':'migrating'});self.assertEqual(json.loads(p.read_text()),{'status':'migrating'})
    def test_inert_version(self):
        site=self.root/'site';(site/'wp-includes').mkdir(parents=True);(site/'wp-includes/version.php').write_text("<?php $wp_version = '6.9.1'; throw new Exception('TRAP');")
        self.assertEqual(a04.version(site,'core'),'6.9.1')
    def test_bad_state(self):
        with self.assertRaisesRegex(a04.Refusal,'A04_STATE'):a04.validate_state({'completed':['core']},'x','/fiction','c')
if __name__=='__main__':unittest.main(verbosity=2)
