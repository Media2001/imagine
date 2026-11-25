import copy, importlib.util, pathlib, unittest
path=pathlib.Path('/subject/a04/qualification.py') if pathlib.Path('/subject').exists() else pathlib.Path(__file__).resolve().parents[2]/'outils/bascule/a04/qualification.py'
class QualificationTests(unittest.TestCase):
    def module(self):
        self.assertTrue(path.is_file(),'A04_QUALIFICATION_MISSING')
        spec=importlib.util.spec_from_file_location('qualification',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def fixture(self):
        before={'generated_at_utc':'2026-11-25T10:00:00+00:00','versions':{'wordpress':'7.0','woocommerce':'11.0.1','subscriptions':'9.4.1','memberships':'1.30.3','php':'8.2.36'},'actions':{'1':{'hook':'woocommerce_scheduled_subscription_payment','date':'2027-01-01 00:00:00'}},'action_days':{'woocommerce_scheduled_subscription_payment:2027-01-01':1},'access':{'2:3':True}}
        after=copy.deepcopy(before);after['generated_at_utc']='2026-11-25T10:01:00+00:00';after['versions']['wordpress']='7.0.9';after['versions']['woocommerce']='11.1.1';after['actions']['2']={'hook':'woocommerce_run_on_woocommerce_admin_updated','date':'2026-11-25 10:00:30'};after['action_days']['woocommerce_run_on_woocommerce_admin_updated:2026-11-25']=1
        targets={'wordpress':'7.0.9','woocommerce':'11.1.1','subscriptions':'9.4.1','memberships':'1.30.3'}
        return before,after,targets
    def test_exact_one_native_hook(self):
        m=self.module();a,b,t=self.fixture();self.assertTrue(m.qualify(a,b,t)['qualified'])
    def test_other_hook_is_not_noise(self):
        m=self.module();a,b,t=self.fixture();b['actions']['2']['hook']='unexpected_upgrade'
        self.assertFalse(m.qualify(a,b,t)['qualified'])
    def test_membership_change_is_not_noise(self):
        m=self.module();a,b,t=self.fixture();b['access']['2:3']=False
        self.assertFalse(m.qualify(a,b,t)['qualified'])
    def test_duplicate_native_job_refused(self):
        m=self.module();a,b,t=self.fixture();b['actions']['3']=copy.deepcopy(b['actions']['2']);b['action_days']['woocommerce_run_on_woocommerce_admin_updated:2026-11-25']=2
        self.assertFalse(m.qualify(a,b,t)['qualified'])
    def test_php_drift_refused(self):
        m=self.module();a,b,t=self.fixture();b['versions']['php']='8.4.0'
        self.assertFalse(m.qualify(a,b,t)['qualified'])
    def test_action_deletion_refused(self):
        m=self.module();a,b,t=self.fixture();del b['actions']['1']
        self.assertFalse(m.qualify(a,b,t)['qualified'])
if __name__=='__main__':unittest.main(verbosity=2)
