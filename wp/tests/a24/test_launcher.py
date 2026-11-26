"""Closed launcher refusals under each real Windows console context."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'wp/outils/bascule/a24/confine.py'


class LauncherTests(unittest.TestCase):
    def call(self, args, encoding='utf-8', script=SCRIPT):
        self.assertTrue(script.is_file(), 'mandatory A24 launcher is missing')
        return subprocess.run([sys.executable, '-B', str(script), *args], cwd=ROOT,
                              capture_output=True, text=True, encoding=encoding, errors='strict', timeout=30,
                              env={**os.environ, 'PYTHONIOENCODING': encoding,
                                   'PYTHONUTF8': '0' if encoding == 'cp1252' else '1',
                                   'PYTHONDONTWRITEBYTECODE': '1'})

    def test_missing_arguments(self):
        p = self.call([])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_USAGE\n'))

    def test_unrecognised_argument_does_not_echo_value(self):
        p = self.call(['--A24_PERSON_PRIVATE_CANARY=/secret/A24_PATH_PRIVATE_CANARY'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_USAGE\n'))

    def test_empty_original_and_duplicate_arguments(self):
        for args in (['--wp-path=', '--audit=x', '--output=x'],
                     ['--wp-path=x', '--wp-path=A24_PRIVATE_CANARY']):
            p = self.call(args)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_USAGE\n'))

    def test_cp1252_refusal_real_interpreter(self):
        p = self.call(['--bad=A24_PRIVATE_CANARY'], encoding='cp1252')
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_USAGE\n'))

    def test_missing_supervisor_is_closed(self):
        with tempfile.TemporaryDirectory(prefix='a24-missing-seam-', dir=os.environ.get('TMPDIR')) as tmp:
            dest = Path(tmp) / 'a24'
            dest.mkdir()
            for name in ('confine.py', 'refusals.json', 'report.py', 'country_codes.json'):
                self.assertTrue((SCRIPT.parent / name).is_file())
                (dest / name).write_bytes((SCRIPT.parent / name).read_bytes())
            p = self.call(['--wp-path=private', '--audit=private', '--output=private'], script=dest / 'confine.py')
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_SUPERVISOR_UNAVAILABLE\n'))


if __name__ == '__main__':
    unittest.main()
