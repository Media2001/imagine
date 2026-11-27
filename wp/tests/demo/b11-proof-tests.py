"""Contrats locaux des assertions B11 ; aucune de ces unités ne vaut rejeu UI."""
import sys
sys.dont_write_bytecode=True
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
spec=importlib.util.spec_from_file_location('recipe',ROOT/'wp/outils/demo/b11-recette.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ProofRules(unittest.TestCase):
    def test_same_preimage_cannot_prove_changed_write(self):
        self.assertFalse(m.persisted({'11':['old','pod'],'3454':['old','pod']},{'11':['new','newpod'],'3454':['new','newpod']}))
    def test_both_objects_required(self):
        self.assertFalse(m.persisted({'11':['new','newpod']},{'11':['new','newpod'],'3454':['new','newpod']}))
    def test_both_fields_required(self):
        self.assertFalse(m.persisted({'11':['new','oldpod']},{'11':['new','newpod']}))
    def test_clear_is_a_real_expected_state(self):
        self.assertTrue(m.persisted({'11':['','']},{'11':['','']}))
        self.assertFalse(m.persisted({'11':['old','oldpod']},{'11':['','']}))
    def test_only_admin_origin_can_except_gravatar(self):
        event={'url':'https://secure.gravatar.com/avatar/test','context':'admin','origin':'http://fictif.invalid/wp-admin/post.php'}
        self.assertFalse(m.forbidden_external(event))
        self.assertTrue(m.forbidden_external({**event,'context':'anon'}))
        self.assertTrue(m.forbidden_external({**event,'origin':'http://fictif.invalid/article/'}))
    def test_public_gravatar_and_admin_other_host_are_red(self):
        self.assertTrue(m.forbidden_external({'url':'https://secure.gravatar.com/avatar/test','context':'anon','origin':'http://fictif.invalid/article/'}))
        self.assertTrue(m.forbidden_external({'url':'https://s.w.org/test','context':'admin','origin':'http://fictif.invalid/wp-admin/post.php'}))
    def test_effective_defaults_accept_only_exact_native_explicit_default(self):
        def row(value, present, default='default'):
            return {'effective_sha256': value, 'raw_sha256': value if present else None,
                    'present': present, 'default_sha256': default, 'default_known': True}
        before={'imagine_medias':row('off',True),'owned':row('default',False)}
        after={'imagine_medias':row('on',True),'owned':row('default',True)}
        result=m.compare_options(before,after)
        self.assertTrue(result['ok'])
        self.assertEqual(result['absent_to_exact_default'],['owned'])
        for damaged in [row('different',True),row('DEFAULT',True),row('empty',True)]:
            self.assertFalse(m.compare_options(before,{**after,'owned':damaged})['ok'])
        self.assertFalse(m.compare_options(before,{'imagine_medias':after['imagine_medias']})['ok'])
        present={**before,'owned':row('invalid-but-existing',True)}
        self.assertFalse(m.compare_options(present,after)['ok'])
        self.assertFalse(m.compare_options(before,{**after,'owned':{**after['owned'],'default_sha256':'changed'}})['ok'])

    def test_ambient_destination_does_not_allow_arbitrary_local_or_external_requests(self):
        known={'host':'license.dynamic.ooo','ambient_novamira_update':True,'subject_b11':False}
        self.assertTrue(m.ambient_destination(known,'http://demo.invalid:8085'))
        cron={'host':'demo.invalid','path':'/wp-cron.php','stack':['spawn_cron'],
              'ambient_novamira_update':False,'subject_b11':False}
        self.assertTrue(m.ambient_destination(cron,'http://demo.invalid:8085'))
        for bad in [{**cron,'host':'evil.invalid'},{**cron,'path':'/unexpected'},
                    {**cron,'stack':[]},{**cron,'subject_b11':True},
                    {**known,'host':'evil.invalid'}]:
            self.assertFalse(m.ambient_destination(bad,'http://demo.invalid:8085'))

    def test_passive_observer_does_not_rewrite_path(self):
        text=(ROOT/'wp/tests/demo/b11-observer.php').read_text(encoding='utf-8')
        self.assertNotIn('use_block_editor_for_post',text)
        self.assertNotIn('allowed_options',text)
        self.assertNotIn('X_IMAGINE_B11_SETTINGS',text)

if __name__=='__main__':unittest.main()
