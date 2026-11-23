"""Defensive archive unit tests: only fabricated in-memory payloads."""
import io
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

from archive import Refusal, restore


def entry(path, data=b'x'):
    parts = path.rsplit('/', 1)
    prefix, name = parts if len(parts) == 2 else ('', parts[0])
    return struct.pack('255s14s12s4096s', name.encode(), str(len(data)).encode(), b'0', prefix.encode()) + data


class ArchiveSafety(unittest.TestCase):
    def setUp(self):
        base = Path(os.environ.get('TMPDIR', '/opt/court/test-scratch'))
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.target = Path(self.temp.name) / 'content'

    def tearDown(self):
        self.temp.cleanup()

    def parse(self, data, **kwargs):
        return restore(io.BytesIO(data), self.target, **kwargs)

    def test_preserves_plugin_theme_upload_and_mu_bytes(self):
        values = {'plugins/fiction/main.php': b'<?php /* FICTIF */', 'themes/fiction/style.css': b'/* FICTION */',
                  'uploads/fiction.bin': bytes(range(256)), 'mu-plugins/fiction.php': b'<?php /* FICTION MU */'}
        data = entry('database.sql', b'FICTION SQL') + b''.join(entry(k,v) for k,v in values.items()) + bytes(4377)
        sql, package, count = self.parse(data)
        self.assertEqual(b'FICTION SQL', sql)
        self.assertEqual(5, count)
        for path, value in values.items():
            self.assertEqual(value, self.target.joinpath(path).read_bytes())

    def test_rejects_parent_traversal(self):
        with self.assertRaises(Refusal):
            self.parse(entry('../fiction') + bytes(4377))

    def test_rejects_absolute_path(self):
        with self.assertRaises(Refusal):
            self.parse(entry('/fiction') + bytes(4377))

    def test_rejects_windows_drive_path(self):
        with self.assertRaises(Refusal):
            self.parse(entry('C:/fiction') + bytes(4377))

    def test_rejects_identical_duplicate(self):
        with self.assertRaisesRegex(Refusal, '^ARCHIVE_PATH_DUPLICATE$'):
            self.parse(entry('plugins/fiction.php') + entry('plugins/fiction.php') + entry('database.sql') + bytes(4377))

    def test_rejects_truncated_payload(self):
        with self.assertRaises(Refusal):
            self.parse(entry('database.sql', b'FICTIF')[:-1])

    def test_rejects_trailing_bytes(self):
        with self.assertRaises(Refusal):
            self.parse(entry('database.sql') + bytes(4377) + b'FICTIF')

    def test_rejects_missing_database(self):
        with self.assertRaises(Refusal):
            self.parse(entry('uploads/fictif') + bytes(4377))

    def test_rejects_expansion_limit(self):
        with self.assertRaises(Refusal):
            self.parse(entry('database.sql', b'FICTIF') + bytes(4377), max_bytes=2)

    def test_rejects_root_configuration(self):
        with self.assertRaises(Refusal):
            self.parse(entry('wp-config.php') + entry('database.sql') + bytes(4377))

    def test_rejects_multisite(self):
        with self.assertRaises(Refusal):
            self.parse(entry('multisite.json') + entry('database.sql') + bytes(4377))

    def test_requires_fresh_content_directory(self):
        self.target.mkdir()
        with self.assertRaises(Refusal):
            self.parse(entry('database.sql') + bytes(4377))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ArchiveSafety)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    Path('/report/archive-safety.json').write_text(json.dumps({'tests': result.testsRun,
        'success': result.wasSuccessful(), 'failures': len(result.failures), 'errors': len(result.errors)}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
