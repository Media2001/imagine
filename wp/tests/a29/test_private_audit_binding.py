"""Pure binding checks; no PHP/native execution is claimed here."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

v = load('a29_binding_verifier_tests', ROOT / 'wp/tests/a29/verify.py')
f = load('a29_binding_report_fixture_tests', ROOT / 'wp/tests/a29/test_report.py')

class PrivateAuditBindingTests(unittest.TestCase):
    def test_receipt_keeps_full_canonical_binding_without_raw_private_audit(self):
        self.assertTrue(hasattr(v, 'bound_report'), 'missing private-input-free verification')
        scratch = os.environ.get('TMPDIR', str(ROOT.parent / 'AppData/Local/hermes/cache/scratch'))
        with tempfile.TemporaryDirectory(prefix='a29-bindings-', dir=scratch) as temp:
            root = Path(temp)
            output = root / 'classic-tasks'
            output.mkdir()
            data = f.fixture()
            raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (output / 'taches.json').write_bytes(raw)
            (output / 'taches.md').write_bytes(f.r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            receipt = {'scope': 'native_private_audit_binding', 'audit_sha256': data['audit_sha256'],
                       'as_of_utc': data['as_of_utc'], 'storage': 'classic', 'native_audit_exit_code': 0,
                       'raw_input_erased': True, 'private_canary_present': True,
                       'native_complete_reports': {'classic-tasks': True}, 'exit_code': 0}
            path = root / 'binding.json'
            def check(value):
                path.write_text(json.dumps(value), encoding='utf-8')
                return v.bound_report(output, path, f.r)
            self.assertTrue(check(receipt))
            for key, value in [('audit_sha256', '1' * 64), ('as_of_utc', '2026-11-27T12:00:00+00:00'),
                               ('storage', 'hpos'), ('native_audit_exit_code', 1), ('raw_input_erased', False),
                               ('native_complete_reports', {'classic-tasks': False}), ('exit_code', 1)]:
                mutated = copy.deepcopy(receipt)
                mutated[key] = value
                self.assertFalse(check(mutated), key)
            self.assertTrue(check(receipt))
            (output / 'taches.md').write_bytes(b'not canonical\n')
            self.assertFalse(check(receipt))
