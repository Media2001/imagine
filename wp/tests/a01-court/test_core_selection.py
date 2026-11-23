"""A-01 6.9.1 qualification: data-only selection and warning policy."""
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
from archive import restore, Refusal


def archive_bytes(package):
    stream = io.BytesIO()
    for name, value in [('database.sql', b'not executed'), ('package.json', package), ('plugins/fake/fake.php', b'<?php /* never execute */')]:
        prefix, filename = name.rsplit('/', 1) if '/' in name else ('', name)
        stream.write(struct.pack('255s14s12s4096s', filename.encode(), str(len(value)).encode(), b'0', prefix.encode()))
        stream.write(value)
    stream.write(bytes(4377))
    return stream.getvalue()


class CoreSelection(unittest.TestCase):
    def test_plugin_minima_only_warn_and_never_change_files(self):
        import core_source
        with tempfile.TemporaryDirectory(dir=os.getenv('TMPDIR')) as folder:
            content = Path(folder)
            plugin = content / 'plugins/fiction/fiction.php'
            plugin.parent.mkdir(parents=True)
            raw = b'<?php /*\nPlugin Name: Fictitious warning\nRequires at least: 99.0\nRequires PHP: 99.0\n*/'
            plugin.write_bytes(raw)
            warnings = core_source.plugin_warnings(content, '6.9.1', '8.2')
            self.assertEqual(['PLUGIN_REQUIRES_NEWER_WORDPRESS', 'PLUGIN_REQUIRES_NEWER_PHP'], [w['code'] for w in warnings])
            self.assertTrue(all(w['blocking'] is False for w in warnings))
            self.assertEqual(raw, plugin.read_bytes())

    def test_archive_version_selects_core_not_commercial_baseline(self):
        import core_source
        self.assertEqual('6.9.1', core_source.select_version(b'{"WordPress":{"Version":"6.9.1"}}', '6.9.1'))
        for package in (b'{}', b'not-json', b'{"WordPress":{"Version":"../7.0"}}'):
            with self.assertRaisesRegex(Refusal, '^SOURCE_CORE_METADATA_REFUSED$'):
                core_source.select_version(package, '6.9.1')
        with self.assertRaisesRegex(Refusal, '^SOURCE_EXPECTED_CORE_VERSION_MISMATCH$'):
            core_source.select_version(b'{"WordPress":{"Version":"7.0.9"}}', '6.9.1')

    def test_metadata_scan_never_restores_files_or_sql(self):
        package = b'{"WordPress":{"Version":"6.9.1"}}'
        with tempfile.TemporaryDirectory(dir=os.getenv('TMPDIR')) as folder:
            target = Path(folder) / 'must-not-exist'
            sql, found, count = restore(io.BytesIO(archive_bytes(package)), target, metadata_only=True)
            self.assertFalse(target.exists())
            self.assertIsNone(sql)
            self.assertEqual(package, found)
            self.assertEqual(3, count)


if __name__ == '__main__':
    unittest.main(verbosity=2)
