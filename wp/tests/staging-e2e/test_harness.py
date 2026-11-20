"""Local safety tests: no Docker/network/WordPress dependency."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('e2e_harness', ROOT / 'harness.py')
module = None
if (ROOT / 'harness.py').exists():
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


class HarnessSafetyTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(module, 'The isolated synthetic harness is not implemented')

    def good_inspection(self):
        return {
            'Name': '/imagine-staging-e2e-0123456789ab',
            'Config': {'Labels': {'org.imagine.synthetic-e2e': 'true'}, 'ExposedPorts': None},
            'HostConfig': {'NetworkMode': 'none', 'PortBindings': {},
                           'Privileged': False, 'Binds': None,
                           'CapDrop': ['ALL'], 'SecurityOpt': ['no-new-privileges']},
            'Mounts': [],
            'NetworkSettings': {'Ports': {}, 'Networks': {'none': {}}},
        }

    def test_accepts_unpublished_network_none_without_mounts(self):
        module.validate_inspection(self.good_inspection())

    def test_rejects_bridge_network(self):
        value = self.good_inspection()
        value['HostConfig']['NetworkMode'] = 'bridge'
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_even_one_mount(self):
        value = self.good_inspection()
        value['Mounts'] = [{'Type': 'volume', 'Name': 'not-ours'}]
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_any_published_port(self):
        value = self.good_inspection()
        value['HostConfig']['PortBindings'] = {'80/tcp': [{'HostPort': '9999'}]}
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_exposed_port_even_if_unpublished(self):
        value = self.good_inspection()
        value['Config']['ExposedPorts'] = {'80/tcp': {}}
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_unnamed_existing_site(self):
        value = self.good_inspection()
        value['Name'] = '/existing-site'
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_missing_ownership_label(self):
        value = self.good_inspection()
        value['Config']['Labels'] = {}
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_privileged_mode(self):
        value = self.good_inspection()
        value['HostConfig']['Privileged'] = True
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_missing_cap_drop(self):
        value = self.good_inspection()
        value['HostConfig']['CapDrop'] = []
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_secondary_network_even_with_none_hostconfig(self):
        value = self.good_inspection()
        value['NetworkSettings']['Networks']['bridge'] = {}
        with self.assertRaises(module.SafetyError):
            module.validate_inspection(value)

    def test_rejects_nonzero_inner_result(self):
        with self.assertRaises(module.SafetyError):
            module.validate_result({'mode': 'fixture-selftest', 'exit_code': 2, 'checks': []}, 'fixture-selftest')

    def test_rejects_wrong_mode_receipt(self):
        with self.assertRaises(module.SafetyError):
            module.validate_result({'mode': 'fixture-selftest', 'exit_code': 0, 'checks': [{'check': 'real', 'status': 'PASS'}]}, 'acceptance')

    def test_rejects_a_success_receipt_with_no_checks(self):
        with self.assertRaises(module.SafetyError):
            module.validate_result({'mode': 'fixture-selftest', 'exit_code': 0, 'checks': []}, 'fixture-selftest')

    def test_accepts_real_inner_receipt_with_explicit_untested(self):
        module.validate_result({'mode': 'fixture-selftest', 'exit_code': 0, 'checks': [
            {'check': 'actual', 'status': 'PASS'}, {'check': 'paid', 'status': 'NOT_TESTED'}]}, 'fixture-selftest')

    def test_only_public_artifacts_are_downloadable(self):
        for url in module.ARTIFACTS.values():
            self.assertTrue(url.startswith('https://'))
        self.assertEqual(6, len(module.ARTIFACTS))
        self.assertIn('contact-form-7.zip', module.ARTIFACTS)
        self.assertIn('wordpress-seo.zip', module.ARTIFACTS)
        self.assertIn('meta-box.zip', module.ARTIFACTS)

    def test_acceptance_cannot_claim_success_without_both_fidelity_proofs(self):
        value = {'mode': 'acceptance', 'exit_code': 0, 'checks': [{'check': 'actual', 'status': 'PASS'}]}
        with self.assertRaises(module.SafetyError):
            module.validate_result(value, 'acceptance')

    def test_windows_paths_translate_without_shell(self):
        self.assertEqual('/mnt/c/synthetic fixture', module.wsl_path('C:/synthetic fixture'))


if __name__ == '__main__':
    import datetime
    import hashlib
    import sys
    import uuid
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    target = ROOT / 'evidence' / ('safety-' + uuid.uuid4().hex[:12])
    target.mkdir(parents=True, exist_ok=False)
    receipt = {'mode': 'host-safety', 'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'tests_run': result.testsRun, 'successful': result.wasSuccessful(),
               'failures': [test.id() for test, _ in result.failures],
               'errors': [test.id() for test, _ in result.errors],
               'skips': [test.id() for test, _ in result.skipped],
               'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                           for name in ('test_harness.py', 'harness.py')}}
    (target / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'receipt': str(target.relative_to(ROOT) / 'result.json'), 'tests_run': result.testsRun,
                      'successful': result.wasSuccessful()}))
    sys.exit(0 if result.wasSuccessful() else 1)
