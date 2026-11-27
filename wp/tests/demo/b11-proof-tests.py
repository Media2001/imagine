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
    def test_passive_observer_does_not_rewrite_path(self):
        text=(ROOT/'wp/tests/demo/b11-observer.php').read_text(encoding='utf-8')
        self.assertNotIn('use_block_editor_for_post',text)
        self.assertNotIn('allowed_options',text)
        self.assertNotIn('X_IMAGINE_B11_SETTINGS',text)

if __name__=='__main__':unittest.main()
