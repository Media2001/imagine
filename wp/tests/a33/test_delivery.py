"""A33 packet evidence falsification contracts, independent of outer hashes."""
import copy
import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('a33delivery', Path(__file__).with_name('delivery.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def global_green():
    return {'pass': True, 'tests': 1204, 'failures': 0, 'errors': 0, 'skipped': 0,
            'tools': {'tools': 23, 'checks': 852, 'failures': 0, 'excluded': []},
            'packets': {'verified': 13, 'lots': sorted(d.PREVIOUS | {'A-33'}), 'failures': [], 'excluded': []}}


class DeliveryTests(unittest.TestCase):
    def test_green_global(self):
        self.assertTrue(d.global_valid(global_green(), True))

    def test_missing_pure_controls_refused(self):
        data = global_green()
        data['tools']['checks'] = 846
        self.assertFalse(d.global_valid(data, True))

    def test_hidden_packet_red_never_green_suite(self):
        data = global_green()
        data['packets']['failures'] = [{'lot': 'A-31', 'control': 'failure'}]
        self.assertFalse(d.global_valid(data, True))

    def test_no_packet_exclusion(self):
        data = global_green()
        data['packets']['excluded'] = [{'lot': 'A-33'}]
        self.assertFalse(d.global_valid(data, True))

    def test_declared_packet_total_exact(self):
        data = global_green()
        data['packets']['verified'] = 14
        self.assertFalse(d.global_valid(data, True))

    def test_self_must_run_before_ready(self):
        data = global_green()
        data['packets']['lots'].remove('A-33')
        data['packets']['verified'] -= 1
        self.assertFalse(d.global_valid(data, True))

    def test_native_missing_named_channel(self):
        rows = [{'check': x, 'status': 'PASS'} for x in sorted(d.REQUIRED_NATIVE - {'channel_file'})]
        self.assertFalse(d.checks_valid({'exit_code': 0, 'checks': rows}, d.REQUIRED_NATIVE))

    def test_native_red_not_hidden_by_exit(self):
        self.assertFalse(d.checks_valid({'exit_code': 0, 'checks': [{'check': 'native', 'status': 'FAIL'}]}))

    def test_duplicate_controls_refused(self):
        self.assertFalse(d.checks_valid({'exit_code': 0, 'checks': [{'check': 'native', 'status': 'PASS'}] * 2}))

    def test_readme_exact_owned_lines_only(self):
        contract = b'heading\r\nA33-PORTEE\r\ncommand\r\n'
        self.assertTrue(d.readme_valid(b'neighbour\n' + contract + b'other lot\n', contract))
        for raw in (contract.replace(b'A33-PORTEE', b'changed'), contract + b'command\r\n', contract.replace(b'command\r\n', b''), contract.replace(b'\r\n', b'\n')):
            self.assertFalse(d.readme_valid(raw, contract))

    def test_duplicate_global_result_refused(self):
        with self.assertRaises(ValueError):
            d.global_result('T01_RESULT {}\nT01_RESULT {}\n')


if __name__ == '__main__':
    unittest.main()
