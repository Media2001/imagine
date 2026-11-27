"""Real Python mutation witnesses, confined to disposable scratch copies."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from test_report import fixture

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'wp/outils/bascule/a31/report.py'


class MutationTests(unittest.TestCase):
    def module(self, root, old, new):
        text = SOURCE.read_text(encoding='utf-8')
        self.assertEqual(text.count(old), 1)
        path = root / 'mutant.py'
        path.write_text(text.replace(old, new), encoding='utf-8')
        spec = importlib.util.spec_from_file_location('a31_disposable_mutant', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def report(self, base, r, storage='classic', markdown=None):
        audit = base / 'audit.json'
        audit.write_text(json.dumps({'sections': {'commerce': {'order_storage': 'classic'}}}), encoding='utf-8')
        out = base / 'out'
        out.mkdir()
        d = fixture()
        d['storage'] = storage
        d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
        raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
        (out / 'commandes.json').write_bytes(raw)
        (out / 'commandes.md').write_bytes(markdown if markdown is not None else r.MARKDOWN.encode('utf-8') + raw + b'```\n')
        return out, audit

    def test_missing_storage_guard_reproduces_admission(self):
        with tempfile.TemporaryDirectory(prefix='a31-mutation-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            r = self.module(base, "and data['storage'] == photo['sections']['commerce']['order_storage']", 'and True')
            out, audit = self.report(base, r, 'hpos')
            self.assertTrue(r.complete_report(out, audit))

    def test_missing_markdown_guard_reproduces_canary_admission(self):
        with tempfile.TemporaryDirectory(prefix='a31-mutation-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            r = self.module(base, "and (output / 'commandes.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\\n'", 'and True')
            out, audit = self.report(base, r, markdown=b'A31_PRIVATE_CANARY')
            self.assertTrue(r.complete_report(out, audit))

    def test_missing_binding_guard_reproduces_coherent_shutdown_admission(self):
        with tempfile.TemporaryDirectory(prefix='a31-mutation-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            r = self.module(base, 'set(digest) == files and digest == {', 'set(digest) == files or digest == {')
            out, audit = self.report(base, r)
            protocol = b'A31_OK commandes.json commandes.md\nA31_FINAL ' + json.dumps(
                {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}).encode('ascii') + b'\n'
            data = json.loads((out / 'commandes.json').read_bytes())
            data['counts']['natures']['autres'] = 7
            raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'commandes.json').write_bytes(raw)
            (out / 'commandes.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            self.assertTrue(r.complete_report(out, audit))
            self.assertTrue(r.final_binding(protocol, out))


if __name__ == '__main__':
    unittest.main()
