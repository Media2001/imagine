"""Verifier boundary doubles only; these are not native proof receipts."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a28_delivery_verifier', ROOT / 'production/A-28/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifierControls(unittest.TestCase):
    def test_baseline_requires_actual_exit_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.runner_fixture(root)
            data = json.loads((root / 'runner.json').read_bytes())
            data['commands'] = []
            (root / 'runner.json').write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'RUNNER_COMMANDS'):
                v.runner_contract(root, root, baseline=True)

    def runner_fixture(self, root):
        iso = {'network': 'none', 'mounts': [], 'ports': [], 'privileged': False, 'no_new_privileges': True, 'cap_drop': ['ALL']}
        keys = ['native', 'a01-python', 'a01-data', 'a01-test_database_policy', 'a01-test_diagnostics',
                'a01-test_native_file_policy', 'unit', 'lint']
        commands = []
        empty = hashlib.sha256(b'').hexdigest()
        for key in keys:
            for stream in ('stdout', 'stderr'):
                (root / (key + '.' + stream + '.log')).write_bytes(b'')
            commands.append({'key': key, 'exit': 0, 'stdout_sha256': empty, 'stderr_sha256': empty})
        (root / 'owned.py').write_bytes(b'ORIGINAL')
        data = {'status': 'PASS', 'synthetic_only': True, 'sources_unchanged': True,
                'owner_label': 'org.imagine.a28-synthetic', 'runner': 'a28-boundary-double',
                'cleanup': {'name': 'a28-boundary-double', 'absent': True}, 'commands': commands,
                'isolation_before': iso, 'isolation_after': iso,
                'source_manifest': {'owned.py': hashlib.sha256(b'ORIGINAL').hexdigest()}}
        (root / 'runner.json').write_text(json.dumps(data), encoding='utf-8')
        (root / 'unit.json').write_text(json.dumps({'exit_code': 0, 'checks': [{'status': 'PASS'}]}), encoding='utf-8')
        (root / 'a01-data.json').write_text(json.dumps({'ok': True, 'cases': 9, 'assertions': 1}), encoding='utf-8')
        return data

    def test_current_sources_required_not_just_passing_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.runner_fixture(root)
            v.runner_contract(root, root)
            (root / 'owned.py').write_bytes(b'CHANGED')
            with self.assertRaisesRegex(ValueError, 'RUNNER_SOURCE_DRIFT'):
                v.runner_contract(root, root)

    def test_changed_log_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.runner_fixture(root)
            (root / 'native.stdout.log').write_bytes(b'A28_TAMPERED')
            with self.assertRaisesRegex(ValueError, 'RUNNER_LOG'):
                v.runner_contract(root, root)

    def test_nonzero_exit_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.runner_fixture(root)
            data['commands'][0]['exit'] = 1
            (root / 'runner.json').write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'RUNNER_EXIT'):
                v.runner_contract(root, root)

    def test_cleanup_not_assumed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = self.runner_fixture(root)
            data['cleanup']['absent'] = False
            (root / 'runner.json').write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'RUNNER_CLEANUP'):
                v.runner_contract(root, root)

    def test_readme_contract_preserves_exact_three_lines(self):
        lines = ['A28 one\n', 'A28 two\n', 'A28 three\n']
        raw = b'OLD\n```sh\nced command\n```\n' + ''.join(lines).encode()
        commands = ['```sh\nced command\n```']
        v.readme_contract(raw, lines, commands)
        v.readme_contract(raw + b'Other lot\n', lines, commands)
        for changed in (raw.replace(b'A28 one\n', b'A28 one\r\n'), raw + b'A28 two\n',
                        raw.replace(b'A28 three\n', b''), raw.replace(b'A28 one', b'A28 changed')):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'README_LINES'):
                v.readme_contract(changed, lines, commands)

    def test_ced_command_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'CED_COMMAND_CHANGED'):
            v.readme_contract(b'A28\n```sh\nchanged\n```', ['A28\n'], ['```sh\nced command\n```'])

    def test_native_count_is_hard_assertion(self):
        with self.assertRaisesRegex(ValueError, 'NATIVE_CHECKS'):
            v.native_contract({'status': 'PASS', 'synthetic_only': True, 'baseline': False,
                               'checks': [{'pass': True}], 'failed': 0, 'passed': 999})

    def test_empty_native_matrix_refused(self):
        with self.assertRaisesRegex(ValueError, 'NATIVE_MATRIX'):
            v.native_contract({'status': 'PASS', 'synthetic_only': True, 'baseline': False,
                               'checks': [{'pass': True}], 'failed': 0, 'passed': 1, 'cases': []})


if __name__ == '__main__':
    unittest.main(verbosity=2)
