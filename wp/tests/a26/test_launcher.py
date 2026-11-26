"""Launcher refusal output stays closed, including Windows console contexts."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'wp/outils/bascule/a26/confine.py'


class LauncherTests(unittest.TestCase):
    def call(self, args, encoding='utf-8', script=SCRIPT):
        self.assertTrue(script.is_file(), 'mandatory A26 launcher is missing')
        return subprocess.run([sys.executable, '-B', str(script), *args], cwd=ROOT,
                              capture_output=True, text=True, encoding=encoding, errors='strict', timeout=30,
                              env={**os.environ, 'PYTHONIOENCODING': encoding,
                                   'PYTHONUTF8': '0' if encoding == 'cp1252' else '1',
                                   'PYTHONDONTWRITEBYTECODE': '1'})

    def test_missing_arguments(self):
        p = self.call([])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A26_USAGE\n'))

    def test_unrecognised_argument_does_not_echo_value(self):
        p = self.call(['--A26_PERSON_PRIVATE_CANARY=/secret/A26_PATH_PRIVATE_CANARY'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A26_USAGE\n'))

    def test_duplicate_argument(self):
        p = self.call(['--wp-path=first', '--wp-path=A26_SITE_PRIVATE_CANARY'])
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A26_USAGE\n'))

    def test_cp1252_refusal_real_interpreter(self):
        p = self.call(['--bad=A26_PRIVATE_CANARY'], encoding='cp1252')
        self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A26_USAGE\n'))

    def test_missing_supervisor_is_closed(self):
        with tempfile.TemporaryDirectory(prefix='a26-missing-seam-') as tmp:
            dest = Path(tmp) / 'a26'
            dest.mkdir()
            for name in ('confine.py', 'refusals.json', 'report.py'):
                self.assertTrue((SCRIPT.parent / name).is_file(), 'A26 launcher contract missing')
                (dest / name).write_bytes((SCRIPT.parent / name).read_bytes())
            p = self.call(['--wp-path=private', '--audit=private', '--output=private'], script=dest / 'confine.py')
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A26_SUPERVISOR_UNAVAILABLE\n'))


if __name__ == '__main__':
    unittest.main()
