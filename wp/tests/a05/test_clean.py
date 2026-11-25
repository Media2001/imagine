"""Safety contracts exercised inside the owned offline runner."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
sys.path.insert(0, '/subject/a05')

class Contract(unittest.TestCase):
    def test_unnamed_plugin_is_kept(self):
        import clean
        plan = {'plugins': []}
        self.assertEqual('garder', clean.plugin_action(plan, 'unnamed/main.php'))

    def test_dependency_blocks_removal_named_in_error(self):
        import clean
        plan = {'plugins': [{'plugin': 'base/base.php', 'action': 'retirer', 'uninstall': False}], 'tables': [], 'options': [], 'cron': [], 'uploads': [], 'table_owners': {}}
        inventory = {'plugins': {'base/base.php': {'requires': [], 'gateway': False}, 'kept/kept.php': {'requires': ['base'], 'gateway': False}}, 'theme': 'fiction', 'tables': [], 'options': [], 'cron': [], 'prefix': 'wp_'}
        with self.assertRaisesRegex(clean.Refusal, 'DEPENDENCY.*base/base.php'):
            clean.protect(plan, inventory)

    def test_inventory_entrypoint_is_available(self):
        import clean
        self.assertTrue(callable(clean.inspect_site))

class Safety(unittest.TestCase):
    def plan(self):
        return {'schema':'imagine-a05-v1','site_status':'verified-staging','plugins':[],'tables':[],'options':[],'cron':[],'uploads':[],'table_owners':{}}

    def inventory(self):
        return {'plugins':{'keep/main.php':{'requires':[],'gateway':False}},'theme':'fiction','tables':[],'options':[],'cron':[],'prefix':'wp_','mu_plugins':[]}

    def test_example_is_only_a_keep_form(self):
        import clean,json
        p=clean.validate(json.loads(pathlib.Path('/subject/plan-imagine.exemple.json').read_text()))
        self.assertTrue(all(r['action']=='garder' for kind in ['plugins','tables','uploads'] for r in p[kind]))
        self.assertTrue(all(r['uninstall'] is False for r in p['plugins']))
        self.assertEqual([],p['options']);self.assertEqual([],p['cron']);self.assertEqual({},p['table_owners'])
        self.assertEqual({'ahm_','matomo_','fsmpt_email_logs'},{r['name'] for r in p['tables']})

    def test_example_directory_names_only_allowed_for_keep(self):
        import clean
        p=self.plan();p['plugins']=[{'plugin':'diagnostic-directory','action':'garder','uninstall':False}]
        self.assertEqual(p,clean.validate(p))
        p['plugins'][0]['action']='retirer'
        with self.assertRaises(clean.Refusal):clean.validate(p)

    def test_directory_keep_wins_over_main_file_removal(self):
        import clean
        p=self.plan();p['plugins']=[{'plugin':'example','action':'garder','uninstall':False},{'plugin':'example/main.php','action':'retirer','uninstall':False}]
        self.assertEqual('garder',clean.plugin_action(p,'example/main.php'))
        with tempfile.TemporaryDirectory() as tmp:
            site=pathlib.Path(tmp);folder=site/'wp-content/plugins/example';folder.mkdir(parents=True);(folder/'main.php').write_text('<?php')
            i=self.inventory();i['plugins']={'example/main.php':{'requires':[],'gateway':False,'active':True}}
            self.assertEqual([],clean.operations(site,p,i))

    def test_keep_wins_over_prefix_deletion(self):
        import clean
        rules=[{'match':'prefix','name':'old_','action':'supprimer'},{'match':'exact','name':'old_keep','action':'garder'}]
        self.assertFalse(clean.selected(rules,'old_keep'));self.assertTrue(clean.selected(rules,'old_drop'));self.assertFalse(clean.selected(rules,'unlisted'))

    def test_unknown_fields_rejected(self):
        import clean
        p=self.plan();p['themes']=[]
        with self.assertRaisesRegex(clean.Refusal,'A05_PLAN'):clean.validate(p)

    def test_missing_ownership_refuses_table_drop(self):
        import clean
        p=self.plan();p['tables']=[{'match':'exact','name':'wp_old','action':'supprimer'}];i=self.inventory();i['tables']=[{'name':'wp_old'}]
        with self.assertRaisesRegex(clean.Refusal,'A05_TABLE_OWNERSHIP_REQUIRED:keep/main.php'):clean.protect(p,i)

    def test_core_and_commerce_tables_always_protected(self):
        import clean
        for table in ['wp_posts','wp_options','wp_users','wp_wc_orders','wp_woocommerce_order_items','wp_actionscheduler_actions']:
            with self.subTest(table=table):
                p=self.plan();p['table_owners']={'keep/main.php':[],'theme:fiction':[]};p['tables']=[{'match':'exact','name':table,'action':'supprimer'}];i=self.inventory();i['tables']=[{'name':table}]
                with self.assertRaisesRegex(clean.Refusal,'A05_PROTECTED_TABLE:'+table):clean.protect(p,i)

    def test_protected_plugins_even_inactive(self):
        import clean
        for name in ['woocommerce/woocommerce.php','woocommerce-subscriptions/main.php','woocommerce-memberships/main.php','unknown/main.php']:
            with self.subTest(name=name):
                p=self.plan();p['plugins']=[{'plugin':name,'action':'desactiver','uninstall':False}];i=self.inventory();i['plugins']={name:{'gateway':name.startswith('unknown'),'requires':[]}}
                with self.assertRaisesRegex(clean.Refusal,'A05_PROTECTED_PLUGIN'):clean.protect(p,i)

    def test_option_and_hook_commerce_protected(self):
        import clean
        for kind,name in [('options','woocommerce_setting'),('cron','woocommerce_payment')]:
            with self.subTest(kind=kind):
                p=self.plan();p[kind]=[{'match':'exact','name':name,'action':'supprimer'}];i=self.inventory();i[kind]=[{'name':name}]
                with self.assertRaises(clean.Refusal):clean.protect(p,i)

    def test_upload_escape_and_symlink_are_refused(self):
        import clean
        with tempfile.TemporaryDirectory() as tmp:
            site=pathlib.Path(tmp);(site/'wp-content/uploads').mkdir(parents=True)
            for rel in ['../outside','/outside','a/../../outside','a\\outside','a//outside','a/./outside']:
                with self.subTest(rel=rel),self.assertRaises(clean.Refusal):clean.safe_upload(site,rel)
            outside=site/'outside';outside.mkdir();(site/'wp-content/uploads/link').symlink_to(outside,target_is_directory=True)
            with self.assertRaisesRegex(clean.Refusal,'A05_UPLOAD_SYMLINK'):clean.safe_upload(site,'link')

    def test_upload_kept_descendant_blocks_ancestor_deletion(self):
        import clean
        with tempfile.TemporaryDirectory() as tmp:
            site=pathlib.Path(tmp);(site/'wp-content/uploads/old/keep').mkdir(parents=True)
            p=self.plan();p['uploads']=[{'path':'old','action':'supprimer'},{'path':'old/keep','action':'garder'}]
            with self.assertRaisesRegex(clean.Refusal,'A05_UPLOAD_KEEP_CONFLICT'):clean.operations(site,p,self.inventory())

    def test_shared_directory_deactivate_neighbour_refuses_in_both_orders(self):
        import clean
        for active in [True, False]:
            for reverse in [False, True]:
                with self.subTest(active=active, reverse=reverse), tempfile.TemporaryDirectory() as tmp:
                    site=pathlib.Path(tmp);folder=site/'wp-content/plugins/shared';folder.mkdir(parents=True)
                    for name in ['remove.php','deactivate.php']:(folder/name).write_text('<?php // Plugin Name: Fiction')
                    p=self.plan();p['plugins']=[{'plugin':'shared/remove.php','action':'retirer','uninstall':False},{'plugin':'shared/deactivate.php','action':'desactiver','uninstall':False}]
                    if reverse:p['plugins'].reverse()
                    i=self.inventory();i['plugins']={name:{'requires':[],'gateway':False,'active':active} for name in ['shared/remove.php','shared/deactivate.php']}
                    before={x.name:x.read_bytes() for x in folder.iterdir()}
                    with self.assertRaisesRegex(clean.Refusal,'A05_SHARED_PLUGIN_DIRECTORY:shared'):
                        clean.operations(site,p,i)
                    self.assertEqual(before,{x.name:x.read_bytes() for x in folder.iterdir()})

    def test_shared_directory_multiple_removals_refuse_instead_of_early_rmtree(self):
        import clean
        with tempfile.TemporaryDirectory() as tmp:
            site=pathlib.Path(tmp);folder=site/'wp-content/plugins/shared';folder.mkdir(parents=True)
            p=self.plan();p['plugins']=[{'plugin':'shared/'+name,'action':'retirer','uninstall':True} for name in ['first.php','second.php']]
            i=self.inventory();i['plugins']={r['plugin']:{'requires':[],'gateway':False,'active':True} for r in p['plugins']}
            with self.assertRaisesRegex(clean.Refusal,'A05_SHARED_PLUGIN_DIRECTORY:shared'):clean.operations(site,p,i)

    def test_comment_dependency_headers_block_removal_and_deactivation(self):
        import clean
        from unittest.mock import patch
        for prefix in ['// ', '# ', '@ ', '/* ', '* ', '']:
            for action in ['retirer','desactiver']:
                with self.subTest(prefix=prefix,action=action), tempfile.TemporaryDirectory() as tmp:
                    site=pathlib.Path(tmp);directory=site/'wp-content/plugins';(directory/'base').mkdir(parents=True);(directory/'kept').mkdir()
                    (directory/'base/main.php').write_text('<?php\n// Plugin Name: Fiction base\n')
                    (directory/'kept/main.php').write_text('<?php\n'+prefix+'Plugin Name: Fiction kept\n'+prefix+'Requires Plugins: base\n')
                    p=self.plan();p['plugins']=[{'plugin':'base/main.php','action':action,'uninstall':False}]
                    i=self.inventory();i['active']=[]
                    with patch.object(clean,'database',return_value=i):actual=clean.inspect_site(site)
                    with self.assertRaisesRegex(clean.Refusal,'A05_DEPENDENCY:base/main.php'):
                        clean.operations(site,p,actual)

    def test_upload_kept_ancestor_blocks_descendant_deletion_in_both_orders(self):
        import clean
        for reverse in [False,True]:
            with self.subTest(reverse=reverse),tempfile.TemporaryDirectory() as tmp:
                site=pathlib.Path(tmp);folder=site/'wp-content/uploads/archive/2020';folder.mkdir(parents=True);(folder/'canary.txt').write_text('fiction kept')
                p=self.plan();p['uploads']=[{'path':'archive','action':'garder'},{'path':'archive/2020','action':'supprimer'}]
                if reverse:p['uploads'].reverse()
                with self.assertRaisesRegex(clean.Refusal,'A05_UPLOAD_KEEP_CONFLICT:archive/2020'):clean.operations(site,p,self.inventory())
                self.assertEqual('fiction kept',(folder/'canary.txt').read_text())

    def test_absent_plan_names_are_information_only_for_every_resource_kind(self):
        import clean
        self.assertTrue(hasattr(clean,'absent_resources'),'dry-run lacks informational absent-name inventory')
        with tempfile.TemporaryDirectory() as tmp:
            site=pathlib.Path(tmp);(site/'wp-content/uploads/present').mkdir(parents=True)
            p=self.plan();p['plugins']=[{'plugin':n,'action':'garder','uninstall':False} for n in ['keep','missing/main.php']]
            for kind in ['tables','options','cron']:
                p[kind]=[{'match':'exact','name':'missing_'+kind,'action':'supprimer'},{'match':'prefix' if kind!='cron' else 'exact','name':'present_'+kind,'action':'garder'}]
            p['uploads']=[{'path':'missing','action':'supprimer'},{'path':'present','action':'garder'}]
            i=self.inventory()
            for kind in ['tables','options','cron']:i[kind]=[{'name':'present_'+kind}]
            expected=[{'kind':kind,'name':name,'status':'nommé, absent'} for kind,name in [('plugin','missing/main.php'),('table','missing_tables'),('option','missing_options'),('cron','missing_cron'),('upload','missing')]]
            self.assertEqual(expected,clean.absent_resources(site,p,i))
            self.assertEqual([],clean.operations(site,p,i))
            self.assertTrue((site/'wp-content/uploads/present').is_dir())

    def test_production_go_is_task_specific(self):
        import clean
        p=self.plan();p['site_status']='frozen-production'
        with self.assertRaisesRegex(clean.Refusal,'A05_PRODUCTION_GO_REQUIRED'):clean.authorize(p,pathlib.Path('/fiction'),'0'*64,None)

    def test_uninstall_requires_explicit_removal(self):
        import clean
        p=self.plan();p['plugins']=[{'plugin':'fiction/main.php','action':'desactiver','uninstall':True}]
        with self.assertRaisesRegex(clean.Refusal,'A05_PLUGIN'):clean.validate(p)

if __name__ == '__main__':
    unittest.main()
