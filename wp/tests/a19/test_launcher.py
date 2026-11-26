"""Portable Python acceptance; subprocess selects its own UTF-8."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
LOT=Path(__file__).resolve().parent.name
CODE=LOT.upper()
class LauncherTest(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule'/LOT/'confine.py'),*args],
            env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'},
            capture_output=True,text=True,encoding='utf-8',timeout=30)
    def test_three_paths_without_date_reach_path_validation(self):
        # Deliberately nonexistent: no PHP, confinement or site bootstrap on host.
        missing=ROOT/'wp/tests/a19/A19_NONEXISTENT_SITE'
        self.assertFalse(missing.exists())
        p=self.invoke('--wp-path='+str(missing),'--output='+str(missing/'report'),'--audit='+str(missing/'audit.json'))
        self.assertEqual(p.returncode,1);self.assertEqual(p.stdout,'')
        self.assertEqual(p.stderr,CODE+'_CONFINEMENT_FAILED\n')
    def test_repeated_date_refused_with_all_paths(self):
        p=self.invoke('--wp-path=x','--output=y','--audit=z','--as-of=2026-11-26T00:00:00Z','--as-of=2026-11-27T00:00:00Z')
        self.assertEqual(p.returncode,1);self.assertEqual(p.stdout,'');self.assertEqual(p.stderr,CODE+'_USAGE\n')
    def test_required_arguments(self):
        p=self.invoke();self.assertEqual(p.returncode,1);self.assertEqual(p.stdout,'')
        self.assertEqual(p.stderr,CODE+'_USAGE\n')
    def test_unknown_argument_never_bootstraps_php(self):
        p=self.invoke('--inconnu=été-漢');self.assertEqual(p.returncode,1);self.assertEqual(p.stderr,CODE+'_USAGE\n');self.assertEqual(p.stdout,'')
    def test_duplicate_argument_refused(self):
        p=self.invoke('--output=x','--output=y');self.assertEqual(p.returncode,1);self.assertEqual(p.stderr,CODE+'_USAGE\n')
if __name__=='__main__':unittest.main()
