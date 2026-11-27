"""Historical Windows evidence must be interpreted identically on Linux."""
import unittest
from matrix import environment_valid

ROOT = r'C:\Users\Ced\imagine'
SCRATCH = r'C:\Users\Ced\AppData\Local\hermes\cache\scratch\a30-captured'


def recorded():
    return {'platform': 'win32', 'stdout': 'cp1252', 'stderr': 'cp1252',
            'utf8_mode': 0, 'TMPDIR_present': False, 'TMPDIR': None,
            'TEMP': SCRATCH, 'TMP': SCRATCH, 'tempdir': SCRATCH,
            'repository_root_windows': ROOT, 'suite_discovered': 34}


class HistoricalWindowsTests(unittest.TestCase):
    def test_valid_windows_capture_is_readable_on_current_host(self):
        self.assertTrue(environment_valid(recorded(), 'cp1252', 0, SCRATCH))

    def test_root_inside_and_overlap_refused(self):
        for path in [ROOT, ROOT + r'\temporary', r'C:\Users\Ced']:
            with self.subTest(path=path):
                env = {**recorded(), **dict.fromkeys(('TEMP', 'TMP', 'tempdir'), path)}
                self.assertFalse(environment_valid(env, 'cp1252', 0, path))

    def test_missing_malformed_or_noncanonical_paths_refused(self):
        for path in ['relative', r'C:relative', '/tmp/a30', SCRATCH + r'\..\escape',
                     SCRATCH + r'\.', SCRATCH.replace('\\', '/'), SCRATCH + '\\']:
            for key in ['TEMP', 'TMP', 'tempdir', 'repository_root_windows']:
                with self.subTest(key=key, path=path):
                    self.assertFalse(environment_valid({**recorded(), key: path}, 'cp1252', 0, SCRATCH))
        env = recorded(); del env['repository_root_windows']
        self.assertFalse(environment_valid(env, 'cp1252', 0, SCRATCH))

    def test_mismatch_refused_and_windows_case_semantics_retained(self):
        for key in ['TEMP', 'TMP', 'tempdir']:
            self.assertFalse(environment_valid({**recorded(), key: SCRATCH + '-other'}, 'cp1252', 0, SCRATCH))
        self.assertFalse(environment_valid(recorded(), 'cp1252', 0, SCRATCH + '-other'))
        self.assertTrue(environment_valid({**recorded(), 'TMP': SCRATCH.upper()}, 'cp1252', 0, SCRATCH))


if __name__ == '__main__':
    unittest.main(verbosity=2)
