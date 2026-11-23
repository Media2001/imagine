"""Reject incomplete or altered qualification evidence, not just truthy flags."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_publication
ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / os.getenv('A01_691_REPORT', 'production/A-01/publication-23nov/52170a14f7a7/result.json')


class QualificationReceipts(unittest.TestCase):
    def setUp(self):
        self.assertTrue(REPORT.is_file(), 'Complete 6.9.1 receipt required')
        self.value = json.loads(REPORT.read_bytes())
        # Immutable historical receipts exercise their schema, not changed code.
        # The default verifier remains strict; HistoricalReceiptBoundary proves it.
        self.assertEqual('HISTORICAL_SCHEMA_ONLY', verify_publication.verify(REPORT, historical_schema_only=True)['status'])

    def reject(self, change):
        change(self.value)
        original = Path.read_bytes
        def read(path):
            return json.dumps(self.value).encode() if path == REPORT else original(path)
        with mock.patch.object(Path, 'read_bytes', read):
            with self.assertRaises(AssertionError):
                verify_publication.verify(REPORT, historical_schema_only=True)

    def test_complete_baseline(self):
        self.assertEqual(4, len(self.value['cases']))

    def test_wrong_expected_version(self):
        self.reject(lambda v: v.update(expected_core_version='6.9.2'))

    def test_plugin_update_is_not_import_fidelity(self):
        self.reject(lambda v: v['cases'][0]['offline'].update(import_installed_or_updated_plugins=True))

    def test_minimum_warning_cannot_be_a_blocker(self):
        self.reject(lambda v: v['cases'][0]['offline']['warnings'][1].update(blocking=True))

    def test_woo_file_drift(self):
        self.reject(lambda v: v['cases'][0]['fixture']['source_files'].update({'plugins/woocommerce/woocommerce.php': '0' * 64}))

    def test_missing_subscriptions_cannot_be_claimed_as_tested(self):
        self.reject(lambda v: v['cases'][0]['publication']['probe']['versions'].update(subscriptions='9.4.1'))

    def test_guest_rights_drift(self):
        self.reject(lambda v: v['cases'][0]['publication']['probe']['fidelity']['rights'].update(guest=True))

    def test_core_must_precede_archived_content(self):
        self.reject(lambda v: v['cases'][0]['injection']['empty_target_core_before_archive_injection'].update(archive_content_absent=False))


class HistoricalReceiptBoundary(unittest.TestCase):
    def test_historical_schema_check_is_never_current_source_qualification(self):
        import inspect
        self.assertIn('historical_schema_only', inspect.signature(verify_publication.verify).parameters)
        result = verify_publication.verify(REPORT, historical_schema_only=True)
        self.assertEqual('HISTORICAL_SCHEMA_ONLY', result['status'])
        self.assertFalse(result['source_payloads_match_current_files'])
        self.assertFalse(result['full_staging_ready'])

    def test_default_keeps_strict_source_integrity(self):
        value = json.loads(REPORT.read_bytes())
        value['command_sources'][next(iter(value['command_sources']))] = '0' * 64
        original = Path.read_bytes
        with mock.patch.object(Path, 'read_bytes', lambda p: json.dumps(value).encode() if p == REPORT else original(p)):
            with self.assertRaisesRegex(AssertionError, 'COMMAND_SOURCE_DRIFT'):
                verify_publication.verify(REPORT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
