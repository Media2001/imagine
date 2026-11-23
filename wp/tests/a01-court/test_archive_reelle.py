"""Archives inventées uniquement : diagnostic intégral, sans valeurs ni extraction."""
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parents[2] / 'outils/staging-court'
sys.path.insert(0, str(TOOLS))
import archive


def entry(path, data=b'x'):
    prefix, name = path.rsplit('/', 1) if '/' in path else ('', path)
    return struct.pack('255s14s12s4096s', name.encode(), str(len(data)).encode(), b'0', prefix.encode()) + data


def fixture(items):
    return b''.join(entry(p, v) for p, v in items) + bytes(4377)


class ArchiveReelle(unittest.TestCase):
    def test_all_path_rules_counted_without_filename_or_values(self):
        self.assertTrue(hasattr(archive, 'audit'), 'Le diagnostic intégral manque')
        raw = fixture([
            ('uploads/2026/ALICE:photo.jpg', b'NEVER_VALUE'),
            ('uploads/2026/ALICE\\photo.jpg', b'x'),
            ('uploads/2026/ALICE\x7fphoto.jpg', b'x'),
            ('plugins/fiction/../../ALICE.php', b'x'),
            ('plugins/fiction//ALICE.php', b'x'),
            ('C:/ALICE.php', b'x'), ('/folder/ALICE.php', b'x'),
            ('wp-admin/ALICE.php', b'x'),
            ('uploads/2026/ALICE.jpg', b'x'), ('uploads/2026/ALICE.jpg', b'y'),
            ('database.sql', b'SYNTHETIC'),
        ])
        scan = archive.audit(io.BytesIO(raw))
        rules = {r['code']: r for r in scan['report']['rules']}
        for code in ('ARCHIVE_PATH_BACKSLASH', 'ARCHIVE_PATH_CONTROL', 'ARCHIVE_PATH_PARENT',
                     'ARCHIVE_PATH_EMPTY', 'ARCHIVE_PATH_DRIVE', 'ARCHIVE_PATH_ABSOLUTE',
                     'ARCHIVE_LAYOUT_UNSUPPORTED', 'ARCHIVE_PATH_DUPLICATE', 'ARCHIVE_PATH_COLON'):
            self.assertEqual(1, rules[code]['count'], code)
        text = json.dumps(scan['report'])
        self.assertNotIn('ALICE', text)
        self.assertNotIn('NEVER_VALUE', text)
        self.assertIn('uploads/2026', text)
        self.assertEqual(11, scan['report']['entries'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
