"""Non-régression des corrections arbitrées B00, sans réseau."""
import json
import subprocess
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from test_b00_construction import builder


class B00Corrections(unittest.TestCase):
    def test_initial_get_busy_is_retried(self):
        m = builder()
        calls, waits = [], []
        def api(method, path, payload=None):
            calls.append(method)
            if len(calls) == 1:
                raise m.StagingBusy('occupé')
            return {'slug': m.SLUG, 'status': 'running'}
        self.assertEqual(m.ensure_site(api, waits.append)['status'], 'running')
        self.assertEqual(calls, ['GET', 'GET'])
        self.assertTrue(waits)

    def test_followup_get_busy_does_not_repeat_creation(self):
        m = builder()
        calls, waits = [], []
        def api(method, path, payload=None):
            calls.append(method)
            if len(calls) == 1:
                raise HTTPError(path, 404, 'absent', {}, None)
            if len(calls) == 2:
                return {'slug': m.SLUG, 'status': 'creating'}
            if len(calls) == 3:
                raise m.StagingBusy('occupé')
            return {'slug': m.SLUG, 'status': 'running'}
        self.assertEqual(m.ensure_site(api, waits.append)['status'], 'running')
        self.assertEqual(calls, ['GET', 'POST', 'GET', 'GET'])
        self.assertEqual(calls.count('POST'), 1)

    def test_api_read_busy_retries_at_transport_boundary(self):
        m = builder()
        with patch.object(m, 'urlopen', side_effect=[HTTPError('x', 423, 'busy', {}, None), HTTPError('x', 404, 'absent', {}, None)]), patch.object(m.time, 'sleep') as sleep:
            with self.assertRaises(HTTPError) as result:
                m.request_api('GET', '/api/sites/' + m.SLUG)
            self.assertEqual(result.exception.code, 404)
            self.assertEqual(sleep.call_count, 1)

    def test_exhausted_read_is_bounded_and_handled(self):
        m = builder()
        waits = []
        def api(*args):
            raise m.StagingBusy('occupé')
        with self.assertRaisesRegex(m.StagingBusy, 'lecture'):
            m.ensure_site(api, waits.append)
        self.assertGreater(len(waits), 3)
        self.assertLessEqual(len(waits), 180)

    def test_remote_mutations_retry_three_times_not_nested(self):
        m = builder()
        busy = subprocess.CompletedProcess([], 0, json.dumps({'busy': True}), '')
        ok = subprocess.CompletedProcess([], 0, json.dumps({'written': 'imagine-demo-build/test'}), '')
        with patch.object(m.subprocess, 'run', side_effect=[busy, busy, busy, ok]) as run, patch.object(m.time, 'sleep') as sleep:
            self.assertIn('written', m.upload('imagine-demo-build/test', b'x'))
            self.assertEqual(run.call_count, 4)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [300, 300, 300])

    def test_remote_mutation_exhaustion_is_exactly_four_attempts(self):
        m = builder()
        busy = subprocess.CompletedProcess([], 0, json.dumps({'busy': True}), '')
        with patch.object(m.subprocess, 'run', return_value=busy) as run, patch.object(m.time, 'sleep') as sleep:
            with self.assertRaises(m.StagingBusy):
                m.wp('option', 'update', 'fictive', '1')
            self.assertEqual(run.call_count, 4)
            self.assertEqual(sleep.call_count, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
