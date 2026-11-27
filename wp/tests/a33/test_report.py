"""A33 closed schema and real Windows refusal boundaries."""
import hashlib
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
TOOLS = ROOT / 'wp/outils/bascule/a33'
spec = importlib.util.spec_from_file_location('a33report', TOOLS / 'report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def valid():
    empty = {'count': 0, 'present': 0, 'missing': 0, 'known_bytes': 0, 'total_bytes': 0}
    return {'schema': 'imagine-a33-archives-v1', 'read_only': True, 'imported': False, 'selected_issues': 10,
            'published_outside': [{'type': 'article', 'type_group': 0, 'year': 2010, 'count': 2}],
            'outside_media_by_year': [{'year': 2010, 'files': {'count': 2, 'present': 1, 'missing': 1, 'known_bytes': 7, 'total_bytes': 'inconnu fichiers absents'}}],
            'orphan_media': dict(empty), 'recent_media': dict(empty), 'other_media': dict(empty),
            'excluded_directories_bytes': 'non évalué', 'audit_sha256': 'a' * 64, 'mapping_sha256': 'b' * 64}


class ReportTests(unittest.TestCase):
    def test_nominal(self):
        self.assertTrue(r.projection(valid(), 'a' * 64, 'b' * 64))

    def test_distinct_unknown_types_not_merged(self):
        d = valid()
        d['published_outside'] = [{'type': 'autre', 'type_group': i, 'year': 2023, 'count': 1} for i in (1, 2)]
        self.assertTrue(r.projection(d, 'a' * 64, 'b' * 64))
        d['published_outside'][1]['type_group'] = 1
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_imported_unknown_not_zero(self):
        d = valid()
        d.update(imported=True, excluded_directories_bytes=r.UNKNOWN)
        d['outside_media_by_year'][0]['files']['total_bytes'] = r.UNKNOWN
        self.assertTrue(r.projection(d, 'a' * 64, 'b' * 64))
        d['excluded_directories_bytes'] = 0
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_missing_never_zero(self):
        d = valid()
        d['outside_media_by_year'][0]['files']['total_bytes'] = 0
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_count_consistency(self):
        d = valid()
        d['outside_media_by_year'][0]['files']['count'] = 3
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_bool_float_negative_oversized_closed(self):
        for v in (True, 0.1, -1, 2**60):
            d = valid()
            d['selected_issues'] = v
            self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_type_never_site_controlled(self):
        d = valid()
        d['published_outside'][0]['type'] = 'A33_TYPE_CANARY'
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_duplicate_groups_rejected(self):
        d = valid()
        d['published_outside'] *= 2
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_year_closed(self):
        for v in ('A33_YEAR_CANARY', True, 0, 999):
            d = valid()
            d['published_outside'][0]['year'] = v
            self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_extra_title_path_rejected_all_levels(self):
        for target in ('root', 'group', 'media'):
            d = valid()
            where = {'root': d, 'group': d['published_outside'][0], 'media': d['orphan_media']}[target]
            where['title'] = 'A33_CANARY'
            self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_duplicate_nonfinite_json_rejected(self):
        for text in ('{"x":1,"x":1}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                r.read(text)

    def test_no_more_than_ten(self):
        d = valid()
        d['selected_issues'] = 12
        self.assertFalse(r.projection(d, 'a' * 64, 'b' * 64))

    def test_hash_binding(self):
        self.assertFalse(r.projection(valid(), 'c' * 64, 'b' * 64))
        self.assertFalse(r.projection(valid(), 'a' * 64, 'c' * 64))

    def test_zero_present_is_not_absence(self):
        self.assertTrue(r.media({'count': 1, 'present': 1, 'missing': 0, 'known_bytes': 0, 'total_bytes': 0}, False))

    def test_actual_file_channel_tampering(self):
        scratch = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local')) / 'hermes/cache/scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='a33-report-test-', dir=scratch) as td:
            p = Path(td)
            audit, mapping = p / 'audit.json', p / 'map.json'
            audit.write_bytes(b'{}')
            mapping.write_bytes(b'{}')
            out = p / 'out'
            out.mkdir()
            d = valid()
            d['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
            d['mapping_sha256'] = hashlib.sha256(mapping.read_bytes()).hexdigest()
            raw = (json.dumps(d, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
            (out / 'archives.json').write_bytes(raw)
            (out / 'archives.md').write_bytes(r.MARKDOWN.encode('utf-8') + raw + b'```\n')
            binding = b'A33_OK archives.json archives.md\nA33_FINAL ' + json.dumps({f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir()}, separators=(',', ':')).encode() + b'\n'
            self.assertTrue(r.complete_report(out, audit, mapping))
            self.assertTrue(r.final_binding(binding, out))
            (out / 'archives.md').write_bytes(b'A33_FILE_CANARY')
            self.assertFalse(r.complete_report(out, audit, mapping))
            self.assertFalse(r.final_binding(binding, out))


class LauncherTests(unittest.TestCase):
    def invoke(self, args):
        return subprocess.run([sys.executable, '-B', str(TOOLS / 'confine.py'), *args], capture_output=True, text=True, encoding='utf-8', errors='strict', timeout=20,
                              env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})

    def test_mapping_required(self):
        p = self.invoke([])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A16_MAPPING_REQUIRED\n'))

    def test_unknown_argument_never_echoed(self):
        p = self.invoke(['--A33_PRIVATE_CANARY=C:/secret/é'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A33_USAGE\n'))

    def test_duplicate_refused(self):
        p = self.invoke(['--wp-path=x', '--wp-path=y'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A33_USAGE\n'))

    def test_missing_site_closed(self):
        p = self.invoke(['--wp-path=A33_MISSING_CANARY', '--audit=x', '--correspondance=x', '--output=x'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A33_CONFINEMENT_FAILED\n'))


if __name__ == '__main__':
    unittest.main()
