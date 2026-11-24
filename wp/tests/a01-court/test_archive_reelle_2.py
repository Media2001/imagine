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
    def test_real_manifest_settings_restore_and_unsafe_plugin_refusal(self):
        import diagnosis
        sys.modules['legacy_importer'] = diagnosis.parser_module()
        import inside
        self.assertTrue(hasattr(inside, 'manifest_settings_values'))
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            content = Path(tmp)
            (content / 'plugins/public').mkdir(parents=True)
            (content / 'plugins/public/main.php').write_text('<?php')
            (content / 'themes/fiction').mkdir(parents=True)
            manifest = {'Plugins':['public/main.php'], 'Template':'fiction', 'Stylesheet':'fiction'}
            values = inside.manifest_settings_values(json.dumps(manifest).encode(), content)
            self.assertEqual('fiction', values['template'])
            self.assertEqual('a:1:{i:0;s:15:"public/main.php";}', values['active_plugins'])
            manifest['Plugins'] = ['../outside.php']
            with self.assertRaisesRegex(archive.Refusal, '^SOURCE_SETTINGS_METADATA_REFUSED$'):
                inside.manifest_settings_values(json.dumps(manifest).encode(), content)

    def test_default_summary_is_short_and_detail_retains_locations(self):
        import diagnosis
        self.assertTrue(hasattr(diagnosis, 'format_summary'))
        report = {'status':'REFUSED','entries':49756,'total_bytes':2000000000,'database_bytes':150000000,
                  'rules':[{'code':'ARCHIVE_LIMIT','count':45376,'blocking':True,
                            'locations':[{'zone':'uploads/' + str(i),'count':1} for i in range(50)]}],
                  'inventory':{'plugins':['woocommerce'],'themes':['fiction'],'uploads':[{'directory':'2026','count':49756,'bytes':2000000000}]},'excluded':[]}
        output = diagnosis.format_summary(report)
        self.assertLess(len(output.splitlines()), 12)
        self.assertIn('45376', output)
        self.assertIn('BLOQUANT', output)
        self.assertNotIn('uploads/5', output)
        self.assertEqual(50, len(report['rules'][0]['locations']))

    def test_streamed_sql_and_targeted_nonblocking_secrets(self):
        import diagnosis
        sql = b'CREATE TABLE `wp_options` (`option_name` varchar(100),`option_value` text) ENGINE=InnoDB;'
        sql += b"INSERT INTO `wp_options` VALUES ('home','fiction'),('siteurl','fiction');"
        sql += b''.join(('CREATE TABLE `wp_' + t + '` (`id` bigint) ENGINE=InnoDB;').encode() for t in ('users','usermeta','posts','postmeta','comments'))
        raw = attack('./package.json', b'{"WordPress":{"Version":"6.9.1"}}') + attack('./database.sql', sql)
        for path in ('plugins/public/main.php', 'themes/public/style.php', 'uploads/2026/a.jpg', 'uploads/2026/a.mp3', 'mu-plugins/site.php', 'site.json'):
            raw += attack(path, b"<?php $api_key='FICTION_ONLY'; whsec_FICTION")
        report = diagnosis.diagnose(io.BytesIO(raw + bytes(4377)))
        rule = next(r for r in report['rules'] if r['code'] == 'SECRET_OU_IDENTIFIANT')
        self.assertEqual(2, rule['count'])
        self.assertFalse(rule['blocking'])
        self.assertEqual([], report['blockers'])
        from sql_stream import Framer
        statements = []
        framer = Framer(statements.append)
        malicious = b"INSERT INTO `wp_posts` VALUES ('fiction;CREATE TABLE `NEVER_VALUE` (`email` text)');"
        for offset in range(0, len(malicious), 7):
            framer.feed(malicious[offset:offset+7])
        framer.finish()
        self.assertEqual([malicious], statements)
        with self.assertRaisesRegex(archive.Refusal, '^SQL_STATEMENT_LIMIT$'):
            Framer(lambda statement: None, limit=8).feed(b"SELECT 'long';")
        for byte in range(len(malicious)):
            parts = []
            framed = Framer(parts.append)
            framed.feed(malicious[:byte]); framed.feed(malicious[byte:]); framed.finish()
            self.assertEqual([malicious], parts)

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
        named = archive.audit(io.BytesIO(attack('uploads/dossier fictif/file.pdf') + attack('./database.sql') + bytes(4377)))['report']
        self.assertEqual('dossier fictif', named['inventory']['uploads'][0]['directory'])
        self.assertIn('uploads/dossier fictif', json.dumps(named))
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
            import diagnosis
            sys.modules['legacy_importer'] = diagnosis.parser_module()
            import inside
            source = Path(tmp) / 'fixture.wpress'
            source.write_bytes(raw)
            with patch.object(archive.shutil, 'disk_usage', return_value=type('Disk', (), {'free': 0})()), \
                 patch.object(inside, 'database_start', side_effect=AssertionError('Must not create database before disk gate')) as start:
                refusal = inside.execute_offline_request(str(source), {}, True)
            self.assertEqual('DISK_SPACE_INSUFFICIENT', refusal['failure']['code'])
            start.assert_not_called()
            import publish
            self.assertTrue(hasattr(publish, 'archive_capacity_on_engine'))
            with patch.object(publish, 'call', return_value=__import__('subprocess').CompletedProcess([],0,b'/var/lib/docker\n',b'')), \
                 patch.object(publish, 'wsl_python', return_value={'free':0}):
                with self.assertRaisesRegex(RuntimeError, '^DISK_SPACE_INSUFFICIENT$'):
                    publish.archive_capacity_on_engine(source, {})
            from contextlib import redirect_stdout
            nonexistent = Path(tmp) / 'no-created-repository'
            output = io.StringIO()
            with patch.object(publish, 'ROOT', nonexistent), patch.object(publish, 'HERE', nonexistent), \
                 patch.object(publish, 'archive_capacity_on_engine', side_effect=RuntimeError('DISK_SPACE_INSUFFICIENT')), \
                 patch.object(sys, 'argv', ['publish.py','--operator-ced','--archive',str(source),
                     '--name','imagine-test-a01-no-space','--production-url','https://source.invalid']), redirect_stdout(output):
                self.assertEqual(1, publish.main())
            self.assertFalse(nonexistent.exists())
            self.assertEqual('DISK_SPACE_INSUFFICIENT', json.loads(output.getvalue())['blocker'])
            self.assertIsNone(json.loads(output.getvalue())['report'])
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
