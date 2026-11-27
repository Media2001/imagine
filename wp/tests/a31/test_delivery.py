"""A31 refusal tests use incomplete toy packets only, never fabricated green native receipts."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


class DeliveryTests(unittest.TestCase):
    def test_reseal_partial_refused_without_publishing(self):
        script = HERE / 'reseal.py'
        self.assertTrue(script.is_file(), 'owned reseal command missing')
        with tempfile.TemporaryDirectory(prefix='a31-refused-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            matrix = base / 'matrix'
            gates = base / 'gates'
            matrix.mkdir()
            gates.mkdir()
            (matrix / 'windows-matrix.json').write_text(json.dumps({'scope': 'python_only'}), encoding='utf-8')
            manifest = ROOT / 'production/A-31/manifest.json'
            before = manifest.read_bytes() if manifest.exists() else None
            p = subprocess.run([sys.executable, '-B', str(script), '--parent-serialized',
                                '--evidence=' + str(matrix), '--gates=' + str(gates)], cwd=ROOT,
                               capture_output=True, text=True, encoding='utf-8', timeout=30,
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual((p.returncode, p.stderr), (1, ''))
            self.assertEqual(json.loads(p.stdout)['code'], 'A31_PARTIAL_EVIDENCE')
            self.assertEqual(before, manifest.read_bytes() if manifest.exists() else None)

    def test_missing_gates_do_not_pass(self):
        spec = importlib.util.spec_from_file_location('a31_delivery_test', HERE / 'delivery.py')
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        with tempfile.TemporaryDirectory(prefix='a31-gates-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            (base / 'result.json').write_text('{"exit_code":0,"sources_stable":true}', encoding='utf-8')
            (base / 'commands.json').write_text('[]', encoding='utf-8')
            self.assertFalse(helper.gate_logs_valid(base))


if __name__ == '__main__':
    unittest.main()
