"""A04 correction regressions; run in the disconnected owned bench."""
import copy
import hashlib
import importlib.util
import pathlib
import tempfile
import time
import unittest

P = pathlib.Path('/subject/a04/update.py') if pathlib.Path('/subject').exists() else pathlib.Path(__file__).resolve().parents[2] / 'outils/bascule/a04/update.py'
spec = importlib.util.spec_from_file_location('a04_corrections', P)
a04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a04)


class BackupCorrections(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='a04-corrections-')
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name).resolve()
        self.site = self.root / 'site'
        self.site.mkdir()
        self.outside = self.root / 'backup'
        self.outside.mkdir()
        self.file = self.outside / 'fiction.sql'
        self.file.write_text('SYNTHETIC backup')

    def backup(self, path):
        entry = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        return {'site': str(self.site), 'created_at': int(time.time()), 'database': entry, 'files': dict(entry)}

    def test_real_external_backup_accepted(self):
        a04.check_backup(self.backup(self.file), self.site)

    def test_dotdot_resolving_inside_site_refused(self):
        inside = self.site / 'fiction.sql'
        inside.write_text('SYNTHETIC backup')
        path = self.outside / '..' / 'site' / inside.name
        with self.assertRaisesRegex(a04.Refusal, '^A04_BACKUP_LOCATION$'):
            a04.check_backup(self.backup(path), self.site)

    def test_parent_symlink_resolving_inside_site_refused(self):
        inside = self.site / 'fiction.sql'
        inside.write_text('SYNTHETIC backup')
        link = self.root / 'linked-site'
        link.symlink_to(self.site, target_is_directory=True)
        with self.assertRaisesRegex(a04.Refusal, '^A04_SYMLINK$'):
            a04.check_backup(self.backup(link / inside.name), self.site)

    def test_parent_symlink_to_external_backup_also_refused(self):
        link = self.root / 'linked-backup'
        link.symlink_to(self.outside, target_is_directory=True)
        with self.assertRaisesRegex(a04.Refusal, '^A04_SYMLINK$'):
            a04.check_backup(self.backup(link / self.file.name), self.site)

    def test_final_backup_symlink_refused(self):
        link = self.outside / 'linked.sql'
        link.symlink_to(self.file)
        with self.assertRaises(a04.Refusal):
            a04.check_backup(self.backup(link), self.site)


class MainFileCorrections(unittest.TestCase):
    def plan(self):
        steps = [{'component': k, 'before': '1.0', 'after': '2.0',
                  'archive': '/fixture.zip', 'sha256': 'a' * 64,
                  'adapter': k, 'hooks': [],
                  'main_file': None if k == 'core' else k + '.php'}
                 for k in a04.ORDER]
        steps[0].update(before='6.9.1', after='7.0.9')
        return {'schema': 'imagine-a04-v1', 'site_status': 'verified-staging', 'steps': steps}

    def test_explicit_main_file_plan_accepted(self):
        plan = self.plan()
        plan['steps'][1]['main_file'] = 'commerce-entry.php'
        try:
            self.assertEqual(a04.validate_plan(plan), plan)
        except a04.Refusal as error:
            self.fail('Explicit main_file declaration rejected: ' + str(error))

    def test_unsafe_or_ambiguous_main_file_refused(self):
        for value in ['', '../other.php', '/other.php', 'folder/../../other.php',
                      'folder\\other.php', 'https:entry.php', 'entry.txt', '.', None, 123]:
            with self.subTest(value=value):
                plan = self.plan()
                plan['steps'][1]['main_file'] = value
                with self.assertRaisesRegex(a04.Refusal, '^A04_MAIN_FILE$'):
                    a04.validate_plan(plan)

    def test_core_cannot_declare_plugin_main_file(self):
        plan = self.plan()
        plan['steps'][0]['main_file'] = 'index.php'
        with self.assertRaisesRegex(a04.Refusal, '^A04_MAIN_FILE$'):
            a04.validate_plan(plan)

    def test_missing_main_file_declaration_refused(self):
        plan = self.plan()
        del plan['steps'][1]['main_file']
        with self.assertRaisesRegex(a04.Refusal, '^A04_PLAN$'):
            a04.validate_plan(plan)

    def test_different_folder_and_main_file_metadata_and_installed_version(self):
        import zipfile
        with tempfile.TemporaryDirectory(prefix='a04-main-file-') as temp:
            root = pathlib.Path(temp)
            package = root / 'fiction.zip'
            with zipfile.ZipFile(package, 'w') as archive:
                archive.writestr('fixture-box/entry.php', '<?php\n/*\nPlugin Name: Fiction\nVersion: 2.0\n*/')
                archive.writestr('fixture-box/fixture-box.php', '<?php\n/*\nVersion: 99.0\n*/')
            try:
                metadata = a04.check_package(package, 'fixture-box', '2.0', '7.0.9', '8.2.36', main_file='entry.php')
                self.assertEqual(metadata['version'], '2.0')
                a04.overlay(package, root / 'site', 'fixture-box')
                self.assertEqual(a04.version(root / 'site', 'fixture-box', main_file='entry.php'), '2.0')
            except TypeError as error:
                self.fail('Explicit main_file identity not supported: ' + str(error))


if __name__ == '__main__':
    unittest.main(verbosity=2)
