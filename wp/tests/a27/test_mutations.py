"""Mutation witnesses for publication guards, disposable Python copies only."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'wp/outils/bascule/a27/report.py'
CLOCK = '2026-11-26T12:00:00+00:00'


class MutationTests(unittest.TestCase):
    def module(self, root, replacement=None):
        text = SOURCE.read_text(encoding='utf-8')
        if replacement:
            old, new = replacement
            self.assertEqual(text.count(old), 1)
            text = text.replace(old, new)
        path = root / 'mutant.py'
        path.write_text(text, encoding='utf-8')
        spec = importlib.util.spec_from_file_location('a27_disposable_mutant', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_removed_storage_guard_reproduces_red(self):
        with tempfile.TemporaryDirectory(prefix='a27-red-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            r = self.module(base, ("and data['storage'] == photo['sections']['commerce']['order_storage']", 'and True'))
            audit = base / 'audit.json'
            audit.write_text(json.dumps({'generated_at_utc': CLOCK, 'sections': {'commerce': {'order_storage': 'classic'}}}), encoding='utf-8')
            out = base / 'out'
            out.mkdir()
            data = {'schema': 'imagine-a27-saved-payments-v1', 'read_only': True, 'storage': 'hpos',
                    'neutralisation': 'observe', 'as_of_utc': CLOCK, 'audit_sha256': hashlib.sha256(audit.read_bytes()).hexdigest(),
                    'counts': {k: {'groups': [], 'autres': 0} for k in r.COUNTS}}
            raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'paiements.json').write_bytes(raw)
            (out / 'paiements.md').write_bytes(r.MARKDOWN.encode() + raw + b'```\n')
            self.assertTrue(r.complete_report(out, audit), 'mutant must expose the rejected storage mismatch')

    def test_removed_markdown_guard_reproduces_file_leak(self):
        with tempfile.TemporaryDirectory(prefix='a27-red-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            r = self.module(base, ("and (output / 'paiements.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\\n'", 'and True'))
            audit = base / 'audit.json'
            audit.write_text(json.dumps({'generated_at_utc': CLOCK, 'sections': {'commerce': {'order_storage': 'classic'}}}), encoding='utf-8')
            out = base / 'out'
            out.mkdir()
            data = {'schema': 'imagine-a27-saved-payments-v1', 'read_only': True, 'storage': 'classic',
                    'neutralisation': 'observe', 'as_of_utc': CLOCK, 'audit_sha256': hashlib.sha256(audit.read_bytes()).hexdigest(),
                    'counts': {k: {'groups': [], 'autres': 0} for k in r.COUNTS}}
            raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'paiements.json').write_bytes(raw)
            (out / 'paiements.md').write_bytes(b'A27_REPORT_PRIVATE_CANARY')
            self.assertTrue(r.complete_report(out, audit), 'mutant must admit the private Markdown fixture')


if __name__ == '__main__':
    unittest.main()
