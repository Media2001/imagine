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
            self.assertEqual(2 if code == 'ARCHIVE_PATH_EMPTY' else 1, rules[code]['count'], code)
        text = json.dumps(scan['report'])
        self.assertNotIn('ALICE', text)
        self.assertNotIn('NEVER_VALUE', text)
        self.assertIn('uploads/2026', text)
        self.assertEqual(11, scan['report']['entries'])

    def test_colon_preserved_but_drive_refused(self):
        if os.name == 'nt':
            self.skipTest('Exercé sur le vrai filesystem Linux par exercise_archive_reelle.py')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'content'
            archive.restore(io.BytesIO(fixture([('uploads/2026/fiction:photo.jpg', b'unchanged'), ('database.sql', b'x')])), target)
            self.assertEqual(b'unchanged', (target / 'uploads/2026/fiction:photo.jpg').read_bytes())
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(archive.Refusal, '^ARCHIVE_PATH_DRIVE$'):
                archive.restore(io.BytesIO(fixture([('C:/x', b'x'), ('database.sql', b'x')])), Path(tmp) / 'content')

    def test_case_only_needs_actual_target_probe(self):
        self.assertTrue(hasattr(archive, 'probe_case_sensitive'), 'Sonde réelle de la cible manquante')
        if os.name == 'nt':
            self.skipTest('Preuve positive Linux dans le runner jetable')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'content'
            raw = fixture([('uploads/2026/Photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B'), ('database.sql', b'x')])
            archive.restore(io.BytesIO(raw), target)
            self.assertEqual(b'A', (target / 'uploads/2026/Photo.jpg').read_bytes())
            self.assertEqual(b'B', (target / 'uploads/2026/photo.jpg').read_bytes())
            self.assertTrue(archive.probe_case_sensitive(target))

    def test_ordinary_refusal_has_full_count_and_first_safe_zone(self):
        raw = fixture([('uploads/2026/ALICE\\one.jpg', b'x'), ('uploads/2025/ALICE\\two.jpg', b'x'), ('database.sql', b'x')])
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            target = Path(tmp) / 'content'
            with self.assertRaises(archive.Refusal) as caught:
                archive.restore(io.BytesIO(raw), target)
            self.assertEqual('ARCHIVE_PATH_BACKSLASH', str(caught.exception))
            self.assertEqual(2, caught.exception.detail['count'])
            self.assertEqual('uploads/2026', caught.exception.detail['locations'][0]['zone'])
            self.assertNotIn('ALICE', json.dumps(caught.exception.detail))
            self.assertFalse(target.exists())

    def test_identical_duplicate_rejected_even_linux(self):
        raw = fixture([('uploads/2026/photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B'), ('database.sql', b'x')])
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            with self.assertRaisesRegex(archive.Refusal, '^ARCHIVE_PATH_DUPLICATE$'):
                archive.restore(io.BytesIO(raw), Path(tmp) / 'content')
    def test_cli_diagnose_bypasses_every_publication_prerequisite(self):
        import contextlib
        import publish
        from unittest.mock import patch
        raw = fixture([('package.json', b'{"WordPress":{"Version":"6.9.1"}}'),
                       ('database.sql', b'CREATE TABLE `wp_options` (`id` bigint) ENGINE=InnoDB;'),
                       ('uploads/2026/ALICE.jpg', b'x')])
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            path = Path(tmp) / 'fiction.wpress'
            path.write_bytes(raw)
            before = {p.relative_to(tmp).as_posix(): p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()}
            output = io.StringIO()
            with patch.object(sys, 'argv', ['publish.py', '--diagnose', '--operator-ced', '--archive', str(path)]), \
                 patch.object(publish, 'api', side_effect=AssertionError('SITE_FORBIDDEN')), \
                 patch.object(publish, 'call', side_effect=AssertionError('DOCKER_FORBIDDEN')), \
                 patch.object(publish, 'prepare_core', side_effect=AssertionError('DOWNLOAD_FORBIDDEN')), \
                 patch.object(publish, 'read_admin_password', side_effect=AssertionError('PASSWORD_FORBIDDEN')), \
                 contextlib.redirect_stdout(output):
                code = publish.main()
            report = json.loads(output.getvalue())
            self.assertEqual(1, code)  # missing required schema, not publication prerequisites
            self.assertIn('SCHEMA_INCOMPLET', report['blockers'])
            self.assertEqual([], report['created_sites'])
            self.assertNotIn('ALICE', output.getvalue())
            self.assertEqual(before, {p.relative_to(tmp).as_posix(): p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()})

    def test_manifest_sql_personal_secrets_all_collected_after_bad_paths(self):
        self.assertTrue((TOOLS / 'diagnosis.py').is_file(), 'Diagnostic manifeste/SQL/secrets manquant')
        import diagnosis
        sql = (b'CREATE TABLE `wp_options` (`id` bigint) ENGINE=InnoDB;'
               b'CREATE TABLE `wp_fiction_contacts` (`id` bigint,`email` text,`phone` text) ENGINE=InnoDB;'
               b'CREATE TABLE `wp_other_contacts` (`id` bigint,`nom` text) ENGINE=MyISAM;'
               b'INSERT INTO `wp_fiction_contacts` VALUES (1,\'sk_test_FICTION_SECRET\',\'ALICE_VALUE\');'
               b'DELETE FROM `wp_fiction_contacts`; UPDATE `wp_options` SET `id`=1;')
        raw = fixture([('uploads/2026/ALICE\\photo.jpg', b'x'), ('package.json', b'{"WordPress":{}}'),
                       ('database.sql', sql), ('mu-plugins/fiction/ALICE.php', b'<?php sk_test_FICTION_SECRET'),
                       ('themes/fiction/ALICE.php', b'<?php whsec_FICTION_SECRET')])
        report = diagnosis.diagnose(io.BytesIO(raw), '6.9.1')
        rules = {r['code']: r for r in report['rules']}
        self.assertEqual(2, rules['TABLE_PERSONNELLE_A_TRANCHER']['count'])
        self.assertEqual(2, rules['SQL_STATEMENT']['count'])
        self.assertEqual(1, rules['SOURCE_CORE_METADATA_REFUSED']['count'])
        self.assertEqual(2, rules['SECRET_OU_IDENTIFIANT']['count'])
        self.assertEqual(1, rules['SOURCE_SECRET_NEUTRALISABLE']['count'])
        self.assertFalse(rules['SOURCE_SECRET_NEUTRALISABLE']['blocking'])
        self.assertIn('wp_fiction_contacts', json.dumps(report))
        self.assertNotIn('ALICE', json.dumps(report))
        self.assertNotIn('FICTION_SECRET', json.dumps(report))
        self.assertIn('ARCHIVE_PATH_BACKSLASH', report['blockers'])
        self.assertIn('NON_INNODB_TABLE', report['warnings'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
