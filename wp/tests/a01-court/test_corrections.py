"""Regression orchestration for merged A-01 corrections; no external API."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parents[2] / 'outils/staging-court'
sys.path.insert(0, str(TOOLS))
import publish


class CleanupOrchestration(unittest.TestCase):
    def test_marker_write_then_runner_removal_failure_still_stops_site(self):
        events = []
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as directory:
            root = Path(directory)
            archive = root / 'fiction.wpress'
            archive.write_bytes(b'fiction only; external restore seam not exercised')
            site = {'slug': 'imagine-test-a01-correction', 'status': 'running',
                    'url': 'http://fixture.invalid:1234', 'port': 1234, 'php_version': '8.2',
                    'mcp_enabled': True, 'mcp_status': 'ready'}
            def api(method, path, payload=None):
                if method == 'GET' and not events:
                    events.append('lookup'); return {'code': 404}
                return {'code': 200, 'body': site}
            def call(args, *values, **kwargs):
                if '/var/www/html/.imagine-staging-verified.json' in args:
                    events.append('marker'); raise RuntimeError('MARKER_WRITE_REFUSED')
                return subprocess.CompletedProcess(args, 0, b'', b'')
            def stop(name):
                events.append('stop'); site['status'] = 'stopped'
                return {'status': site['status'], 'all_three_containers_stopped': True}
            def remove(name):
                events.append('remove'); raise RuntimeError('REMOVAL_NOT_PROVEN')
            with mock.patch.multiple(publish, ROOT=root, HERE=root, api=api, call=call,
                                     fresh_runner=lambda name: {}, offline_isolation=lambda name: {},
                                     runtime_core_preflight=lambda *args: {'ok': True},
                                     read_json=lambda *args: {'data_verified': True}, stop_site=stop,
                                     remove_owned=remove,
                                     guarded_publish=lambda *args: site.update(status='running') or {'full_staging_ready': True}), \
                 mock.patch('publication_preflight.collect', return_value={'tool_source_manifest': {}}), \
                 mock.patch.object(publish.getpass, 'getpass', return_value='fixture-only-random-password'), \
                 mock.patch.object(sys, 'argv', ['publish.py', '--archive', str(archive), '--operator-ced',
                                                '--name', site['slug'], '--production-url', 'https://source.invalid']):
                self.assertEqual(1, publish.main())
            report = json.loads(next(root.rglob('result.json')).read_text(encoding='utf-8'))
            self.assertEqual('stopped', site['status'], events)
            self.assertEqual(['marker', 'stop', 'remove'], events[-3:])
            self.assertEqual('MARKER_WRITE_REFUSED', report['cases'][0]['error'])
            self.assertEqual('stopped', report['cases'][0]['failure_stop_readback']['status'])
            self.assertEqual('REMOVAL_NOT_PROVEN', report['cleanup_errors'][0]['code'])
            self.assertEqual('FAIL', report['status'])


def load_inside():
    spec = importlib.util.spec_from_file_location('legacy_importer', TOOLS.parent / 'staging-wp-integration/worker/worker.py')
    legacy = importlib.util.module_from_spec(spec)
    sys.modules['legacy_importer'] = legacy
    spec.loader.exec_module(legacy)
    spec = importlib.util.spec_from_file_location('inside_correction', TOOLS / 'inside.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OfflineDiagnostics(unittest.TestCase):
    def test_truncated_archive_and_unsupported_sql_have_distinct_safe_receipts(self):
        module = load_inside()
        self.assertTrue(hasattr(module, 'execute_offline_request'), 'Structured offline failure receipt missing')
        import struct
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as directory:
            root = Path(directory)
            request = {'target_url': 'http://localhost:1234', 'production_url': 'https://production.invalid',
                       'password': 'fiction-only-password-0123456789', 'decisions': {}}
            core_path = root / 'core'
            (core_path / 'wp-content').mkdir(parents=True)
            (core_path / 'wp-includes').mkdir()
            (core_path / 'wp-includes/version.php').write_text("<?php\n$wp_version = '7.0.9';\n")
            results = []
            for name, payload in [('truncated', b'fiction'), ('sql', b'DELETE FROM `wp_options`;')]:
                archive = root / (name + '.wpress')
                if name == 'sql':
                    package = b'{"WordPress":{"Version":"7.0.9"}}'
                    payload = (struct.pack('255s14s12s4096s', b'database.sql', str(len(payload)).encode(), b'0', b'') + payload
                               + struct.pack('255s14s12s4096s', b'package.json', str(len(package)).encode(), b'0', b'') + package + bytes(4377))
                archive.write_bytes(payload)
                site = root / name
                with mock.patch.multiple(module, SITE=site, CORE=core_path, isolation=lambda: None), \
                     mock.patch.object(module, 'command', side_effect=AssertionError('Database/bootstrap must not run')):
                    results.append(module.execute_offline_request(str(archive), request, False))
            self.assertEqual(['ARCHIVE_TRUNCATED', 'SQL_DDL_UNSUPPORTED'], [r['failure']['code'] for r in results])
            self.assertEqual(['archive_restore', 'sql_preflight'], [r['failure']['stage'] for r in results])
            for result in results:
                self.assertFalse(result['data_verified'])
                self.assertNotIn('stderr', json.dumps(result))
                self.assertNotIn('DELETE', json.dumps(result))


class SourceCoreVersion(unittest.TestCase):
    def test_source_core_version_must_match_exactly_before_bootstrap(self):
        module = load_inside()
        self.assertTrue(hasattr(module, 'validate_core_version'), 'Strict source/core gate missing')
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as directory:
            version = Path(directory) / 'version.php'
            version.write_text("<?php\n$wp_version = '7.0.9';\n")
            with self.assertRaisesRegex(module.Refusal, '^SOURCE_CORE_VERSION_MISMATCH$'):
                module.validate_core_version(b'{"WordPress":{"Version":"6.9.1"}}', version)
            self.assertEqual({'source': '7.0.9', 'pinned': '7.0.9'}, module.validate_core_version(
                b'{"WordPress":{"Version":"7.0.9"}}', version))
            for package in (None, b'{}', b'{"WordPress":{"Version":709}}',
                            b'{"WordPress":{"Version":"7.0.9\\nSECRET"}}', b'not-json'):
                with self.assertRaises(module.Refusal):
                    module.validate_core_version(package, version)


class TableEngines(unittest.TestCase):
    def test_myisam_is_preserved_and_reported_without_general_sql_fallback(self):
        module = load_inside()
        sql = b'CREATE TABLE `wp_options` (`option_id` bigint) ENGINE=MyISAM;'
        try:
            plan = module.sql_plan(sql, table_engines={'INNODB', 'MYISAM'})
        except Exception as exc:
            self.fail('MyISAM import rejected instead of reported: ' + type(exc).__name__)
        self.assertEqual({'wp_options': 'MYISAM'}, plan['table_engines'])
        self.assertIn('MyISAM', plan['statements'][0])
        for suffix in (b' DATA DIRECTORY=\'/outside\'', b'; DELETE FROM `wp_options`', b'; CREATE TRIGGER `evil`'):
            with self.assertRaises(ValueError):
                module.sql_plan(sql[:-1] + suffix + b';', table_engines={'INNODB', 'MYISAM'})
        with self.assertRaises(ValueError):
            module.sql_plan(sql.replace(b'MyISAM', b'BLACKHOLE'), table_engines={'INNODB', 'MYISAM'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
