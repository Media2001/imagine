"""A24 reception verifier contracts. Fixtures never touch the real proof packet."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (HERE / 'verify.py').is_file():
            raise AssertionError('mandatory verifier missing')
        spec = importlib.util.spec_from_file_location('a24_verifier_tests', HERE / 'verify.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_future_pret_does_not_change_source_inventory(self):
        with tempfile.TemporaryDirectory(prefix='a24-future-pret-', dir=os.environ.get('TMPDIR')) as tmp:
            root = Path(tmp)
            for key in ('wp/outils/bascule/a24/tool.py', 'wp/tests/a24/test_sample.py'):
                p = root / key
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b'pass\n')
            before = self.module.inventory(root, self.module.OWN)
            pret = root / 'production/A-24/PRET'
            pret.parent.mkdir(parents=True)
            pret.write_text('parent future readiness\n', encoding='utf-8')
            self.assertEqual(self.module.inventory(root, self.module.OWN), before)
            self.assertNotIn('production/A-24/PRET', before)

    def test_shared_readme_contract_ignores_other_lots(self):
        with tempfile.TemporaryDirectory(prefix='a24-readme-', dir=os.environ.get('TMPDIR')) as tmp:
            root = Path(tmp)
            delta = root / 'production/A-24/readme-ajout.txt'
            delta.parent.mkdir(parents=True)
            lines = ['A24 owned command', 'A24 owned caveat']
            delta.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            shared = root / 'wp/tests/a02-audit/README.md'
            shared.parent.mkdir(parents=True)
            shared.write_text('Other lot before\n' + '\n'.join(lines) + '\nOther lot after\n', encoding='utf-8')
            self.assertTrue(self.module.shared_contract(root))
            for body in ('\n'.join(lines[:1]) + '\n', '\n'.join(lines + lines) + '\n',
                         '\n'.join([lines[0] + ' altered', lines[1]]) + '\n'):
                shared.write_text(body, encoding='utf-8')
                self.assertFalse(self.module.shared_contract(root))

    def test_seal_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix='a24-seal-refusal-', dir=os.environ.get('TMPDIR')) as tmp:
            p = subprocess.run([sys.executable, '-B', str(HERE / 'seal.py'), '--source=' + str(Path(tmp) / 'missing')],
                               capture_output=True, text=True, encoding='utf-8', errors='strict', timeout=30,
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual((p.returncode, p.stdout, p.stderr), (1, '', 'A24_SEAL_REFUSED\n'))

    def test_empty_fake_green_packet_is_refused(self):
        with tempfile.TemporaryDirectory(prefix='a24-forged-packet-', dir=os.environ.get('TMPDIR')) as tmp:
            result = self.module.verify(ROOT, Path(tmp))
            self.assertEqual(result['exit_code'], 1)
            self.assertTrue(any(c['status'] == 'FAIL' for c in result['checks']))


if __name__ == '__main__':
    unittest.main()
