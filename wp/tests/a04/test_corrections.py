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


class AuditCorrections(unittest.TestCase):
    def plan(self, audit=True):
        plan = MainFileCorrections().plan()
        step = {'component': 'fixture-box', 'main_file': 'entry.php',
                'before': '1.0', 'after': '2.0', 'archive': '/fixture.zip',
                'sha256': 'a' * 64, 'adapter': 'bootstrap-only', 'hooks': []}
        if audit:
            step['audit'] = {'component': 'fixture-box', 'path': '/audit/fixture.md',
                             'sha256': 'b' * 64, 'conclusion': 'no-deferred-database-migrations'}
        plan['steps'].append(step)
        return plan

    def test_bootstrap_only_without_audit_refused(self):
        with self.assertRaisesRegex(a04.Refusal, '^A04_AUDIT$'):
            a04.validate_plan(self.plan(audit=False))

    def test_named_audit_trace_accepted(self):
        plan = self.plan()
        try:
            self.assertEqual(a04.validate_plan(plan), plan)
        except a04.Refusal as error:
            self.fail('Named audit trace rejected: ' + str(error))

    def test_audit_must_name_this_component_and_explicit_conclusion(self):
        for key, value in [('component', 'different-plugin'), ('conclusion', 'unknown'),
                           ('path', 'relative.md'), ('sha256', ''), ('sha256', 'x' * 64)]:
            with self.subTest(key=key, value=value):
                plan = self.plan()
                plan['steps'][-1]['audit'][key] = value
                with self.assertRaisesRegex(a04.Refusal, '^A04_AUDIT$'):
                    a04.validate_plan(plan)

    def test_custom_adapter_after_first_four_stays_refused(self):
        plan = self.plan()
        plan['steps'][-1]['adapter'] = 'fixture-box'
        with self.assertRaisesRegex(a04.Refusal, '^A04_ADAPTER$'):
            a04.validate_plan(plan)

    def test_audit_file_readback_detects_changed_or_missing_evidence(self):
        self.assertTrue(hasattr(a04, 'check_audit'), 'Audit bytes must be checked before bootstrap')
        with tempfile.TemporaryDirectory(prefix='a04-audit-') as temp:
            path = pathlib.Path(temp).resolve() / 'fiction.md'
            path.write_text('fixture-box: synthetic header-only plugin, no deferred migration')
            audit = {'component': 'fixture-box', 'path': str(path),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'conclusion': 'no-deferred-database-migrations'}
            a04.check_audit(audit)
            path.write_text('changed')
            with self.assertRaisesRegex(a04.Refusal, '^A04_AUDIT_HASH$'):
                a04.check_audit(audit)
            path.unlink()
            with self.assertRaisesRegex(a04.Refusal, '^A04_AUDIT_FILE$'):
                a04.check_audit(audit)

    def test_audit_symlink_parent_refused(self):
        self.assertTrue(hasattr(a04, 'check_audit'), 'Audit path must be checked before bootstrap')
        with tempfile.TemporaryDirectory(prefix='a04-audit-link-') as temp:
            root = pathlib.Path(temp).resolve()
            real = root / 'real'
            real.mkdir()
            path = real / 'fiction.md'
            path.write_text('fixture-box synthetic audit')
            link = root / 'link'
            link.symlink_to(real, target_is_directory=True)
            audit = {'component': 'fixture-box', 'path': str(link / path.name),
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'conclusion': 'no-deferred-database-migrations'}
            with self.assertRaisesRegex(a04.Refusal, '^A04_AUDIT_FILE$'):
                a04.check_audit(audit)


if __name__ == '__main__':
    unittest.main(verbosity=2)
