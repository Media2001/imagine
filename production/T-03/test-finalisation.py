"""T03 final gates against real captured replays; disposable mutations only."""
import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent


def load_reader():
    path = BASE / 'verify-final.py'
    if not path.is_file():
        raise AssertionError('final state needs an executable read-only reader')
    spec = importlib.util.spec_from_file_location('t03_final', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FinalContracts(unittest.TestCase):
    def test_finalizer_failure_preserves_manifest_without_pret(self):
        self.assertTrue((BASE / 'finaliser.py').is_file(), 'checked finalizer required')
        with tempfile.TemporaryDirectory(prefix='t03-final-contract-', dir=Path(os.environ['LOCALAPPDATA']) / 'hermes/cache/scratch') as temporary:
            target = Path(temporary) / 'production/T-03'
            shutil.copytree(BASE, target)
            (target / 'PRET').unlink(missing_ok=True)
            before = (target / 'manifest.json').read_bytes()
            # Missing frozen tools/evidence is intentionally fatal in this copy.
            environment = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
            environment.pop('TMPDIR', None)
            child = subprocess.run([sys.executable, '-B', str(target / 'finaliser.py')], env=environment, capture_output=True)
            self.assertEqual(child.returncode, 1)
            self.assertFalse((target / 'PRET').exists())
            self.assertEqual((target / 'manifest.json').read_bytes(), before)

    def test_shared_evidence_checks_available_without_relaxing_candidate_contract(self):
        spec = importlib.util.spec_from_file_location('candidate', BASE / 'verify-corrections.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(getattr(module, 'verify_evidence', None)), 'final gate must reuse all candidate evidence checks')

    def test_real_nominal_and_one_byte_are_tests_green_packets_separate(self):
        reader = load_reader()
        directory = Path(os.environ['T03_NATIVE_EVIDENCE'])
        green = reader.verify_replay((directory / 'green.log').read_bytes(), [])
        red = reader.verify_replay((directory / 'one-byte.log').read_bytes(),
                                  [{'lot': 'A-28', 'control': 'PACKAGE_DRIFT'}])
        self.assertEqual(green['last'], red['last'])
        self.assertEqual(green['marker']['packets']['lots'], reader.LOTS)
        for bad in (b'', (directory / 'one-byte.log').read_bytes()):
            with self.assertRaises(ValueError):
                reader.verify_replay(bad, [])
        with self.assertRaises(ValueError):
            reader.verify_replay((directory / 'green.log').read_bytes().replace(b'T01 CLEANUP :', b'NO_CLEANUP :'), [])


if __name__ == '__main__':
    unittest.main()
