"""Closed Windows refusal surface, without PHP or a site."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'wp/outils/bascule/a31/confine.py'


class LauncherTests(unittest.TestCase):
    def call(self, args, encoding='utf-8', script=SCRIPT):
        self.assertTrue(script.is_file(), 'mandatory A31 launcher missing')
        return subprocess.run([sys.executable, '-B', str(script), *args], cwd=ROOT,
                              capture_output=True, text=True, encoding=encoding, errors='strict', timeout=30,
                              env={**os.environ, 'PYTHONIOENCODING': encoding,
                                   'PYTHONUTF8': '0' if encoding == 'cp1252' else '1',
                                   'PYTHONDONTWRITEBYTECODE': '1'})

    def test_usage_is_closed(self):
        for args in ([], ['--bad=A31_PRIVATE_CANARY'], ['--wp-path=one', '--wp-path=A31_PRIVATE_CANARY']):
            p = self.call(args)
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A31_USAGE\n'))

    def test_cp1252_refusal(self):
        for value in ('A31_PRIVATE_CANARY', 'A31_PRIVÉ_🔐_CANARY'):
            p = self.call(['--bad=' + value], 'cp1252')
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A31_USAGE\n'))

    def test_missing_supervisor(self):
        with tempfile.TemporaryDirectory(prefix='a31-missing-', dir=os.environ.get('TMPDIR')) as tmp:
            dest = Path(tmp) / 'a31'
            dest.mkdir()
            for name in ('confine.py', 'refusals.json', 'report.py'):
                self.assertTrue((SCRIPT.parent / name).is_file())
                (dest / name).write_bytes((SCRIPT.parent / name).read_bytes())
            p = self.call(['--wp-path=private', '--audit=private', '--output=private'], script=dest / 'confine.py')
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A31_SUPERVISOR_UNAVAILABLE\n'))


if __name__ == '__main__':
    unittest.main()
