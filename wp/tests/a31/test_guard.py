"""Exercise A22 stream guardian on actual Python child pipes, no PHP/network."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a31_guard', ROOT / 'wp/outils/bascule/stream_guard.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
SUCCESS = b'A31_OK commandes.json commandes.md\n'


class GuardTests(unittest.TestCase):
    def run_child(self, code, **kw):
        return g.supervise([sys.executable, '-B', '-c', code],
                           {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                            'PYTHONDONTWRITEBYTECODE': '1'}, None, None,
                           invalid='A31_PROCESS_OUTPUT_INVALID', expired='A31_PROCESS_TIMEOUT', **kw)

    def test_actual_success(self):
        self.assertEqual(self.run_child("import os; os.write(1, b'A31_OK commandes.json commandes.md\\n')"), (0, SUCCESS, b''))

    def test_direct_stdout_stderr_shutdown_and_invalid_utf8_rejected(self):
        for code in ("import os; os.write(1,b'A31_PRIVATE_CANARY')", "import os; os.write(2,b'A31_PRIVATE_CANARY')",
                     "import atexit,os; atexit.register(lambda:os.write(1,b'A31_PRIVATE_CANARY'))",
                     "import atexit,os; atexit.register(lambda:os.write(2,b'A31_PRIVATE_CANARY'))",
                     "import os; os.write(2,b'\\xff')", 'pass'):
            rc, out, err = self.run_child(code)
            self.assertNotEqual((rc, out, err), (0, SUCCESS, b''))
            self.assertEqual(g.closed_refusal(rc, out, err, {'A31_USAGE'}, 'A31_PROCESS_OUTPUT_INVALID'), 'A31_PROCESS_OUTPUT_INVALID')

    def test_closed_codes_exact_bytes_and_exit(self):
        for rc, out, err, expected in [(1, b'', b'A31_USAGE\n', 'A31_USAGE'),
                (2, b'', b'A31_USAGE\n', 'A31_PROCESS_OUTPUT_INVALID'),
                (1, b'x', b'A31_USAGE\n', 'A31_PROCESS_OUTPUT_INVALID'),
                (1, b'', b'A31_USAGE A31_PRIVATE_CANARY\n', 'A31_PROCESS_OUTPUT_INVALID'),
                (1, b'', b'A31_USAGE\nA31_PRIVATE_CANARY', 'A31_PROCESS_OUTPUT_INVALID')]:
            self.assertEqual(g.closed_refusal(rc, out, err, {'A31_USAGE'}, 'A31_PROCESS_OUTPUT_INVALID'), expected)

    def test_both_pipes_drained_and_bounded(self):
        with self.assertRaisesRegex(RuntimeError, '^A31_PROCESS_OUTPUT_INVALID$'):
            self.run_child("import os; os.write(1,b'x'*70000); os.write(2,b'y'*70000)")

    def test_timeout_closed(self):
        with self.assertRaisesRegex(RuntimeError, '^A31_PROCESS_TIMEOUT$'):
            self.run_child('import time; time.sleep(10)', timeout=0.1)


if __name__ == '__main__':
    unittest.main()
