"""Mandatory A28 importer semantics for the A25 synthetic bench."""
import importlib.util
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a25_verifier_contract',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class ImportPurgeContract(unittest.TestCase):
    def data(self):
        return {'neutraliser_and_anonymiser_executed':True,'marker_count':1,
                'comments_before':3,'comments_after':3,'emails_before':2,'emails_after':3,'ip_before':2,'ip_after':0,
                'known_messages_before':2,'known_messages_after':0,'unknown_messages_before':2,'unknown_message_preserved':True,
                'submission_pk_messages_preserved':True,'submission_child_rows_preserved':True,'guest_orders_preserved':True}
    def test_real_purge_and_unknown_separate(self):
        self.assertTrue(v.import_purge_valid(self.data()))
    def test_known_messages_survive_is_red(self):
        d=self.data();d['known_messages_after']=2
        self.assertFalse(v.import_purge_valid(d))
    def test_absent_positive_purge_witness_is_red(self):
        d=self.data();d['known_messages_before']=0
        self.assertFalse(v.import_purge_valid(d))
    def test_unknown_erasure_is_red(self):
        d=self.data();d['unknown_message_preserved']=False
        self.assertFalse(v.import_purge_valid(d))
    def test_native_red_keep_refusal_and_rollback_are_required(self):
        self.assertTrue((HERE/'neutralise-keep-red.php').is_file())
        for name in ('actual_old_keep_refused_red','old_keep_refusal_database_unchanged'):
            self.assertIn(name,(HERE/'inside.py').read_text(encoding='utf-8'))
            self.assertIn(name,(HERE/'verify.py').read_text(encoding='utf-8'))
    def test_fixture_must_not_request_known_keep(self):
        text=(HERE/'neutralise.php').read_text(encoding='utf-8')
        self.assertNotIn("'wp_fluentform_submissions' => ['action' => 'garder']",text)
        self.assertIn("'known_messages_after'",text)
if __name__=='__main__':unittest.main()
