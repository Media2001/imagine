"""Closed public projection, independent of PHP and the site."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SUBJECT = ROOT / 'wp/outils/bascule/a23'


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((SUBJECT / 'report.py').is_file(), 'closed report validator is missing')
        spec = importlib.util.spec_from_file_location('a23_report', SUBJECT / 'report.py')
        self.report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.report)
        self.tmp = tempfile.TemporaryDirectory(prefix='a23-contract-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audit = self.root / 'audit.json'
        self.audit.write_text('{}\n', encoding='utf-8')
        self.out = self.root / 'out'
        self.out.mkdir()
        pool = {'groups': [], 'autres': 0}
        section = {'accounts': 0, 'families': pool, 'emails': pool, 'logins': pool}
        self.data = {'schema': 'imagine-a23-reader-accounts-v1', 'read_only': True,
                     'storage': 'classic', 'neutralisation': 'observe',
                     'counts': {'readers': section, 'live_readers': section, 'without_commerce': pool},
                     'audit_sha256': hashlib.sha256(self.audit.read_bytes()).hexdigest()}
        self.data = json.loads(json.dumps(self.data))

    def save(self):
        raw = (json.dumps(self.data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
        (self.out / 'comptes.json').write_bytes(raw)
        (self.out / 'comptes.md').write_bytes(self.report.MARKDOWN.encode('utf-8') + raw + b'```\n')

    def test_valid_empty_counts(self):
        self.save()
        self.assertTrue(self.report.complete_report(self.out, self.audit))

    def test_extra_site_string_rejected(self):
        self.data['identity'] = 'A23_REPORT_PRIVATE_CANARY@example.org'
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_unknown_label_rejected(self):
        self.data['counts']['readers']['emails'] = {'groups': [{'label': 'A23_LABEL_PRIVATE_CANARY', 'accounts': 5}], 'autres': 0}
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_small_named_group_rejected(self):
        self.data['counts']['readers']['accounts'] = 2
        self.data['counts']['readers']['families'] = {'groups': [{'label': 'phpass', 'accounts': 2}], 'autres': 0}
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_duplicate_label_rejected(self):
        self.data['counts']['readers']['accounts'] = 10
        self.data['counts']['readers']['families'] = {'groups': [{'label': 'phpass', 'accounts': 5}] * 2, 'autres': 0}
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_markdown_shutdown_tamper_rejected(self):
        self.save()
        with (self.out / 'comptes.md').open('ab') as handle:
            handle.write(b'A23_MARKDOWN_PRIVATE_CANARY')
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_audit_hash_bound(self):
        self.save()
        self.audit.write_text('{"changed":true}', encoding='utf-8')
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_neutralised_blocks_must_be_unknown(self):
        self.data['neutralisation'] = 'inconnu après neutralisation'
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))
        for section in ('readers', 'live_readers'):
            for key in ('families', 'emails', 'logins'):
                self.data['counts'][section][key] = 'inconnu après neutralisation'
        self.save()
        self.assertTrue(self.report.complete_report(self.out, self.audit))

    def test_extra_file_rejected(self):
        self.save()
        (self.out / 'A23_FILE_PRIVATE_CANARY').write_text('private', encoding='utf-8')
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_bool_is_not_count(self):
        self.data['counts']['readers']['accounts'] = False
        self.save()
        self.assertFalse(self.report.complete_report(self.out, self.audit))

    def test_invalid_utf8_rejected(self):
        self.save()
        (self.out / 'comptes.json').write_bytes(b'\xff')
        self.assertFalse(self.report.complete_report(self.out, self.audit))


if __name__ == '__main__':
    unittest.main()
