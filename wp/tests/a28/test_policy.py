"""A28 policy regressions; real Windows Python, no PHP/Docker here."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/staging-court'
sys.path.insert(0, str(TOOLS))
from archive import Refusal
from table_policy import Policy
from sql_stream import validate_file
from diagnosis import parser_module

TABLES = ['fluentform_submissions', 'fluentform_entry_details', 'fluentform_submission_meta',
          'fluentform_logs', 'fluentform_draft_submissions', 'ff_scheduled_actions']


def base_sql():
    return (b'CREATE TABLE `wp_options` (`option_name` varchar(100), `option_value` text) ENGINE=InnoDB;'
            b"INSERT INTO `wp_options` VALUES ('home','fiction'),('siteurl','fiction');"
            + b''.join(('CREATE TABLE `wp_' + t + '` (`id` bigint) ENGINE=InnoDB;').encode()
                       for t in ('users', 'usermeta', 'posts', 'postmeta', 'comments')))


class FormPolicy(unittest.TestCase):
    def test_01_keep_known_refused_with_closed_table_only(self):
        for table in TABLES:
            with self.subTest(table=table):
                with self.assertRaises(Refusal) as caught:
                    Policy({}, {'wp_' + table: {'action': 'garder'}}).resolve('wp_' + table, 'wp_')
                self.assertEqual('FORM_MESSAGES_DECISION_REFUSED', str(caught.exception))
                self.assertEqual({'table': table}, caught.exception.detail)

    def test_anonymise_not_a_free_text_substitute(self):
        for table in TABLES:
            with self.subTest(table=table), self.assertRaises(Refusal):
                Policy({}, {'x_' + table: {'action': 'anonymiser', 'columns': ['payload']}}).resolve('x_' + table, 'x_')

    def test_closed_tables_always_empty(self):
        for table in TABLES:
            self.assertEqual(({'action': 'vider'}, 'formulaires'), Policy({}).resolve('wp_' + table, 'wp_'))
            self.assertEqual(({'action': 'vider'}, 'formulaires'),
                             Policy({}, {'wp_' + table: {'action': 'vider'}}).resolve('wp_' + table, 'wp_'))

    def test_unknown_table_and_magazine_decisions_not_changed(self):
        for table in ('fiction_messages', 'fiction_fluentform_submissions', 'fluentform_submissions_archive'):
            self.assertEqual('garder', Policy({}, {'wp_' + table: {'action': 'garder'}}).resolve('wp_' + table, 'wp_')[0]['action'])
            self.assertEqual('vider', Policy({}).resolve('wp_' + table, 'wp_')[0]['action'])
        self.assertEqual(({'action': 'garder'}, 'catalogue'), Policy({'posts': []}).resolve('wp_posts', 'wp_'))

    def test_full_validator_ignores_non_utf8_known_payload(self):
        for table in TABLES:
            raw = base_sql() + ('CREATE TABLE `wp_' + table + '` (`payload` longtext) ENGINE=InnoDB;').encode()
            raw += ('INSERT INTO `wp_' + table + '` VALUES ').encode() + b"(_binary'\xffA28_FICTIVE_UNIT');"
            with tempfile.TemporaryDirectory() as tmp:
                src, dst = Path(tmp) / 'source.sql', Path(tmp) / 'normalized.sql'
                src.write_bytes(raw)
                plan = validate_file(src, parser_module(), dst)
                self.assertEqual({'action': 'vider'}, plan['table_decisions']['wp_' + table])
                self.assertNotIn(b'A28_FICTIVE_UNIT', dst.read_bytes())

    def test_refusal_receipt_exact_and_no_values(self):
        sys.modules.setdefault('legacy_importer', parser_module())
        spec = importlib.util.spec_from_file_location('a28_inside_subject', TOOLS / 'inside.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        try:
            Policy({}, {'private_fluentform_submissions': {'action': 'garder', 'value': 'A28_PRIVATE_Jerome'}}).resolve(
                'private_fluentform_submissions', 'private_')
        except Refusal as error:
            receipt = module.failure_receipt(error)
        else:
            self.fail('Known form decision was accepted')
        self.assertEqual({'status': 'refused', 'data_verified': False, 'issues': ['FORM_MESSAGES_DECISION_REFUSED'],
                          'failure': {'stage': 'sql_preflight', 'code': 'FORM_MESSAGES_DECISION_REFUSED',
                                      'detail': {'table': 'fluentform_submissions'}}}, receipt)

    def test_provenance_captures_only_known_ids_and_transitive_revisions(self):
        from types import SimpleNamespace
        sys.modules.setdefault('legacy_importer', parser_module())
        spec = importlib.util.spec_from_file_location('a28_provenance_subject', TOOLS / 'inside.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.BASE = TOOLS
        calls = []
        def query(argv, **kwargs):
            calls.append(kwargs['data'])
            return SimpleNamespace(stdout=b'41\n43\t42\n42\t41\n99\t88\n')
        module.command = query
        self.assertEqual([41, 42, 43], module.form_post_provenance('wp_'))
        self.assertEqual(1, len(calls))
        self.assertNotIn(b'postmeta', calls[0])
        self.assertNotIn(b'post_content', calls[0])
        self.assertEqual(2, calls[0].count(b'BINARY post_type'))
        module.command = lambda *a, **kw: SimpleNamespace(stdout=b'99\t88\n')
        self.assertEqual([], module.form_post_provenance('wp_'))
        module.command = lambda *a, **kw: SimpleNamespace(stdout=b'-1\n')
        with self.assertRaises(Refusal):
            module.form_post_provenance('wp_')

    def test_dependency_in_actual_transfer(self):
        # Actual standalone importer copies the one shared JSON to PHP and Python consumers.
        spec = importlib.util.spec_from_file_location('a28_run_subject', TOOLS / 'run.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import tarfile
        import io
        payload, manifest = module.payload(False)
        with tarfile.open(fileobj=io.BytesIO(payload)) as tar:
            raw = (ROOT / 'wp/outils/staging/form-policy.json').read_bytes()
            self.assertEqual(raw, tar.extractfile('subject/form-policy.json').read())
            self.assertEqual(raw, tar.extractfile('opt/staging/form-policy.json').read())
        self.assertIn('wp/outils/staging/form-policy.json', manifest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
