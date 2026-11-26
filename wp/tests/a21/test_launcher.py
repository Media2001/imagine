"""Portable A21 CLI tests; no PHP execution on the Windows host."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
class LauncherTest(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/a21/confine.py'),*args],env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,encoding='utf-8',timeout=30)
    def test_required_paths(self):
        p=self.invoke()
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A21_USAGE\n'))
    def test_unknown_argument_is_closed(self):
        p=self.invoke('--CANARY=été-漢')
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A21_USAGE\n'))
    def test_duplicate(self):
        p=self.invoke('--output=x','--output=y')
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A21_USAGE\n'))
    def test_documented_arguments_need_no_date(self):
        missing=ROOT/'wp/tests/a21/A21_NONEXISTENT_SITE'
        self.assertFalse(missing.exists())
        p=self.invoke('--wp-path='+str(missing),'--audit='+str(missing/'audit.json'),'--output='+str(missing/'report'))
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A21_CONFINEMENT_FAILED\n'))
    def test_duplicate_date(self):
        p=self.invoke('--wp-path=x','--audit=y','--output=z','--as-of=2026-11-26T00:00:00Z','--as-of=2026-11-27T00:00:00Z')
        self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'','A21_USAGE\n'))
if __name__=='__main__':
    unittest.main()
