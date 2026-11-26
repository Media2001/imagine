"""Output grant must be disjoint in both directions before Landlock."""
from pathlib import Path, PurePosixPath
import sys
import unittest
sys.dont_write_bytecode=True
TOOLS=Path(__file__).resolve().parents[2]/'outils/bascule/a12'
if not TOOLS.exists(): TOOLS=Path('/subject/a12')
sys.path.insert(0,str(TOOLS))
import confine

class DisjointOutput(unittest.TestCase):
    def test_ancestors_and_descendants_are_refused(self):
        site=PurePosixPath('/work/site'); repository=PurePosixPath('/code/repo')
        for parent in ('/','/work','/work/site','/work/site/reports','/code','/code/repo','/code/repo/reports'):
            with self.subTest(parent=parent):
                self.assertFalse(confine.disjoint_output(PurePosixPath(parent),site,repository))
        self.assertTrue(confine.disjoint_output(PurePosixPath('/reports'),site,repository))
        self.assertTrue(confine.disjoint_output(PurePosixPath('/work/site-backup'),site,repository))

if __name__=='__main__':unittest.main(verbosity=2)
