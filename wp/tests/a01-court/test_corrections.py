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


if __name__ == '__main__':
    unittest.main(verbosity=2)
