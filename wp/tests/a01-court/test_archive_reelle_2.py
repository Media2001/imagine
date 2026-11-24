"""Targeted A-01/2 attacks; positive archives come from real AI1WM."""
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/staging-court'))
import archive


def attack(path, data=b'x'):
    prefix, name = path.rsplit('/', 1) if '/' in path else ('', path)
    return struct.pack('255s14s12s4096s', name.encode(), str(len(data)).encode(), b'0', prefix.encode()) + data


class ArchiveReelle2(unittest.TestCase):
    def test_excluded_payloads_never_read_and_unknown_uploads_closed(self):
        raw = attack('./database.sql') + attack('uploads/wpallexport/contact.csv', b'NEVER_READ') + bytes(4377)
        class Guard(io.BytesIO):
            def read(self, n=-1):
                data = super().read(n)
                if b'NEVER_READ' in data:
                    raise AssertionError('Excluded payload read')
                return data
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            report = {}
            archive.restore(Guard(raw), Path(tmp) / 'content', report=report)
            self.assertFalse((Path(tmp) / 'content/uploads').exists())
            self.assertEqual(1, report['excluded'][0]['count'])
        report = archive.audit(io.BytesIO(attack('uploads/unknown-fixture/file.pdf') + attack('./database.sql') + bytes(4377)))['report']
        self.assertIn('UPLOADS_DIRECTORY_REVIEW_REQUIRED', report['blockers'])
        self.assertIn('unknown-fixture', json.dumps(report))
        for name in ('a.pdf', 'b.jpg'):
            self.assertFalse(archive.excluded('uploads/woocommerce_uploads/' + name))
        for name in ('a.csv', 'b.html', 'c', 'd.log', 'e.zip'):
            self.assertTrue(archive.excluded('uploads/woocommerce_uploads/' + name))
        self.assertTrue(archive.excluded('themes/fiction/backup.zip'))
        self.assertFalse(archive.excluded('uploads/2026/11/media.zip'))

    def test_realistic_limits_and_disk_checked_before_any_creation(self):
        self.assertGreaterEqual(archive.DEFAULT_MAX_BYTES, 50 * 1024**3)
        self.assertGreaterEqual(archive.DEFAULT_MAX_ENTRIES, 2000000)
        self.assertGreaterEqual(archive.DEFAULT_MAX_SQL_BYTES, 4 * 1024**3)
        raw = attack('./database.sql', b'abc') + bytes(4377)
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            target = Path(tmp) / 'content'
            with patch.object(archive.shutil, 'disk_usage', return_value=type('Disk', (), {'free': 0})()):
                with self.assertRaisesRegex(archive.Refusal, '^DISK_SPACE_INSUFFICIENT$'):
                    archive.restore(io.BytesIO(raw), target)
            self.assertFalse(target.exists())
        report = archive.audit(io.BytesIO(raw), max_sql_bytes=2)['report']
        self.assertIn('ARCHIVE_LIMIT', report['blockers'])
        self.assertEqual(3, report['database_bytes'])

    def test_root_prefix_normalized_only_at_start(self):
        for root in ('.', './'):
            raw = attack(root + '/package.json', b'{}') + attack(root + '/database.sql', b'x') + bytes(4377)
            scan = archive.audit(io.BytesIO(raw))
            self.assertEqual([], scan['report']['blockers'])
            self.assertEqual(b'{}', scan['package'])
        for path in ('plugins/a/./b.php', 'plugins/a/../b.php', './plugins/./a.php', './../x.php'):
            scan = archive.audit(io.BytesIO(attack(path) + attack('./database.sql') + bytes(4377)))
            self.assertTrue(set(scan['report']['blockers']) & {'ARCHIVE_PATH_DOT', 'ARCHIVE_PATH_PARENT'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
