"""Publication contract, no site/archive/engine access in these tests."""
import importlib.util
import pathlib
import sys
import unittest

sys.dont_write_bytecode = True
TOOLS = pathlib.Path(__file__).resolve().parents[2] / 'outils/staging-court'
sys.path.insert(0, str(TOOLS))


class PublicationContract(unittest.TestCase):
    def module(self):
        self.assertTrue((TOOLS / 'publication.py').is_file(), 'Publication guard not implemented')
        spec = importlib.util.spec_from_file_location('publication', TOOLS / 'publication.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_unverified_data_never_reaches_injection_or_start(self):
        module = self.module()
        calls = []
        outcome = module.guarded_publish({'data_verified': False},
                                         lambda: calls.append('inject'),
                                         lambda: calls.append('start'),
                                         lambda: calls.append('probe'))
        self.assertEqual([], calls)
        self.assertEqual('REFUSED_OFFLINE', outcome['status'])


    def verified(self):
        return {'data_verified': True, 'steps': [
            {'phase': phase, 'exit': 0, 'report': {'ok': True}}
            for phase in ('neutraliser', 'anonymiser', 'verifier')]}

    def test_data_flag_without_native_three_receipts_denied(self):
        module = self.module()
        calls = []
        result = module.guarded_publish({'data_verified': True},
            lambda: calls.append('inject'), lambda: calls.append('start'), lambda: {'ok': True})
        self.assertEqual([], calls)
        self.assertEqual('REFUSED_OFFLINE', result['status'])

    def test_failed_runtime_is_stopped_and_not_verified(self):
        module = self.module()
        calls = []
        result = module.guarded_publish(self.verified(),
                                        lambda: calls.append('inject'),
                                        lambda: calls.append('start'),
                                        lambda: {'ok': False},
                                        lambda: calls.append('stop'))
        self.assertEqual(['inject', 'start', 'stop'], calls)
        self.assertEqual('REFUSED_RUNTIME', result['status'])


    def test_name_scope_is_enforced_before_any_api(self):
        module = self.module()
        self.assertTrue(hasattr(module, 'validate_name'), 'Named-test scope guard missing')
        for name in ['imagine', 'imagine-test-', '../imagine-test-a', 'Imagine-test-a', 'imagine-test-a/../x', 'imagine-test-' + 'a' * 40, 'imagine-test-a--b', 'imagine-test-a-']:
            with self.assertRaises(ValueError):
                module.validate_name(name)
        self.assertEqual('imagine-test-a01-22', module.validate_name('imagine-test-a01-22'))


    def test_success_runs_injection_start_then_probe(self):
        calls = []
        result = self.module().guarded_publish(self.verified(),
            lambda: calls.append('inject'), lambda: calls.append('start'),
            lambda: calls.append('probe') or {'ok': True}, lambda: calls.append('stop'))
        self.assertEqual(['inject', 'start', 'probe'], calls)
        self.assertTrue(result['full_staging_ready'])

    def test_bad_phase_exit_or_order_never_injects(self):
        for mutation in ('exit', 'order', 'report', 'truthy_flag'):
            value = self.verified()
            if mutation == 'exit': value['steps'][2]['exit'] = 1
            if mutation == 'order': value['steps'].reverse()
            if mutation == 'report': value['steps'][2]['report']['issues'] = ['SECRET_OU_IDENTIFIANT']
            if mutation == 'truthy_flag': value['data_verified'] = 'true'
            calls = []
            outcome = self.module().guarded_publish(value, lambda: calls.append('inject'),
                lambda: calls.append('start'), lambda: {'ok': True})
            self.assertEqual([], calls, mutation)
            self.assertFalse(outcome['full_staging_ready'])

    def test_injection_exception_stops(self):
        calls = []
        def broken(): raise RuntimeError('SYNTHETIC_FAILURE')
        with self.assertRaises(RuntimeError):
            self.module().guarded_publish(self.verified(), broken, lambda: calls.append('start'),
                                         lambda: {'ok': True}, lambda: calls.append('stop'))
        self.assertEqual(['stop'], calls)

    def test_probe_exception_stops(self):
        calls = []
        def broken(): raise RuntimeError('SYNTHETIC_FAILURE')
        with self.assertRaises(RuntimeError):
            self.module().guarded_publish(self.verified(), lambda: calls.append('inject'),
                lambda: calls.append('start'), broken, lambda: calls.append('stop'))
        self.assertEqual(['inject', 'start', 'stop'], calls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
