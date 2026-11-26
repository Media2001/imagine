"""Publication contract, exercised without PHP or WordPress."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / 'wp/outils/bascule/a26/report.py'


def load():
    if not PATH.is_file():
        raise AssertionError('A26 closed publication validator is not implemented')
    spec = importlib.util.spec_from_file_location('a26_report', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(r):
    services = {k: 0 for k in r.SERVICES}
    return {'schema': 'imagine-a26-third-parties-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'families': {k: {'active': 0, 'identifier': 'non'} for k in r.FAMILIES},
            'content': {'all': dict(services), 'selection': {'mode': 'annee', 'years': [], 'last_ten': None}},
            'audit_sha256': '0' * 64}


class ReportTests(unittest.TestCase):
    def test_nominal_closed_projection(self):
        r = load()
        self.assertTrue(r.projection(fixture(r), '0' * 64))

    def test_untrusted_fields_and_counts_fail_closed(self):
        r = load()
        for path in [('schema',), ('storage',), ('families', 'mesure', 'active'), ('families', 'pixel', 'identifier'), ('content', 'all', 'youtube')]:
            for bad in ('A26_PRIVATE_CANARY', True, -1, 1.5, None, [], {}):
                d = fixture(r)
                target = d
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = bad
                self.assertFalse(r.projection(d, '0' * 64), (path, type(bad)))
        for path in [(), ('families',), ('families', 'pixel'), ('content',), ('content', 'all'), ('content', 'selection')]:
            d = fixture(r)
            target = d
            for key in path:
                target = target[key]
            target['A26_PRIVATE_CANARY'] = 'A26_PRIVATE_CANARY'
            self.assertFalse(r.projection(d, '0' * 64))

    def test_year_partition_and_last_ten_subset(self):
        r = load()
        d = fixture(r)
        d['content']['all']['youtube'] = 1
        self.assertFalse(r.projection(d, '0' * 64))
        d['content']['selection']['years'] = [{'year': 2026, 'counts': dict(d['content']['all'])}]
        self.assertTrue(r.projection(d, '0' * 64))
        d['content']['selection']['years'] *= 2
        self.assertFalse(r.projection(d, '0' * 64))
        d['content']['selection'] = {'mode': 'dix_derniers', 'years': [], 'last_ten': dict(d['content']['all'])}
        self.assertTrue(r.projection(d, '0' * 64))
        d['content']['selection']['last_ten']['vimeo'] = 1
        self.assertFalse(r.projection(d, '0' * 64))

    def test_neutralised_source_counts_unknown_not_zero(self):
        r = load()
        d = fixture(r)
        d['neutralisation'] = r.UNKNOWN
        d['families']['mesure'] = {'active': r.UNKNOWN, 'identifier': r.UNKNOWN}
        d['content'] = r.UNKNOWN
        self.assertTrue(r.projection(d, '0' * 64))
        d['neutralisation'] = 'observe'
        self.assertFalse(r.projection(d, '0' * 64))

    def test_files_and_shutdown_binding(self):
        r = load()
        with tempfile.TemporaryDirectory(prefix='a26-publication-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            audit = base / 'audit.json'
            audit.write_bytes(b'{}\n')
            out = base / 'out'
            out.mkdir()
            d = fixture(r)
            d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
            raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'tiers.json').write_bytes(raw)
            (out / 'tiers.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
            stdout = b'A26_OK tiers.json tiers.md\nA26_FINAL ' + json.dumps(digests).encode('ascii') + b'\n'
            self.assertTrue(r.complete_report(out, audit))
            self.assertTrue(r.final_binding(stdout, out))
            for name in ('tiers.json', 'tiers.md'):
                before = (out / name).read_bytes()
                (out / name).write_bytes(before + b'A26_FILE_PRIVATE_CANARY')
                self.assertFalse(r.complete_report(out, audit))
                self.assertFalse(r.final_binding(stdout, out))
                (out / name).write_bytes(before)
            # Still-valid counts and coherent Markdown must fail their pre-shutdown binding.
            d['families']['mesure'] = {'active': 1, 'identifier': 'oui'}
            raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'tiers.json').write_bytes(raw)
            (out / 'tiers.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            self.assertTrue(r.complete_report(out, audit))
            self.assertFalse(r.final_binding(stdout, out))
            (out / 'extra.txt').write_bytes(b'A26_FILE_PRIVATE_CANARY')
            self.assertFalse(r.complete_report(out, audit))
            self.assertFalse(r.final_binding(stdout, out))


if __name__ == '__main__':
    unittest.main()
