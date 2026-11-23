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
    def test_ordinary_preflight_keeps_precise_rule_count(self):
        import publish
        import subprocess
        from unittest.mock import patch
        if os.name == 'nt':
            self.skipTest('Programme prévol Linux exécuté dans le runner')
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'fiction.wpress'
            source.write_bytes(fixture([('uploads/2026/ALICE\\1.jpg', b'x'), ('uploads/2026/ALICE\\2.jpg', b'x'),
                                        ('database.sql', b'x'), ('package.json', b'{"WordPress":{"Version":"6.9.1"}}')]))
            def local(args, data=None, **kwargs):
                # Execute the exact injected preflight as real Python, offline.
                return subprocess.run([sys.executable, '-'], input=data, capture_output=True, check=True)
            with patch.object(publish, 'call', side_effect=local):
                result = publish.archive_core_preflight('owned-test', str(source), '6.9.1')
            self.assertEqual('ARCHIVE_PATH_BACKSLASH', result['code'])
            self.assertEqual(2, result['detail']['count'])
            self.assertEqual('uploads/2026', result['detail']['locations'][0]['zone'])
            self.assertNotIn('ALICE', json.dumps(result))

    def test_injection_probes_actual_content_target_before_transfer(self):
        import inspect
        import publish
        source = inspect.getsource(publish.inject)
        self.assertIn('probe_case_sensitive', source)
        self.assertLess(source.index('probe_case_sensitive'), source.index('# Install/read back'))

    def test_case_sensitive_metadata_preflight_and_warning(self):
        import publish
        import subprocess
        from unittest.mock import patch
        if os.name == 'nt':
            self.skipTest('Prévol Linux')
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'fiction.wpress'
            source.write_bytes(fixture([('uploads/2026/Photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B'),
                                        ('uploads/2026/colon:fiction.jpg', b'C'),
                                        ('database.sql', b'x'), ('package.json', b'{"WordPress":{"Version":"6.9.1"}}')]))
            def local(args, data=None, **kwargs):
                return subprocess.run([sys.executable, '-'], input=data, capture_output=True, check=True)
            with patch.object(publish, 'call', side_effect=local):
                result = publish.archive_core_preflight('owned-test', str(source), '6.9.1')
            self.assertTrue(result['ok'])
            self.assertIn('ARCHIVE_PATH_CASE_ONLY', result['archive_report']['warnings'])
            self.assertIn('ARCHIVE_PATH_COLON', result['archive_report']['warnings'])
            self.assertTrue(result['archive_report']['target_case_sensitive'])

    def test_real_case_insensitive_host_refuses_case_only(self):
        if os.name != 'nt':
            self.skipTest('Branche négative exécutée sur NTFS hôte réel')
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
            if archive.probe_case_sensitive(tmp):
                self.skipTest('Ce dossier Windows est réellement sensible à la casse')
            raw = fixture([('uploads/2026/Photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B'), ('database.sql', b'x')])
            with self.assertRaisesRegex(archive.Refusal, '^ARCHIVE_CASE_INSENSITIVE_TARGET$'):
                archive.restore(io.BytesIO(raw), Path(tmp) / 'content')

    def test_symlink_case_neighbor_is_refused_before_writes(self):
        if os.name == 'nt':
            self.skipTest('Lien Unix réel dans le runner')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'actual').mkdir()
            (root / 'link').symlink_to(root / 'actual', target_is_directory=True)
            raw = fixture([('uploads/2026/Photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B'), ('database.sql', b'x')])
            with self.assertRaisesRegex(archive.Refusal, '^ARCHIVE_TARGET_SYMLINK$'):
                archive.restore(io.BytesIO(raw), root / 'link/content')
            self.assertEqual([], list((root / 'actual').iterdir()))
    def test_sql_options_and_decisions_inventory_without_values(self):
        import diagnosis
        sql = (b'CREATE TABLE `wp_options` (`option_name` varchar(100),`option_value` text) ENGINE=InnoDB;'
               b'CREATE TABLE `wp_fiction` (`id` bigint,`email` text) ENGINE=InnoDB;'
               b'INSERT INTO `wp_options` VALUES (\'home\',\'https://ALICE.invalid\'),(\'home\',\'https://ALICE.invalid\');')
        report = diagnosis.diagnose(io.BytesIO(fixture([('database.sql', sql), ('package.json', b'{"WordPress":{"Version":"6.9.1"}}')])),
                                    decisions={'wp_fiction': {'action': 'garder'}})
        rules = {r['code']: r for r in report['rules']}
        self.assertEqual(1, rules['OPTION_DUPLIQUEE']['count'])
        self.assertEqual(1, rules['URL_ABSENTE']['count'])
        self.assertNotIn('TABLE_PERSONNELLE_A_TRANCHER', rules)
        self.assertNotIn('ALICE', json.dumps(report))

    def test_all_metadata_errors_and_file_secret_assignments_are_counted(self):
        import diagnosis
        raw = fixture([('package.json', b'{"WordPress":{"Version":"INVALID_ALICE"}}'),
                       ('database.sql', b'DELETE FROM `wp_options`;'),
                       ('plugins/fiction/ALICE.php', b"<?php define('API_KEY', 'ALICE_OPAQUE');"),
                       ('uploads/2026/ALICE.json', b'{"password":"ALICE_OPAQUE"}')])
        report = diagnosis.diagnose(io.BytesIO(raw), expected='INVALID_ALICE')
        self.assertIn('SOURCE_CORE_METADATA_REFUSED', report['blockers'])
        self.assertIn('EXPECTED_CORE_VERSION_REFUSED', report['blockers'])
        self.assertEqual(2, next(r for r in report['rules'] if r['code'] == 'SECRET_OU_IDENTIFIANT')['count'])
        self.assertNotIn('ALICE', json.dumps(report))

    def test_real_cli_no_writes_and_no_network_even_on_valid_source(self):
        import subprocess
        import hashlib
        if os.name == 'nt':
            self.skipTest('CLI exact avec audit système Linux dans runner network=none')
        sql = b''.join(('CREATE TABLE `wp_' + table + '` (`id` bigint) ENGINE=InnoDB;').encode()
                       for table in ('options', 'users', 'usermeta', 'posts', 'postmeta', 'comments'))
        # URL gate is deliberately absent, so exit=1 remains a legitimate diagnostic.
        raw = fixture([('database.sql', sql), ('package.json', b'{"WordPress":{"Version":"6.9.1"}}'),
                       ('uploads/2026/Photo.jpg', b'A'), ('uploads/2026/photo.jpg', b'B')])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fiction.wpress'
            path.write_bytes(raw)
            before = {p.relative_to(tmp).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(tmp).rglob('*') if p.is_file()}
            program = '''import sys,runpy
forbidden={'open','os.mkdir','os.remove','os.rmdir','os.rename','subprocess.Popen','socket.connect','socket.__new__'}
def hook(event,args):
 if event=='open':
  mode=args[1];flags=args[2]
  if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & 0x643): raise AssertionError('FILE_WRITE_FORBIDDEN')
 elif event in forbidden: raise AssertionError('SIDE_EFFECT_FORBIDDEN')
sys.dont_write_bytecode=True
sys.addaudithook(hook)
sys.argv=ARGV
runpy.run_path(SCRIPT,run_name='__main__')
'''.replace('ARGV', repr(['publish.py', '--diagnose', '--operator-ced', '--archive', str(path)])).replace('SCRIPT', repr(str(TOOLS / 'publish.py')))
            p = subprocess.run([sys.executable, '-c', program], capture_output=True)
            self.assertEqual(1, p.returncode, p.stderr.decode())
            report = json.loads(p.stdout)
            self.assertIn('ARCHIVE_PATH_CASE_ONLY', report['warnings'])
            self.assertTrue(report['read_only'])
            self.assertEqual(before, {p.relative_to(tmp).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(tmp).rglob('*') if p.is_file()})


if __name__ == '__main__':
    unittest.main(verbosity=2)
