"""22-Nov arbitrations: real core gate and explicit scripts-only profile."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_corrections import load_inside, TOOLS
sys.path.insert(0, str(TOOLS))
import publish


class ExpectedCore(unittest.TestCase):
    def test_selected_runtime_must_match_expected_without_bootstrap(self):
        module = load_inside()
        self.assertIn('expected', __import__('inspect').signature(module.validate_core_version).parameters,
                      'Expected core version parameter missing')
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as directory:
            version = Path(directory) / 'version.php'
            version.write_text("<?php\n$wp_version = '7.0.9';\n")
            with self.assertRaisesRegex(module.Refusal, '^PINNED_CORE_EXPECTED_VERSION_MISMATCH$'):
                module.validate_core_version(b'{"WordPress":{"Version":"7.0.9"}}', version, '6.9.1')
            versions = module.validate_core_version(b'{"WordPress":{"Version":"7.0.9"}}', version, '7.0.9')
            self.assertEqual({'source': '7.0.9', 'pinned': '7.0.9', 'expected': '7.0.9'}, versions)
            version.write_text("<?php\n$wp_version = '6.9.1';\n")
            self.assertEqual('6.9.1', module.validate_core_version(
                b'{"WordPress":{"Version":"6.9.1"}}', version, '6.9.1')['pinned'])

    def test_operator_default_refuses_wrong_runtime_before_site_or_archive(self):
        self.assertTrue(hasattr(publish, 'runtime_core_preflight'), 'Runtime selection gate missing')
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as directory:
            root = Path(directory)
            preflight = {'ok': False, 'stage': 'core_preflight',
                         'code': 'PINNED_CORE_EXPECTED_VERSION_MISMATCH',
                         'expected': '6.9.1', 'pinned': '7.0.9'}
            with mock.patch.multiple(publish, ROOT=root, HERE=root,
                    fresh_runner=lambda name: {}, offline_isolation=lambda name: {},
                    call=lambda *args, **kwargs: __import__('subprocess').CompletedProcess([], 0, b'', b''),
                    runtime_core_preflight=mock.Mock(return_value=preflight),
                    remove_owned=lambda name: {'name': name, 'absent': True}), \
                 mock.patch.object(publish, 'api', side_effect=AssertionError('No site mutation/lookup before core gate')) as api, \
                 mock.patch('publication_preflight.collect', return_value={'tool_source_manifest': {}}), \
                 mock.patch.object(publish.getpass, 'getpass', side_effect=AssertionError('No archive prompt before core gate')), \
                 mock.patch.object(sys, 'argv', ['publish.py', '--archive', str(root / 'never-open.wpress'),
                       '--operator-ced', '--name', 'imagine-test-a01-version', '--production-url', 'https://source.invalid']):
                self.assertEqual(1, publish.main())
                publish.runtime_core_preflight.assert_called_once()
                self.assertEqual('6.9.1', publish.runtime_core_preflight.call_args.args[1])
                api.assert_not_called()
            result = json.loads(next(root.rglob('result.json')).read_text())
            self.assertEqual(preflight, result['cases'][0]['runtime_core_preflight'])
            self.assertEqual('PINNED_CORE_EXPECTED_VERSION_MISMATCH', result['cases'][0]['error'])
            self.assertEqual('6.9.1', result['expected_core_version'])
            self.assertTrue(result['cleanup'][0]['absent'])


class ScriptsOnlyCapacity(unittest.TestCase):
    def test_capacity_receipt_must_prove_download_script_replay_and_rollback(self):
        self.assertTrue(hasattr(publish, 'script_capacity_probe'), 'Published script-only capacity probe missing')
        proof = {'ok': True, 'policy': 'deployment_scripts_only',
                 'file_mods_locked': True, 'admin_updates_denied': True,
                 'auto_updates_disabled': True, 'wordpress_download_sha256': 'a' * 64,
                 'wordpress_download_http': 200, 'woocommerce_egress_http': 200,
                 'script_deploy_readback': True, 'script_replay_idempotent': True,
                 'rollback_readback': True, 'owned_probe_files_absent': True}
        def response(value, code=0):
            return __import__('subprocess').CompletedProcess([], code,
                ('A01_CAPACITY=' + json.dumps(value) + '\n').encode(), b'')
        with mock.patch.object(publish, 'call', return_value=response(proof)):
            self.assertEqual(proof, publish.script_capacity_probe('imagine-test-a01-unit'))
        for key in ('file_mods_locked', 'admin_updates_denied', 'auto_updates_disabled',
                    'script_deploy_readback', 'script_replay_idempotent', 'rollback_readback', 'owned_probe_files_absent'):
            with mock.patch.object(publish, 'call', return_value=response({**proof, key: False})):
                self.assertFalse(publish.script_capacity_probe('imagine-test-a01-unit')['ok'], key)
        with mock.patch.object(publish, 'call', return_value=response(proof, 1)):
            self.assertFalse(publish.script_capacity_probe('imagine-test-a01-unit')['ok'])


class ReceiptGates(unittest.TestCase):
    def test_publication_verifier_rejects_different_expected_core(self):
        import verify_publication
        report = TOOLS.parents[2] / 'production/A-01/publication-22nov/79cef0705045/result.json'
        value = json.loads(report.read_bytes())
        value['expected_core_version'] = '6.9.1'
        original = Path.read_bytes
        def read(path):
            return json.dumps(value).encode() if path == report else original(path)
        with mock.patch.object(Path, 'read_bytes', read):
            with self.assertRaises(AssertionError):
                verify_publication.verify(report)

    def test_publication_verifier_rejects_false_script_capacity(self):
        import verify_publication
        report = TOOLS.parents[2] / 'production/A-01/publication-22nov/79cef0705045/result.json'
        value = json.loads(report.read_bytes())
        value['cases'][0]['script_update_capacity']['script_replay_idempotent'] = False
        original = Path.read_bytes
        def read(path):
            return json.dumps(value).encode() if path == report else original(path)
        with mock.patch.object(Path, 'read_bytes', read):
            with self.assertRaises(AssertionError):
                verify_publication.verify(report)


if __name__ == '__main__':
    unittest.main(verbosity=2)
