"""Dependency drift uses real files in a disposable repository, never live sources."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DEPENDENCIES=['wp/tests/a02-audit','wp/tests/a19','wp/outils/bascule/audit',
              'wp/outils/bascule/a11','wp/outils/bascule/a12','wp/outils/staging']

class DependencyTest(unittest.TestCase):
    def test_real_verifier_observes_current_dependency_drift(self):
        spec=importlib.util.spec_from_file_location('isolated_a21_verifier',HERE/'verify.py')
        verifier=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        with tempfile.TemporaryDirectory(prefix='a21-dependency-test-',dir=os.environ.get('TMPDIR')) as directory:
            root=Path(directory)
            for name in verifier.OWN+DEPENDENCIES:
                source=ROOT/name
                if source.is_dir():
                    shutil.copytree(source,root/name,ignore=shutil.ignore_patterns('__pycache__'))
                else:
                    (root/name).parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(source,root/name)
            for name in ['production/A-21/readme-ajout.txt','production/A-21/notes.md']:
                (root/name).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,root/name)
            packet=root/'production/A-21/preuves/final'
            shutil.copytree(ROOT/'production/A-21/preuves/final',packet)
            verifier.ROOT=root
            snapshot=verifier.inventory(DEPENDENCIES)
            snapshot.pop('wp/tests/a02-audit/README.md',None)
            for folder in [packet,packet/'utf8']:
                (folder/'dependency-snapshot.json').write_text(json.dumps(snapshot),encoding='utf-8')
            def inspect():
                text=io.StringIO()
                with contextlib.redirect_stdout(text):
                    verifier.verify(packet)
                return {row['check']:row['status'] for row in json.loads(text.getvalue())['checks']}
            baseline=inspect()
            self.assertEqual(baseline.get('exact_current_dependencies'),'PASS')
            targets=['wp/outils/bascule/a11/Runtime.php','wp/outils/bascule/a12/confine.py',
                     'wp/outils/bascule/audit','wp/outils/staging/lib.php',
                     'wp/tests/a02-audit/inside.py','wp/tests/a19/run.py']
            for name in targets:
                with self.subTest(dependency=name):
                    target=root/name
                    before=target.read_bytes()
                    target.write_bytes(before+b'\n# disposable dependency drift\n')
                    drift=inspect()
                    self.assertEqual(drift.get('exact_current_dependencies'),'FAIL')
                    self.assertEqual(drift.get('utf8:executed_dependency_snapshot'),'FAIL')
                    self.assertEqual(drift.get('cp1252:executed_dependency_snapshot'),'FAIL')
                    target.write_bytes(before)
            readme=root/'wp/tests/a02-audit/README.md'
            readme.write_bytes(readme.read_bytes()+b'\nUnrelated appendix from another lot.\n')
            annex=inspect()
            self.assertEqual(annex.get('exact_current_dependencies'),'PASS')
            self.assertEqual(annex.get('own_two_shared_lines_only'),'PASS')

    def test_dependency_roots_match_the_executed_runner(self):
        import run
        import verify
        self.assertEqual(verify.DEPENDENCIES,run.DEPENDENCIES)

if __name__=='__main__':
    unittest.main()
