"""Exercise A22 stream guardian on actual Python child pipes, no PHP/network."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import signal
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a29_guard', ROOT / 'wp/outils/bascule/stream_guard.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
SUCCESS = b'A29_OK taches.json taches.md\n'


class GuardTests(unittest.TestCase):
    def run_child(self, code, **kw):
        return g.supervise([sys.executable, '-B', '-c', code],
                           {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                            'PYTHONDONTWRITEBYTECODE': '1'}, None, None,
                           invalid='A29_PROCESS_OUTPUT_INVALID', expired='A29_PROCESS_TIMEOUT', **kw)

    def test_actual_success(self):
        self.assertEqual(self.run_child("import os; os.write(1, b'A29_OK taches.json taches.md\\n')"), (0, SUCCESS, b''))

    def test_direct_stdout_stderr_shutdown_and_invalid_utf8_rejected(self):
        for code in ("import os; os.write(1,b'A29_PRIVATE_CANARY')", "import os; os.write(2,b'A29_PRIVATE_CANARY')",
                     "import atexit,os; atexit.register(lambda:os.write(1,b'A29_PRIVATE_CANARY'))",
                     "import atexit,os; atexit.register(lambda:os.write(2,b'A29_PRIVATE_CANARY'))",
                     "import os; os.write(2,b'\\xff')", 'pass'):
            rc, out, err = self.run_child(code)
            self.assertNotEqual((rc, out, err), (0, SUCCESS, b''))
            self.assertEqual(g.closed_refusal(rc, out, err, {'A29_USAGE'}, 'A29_PROCESS_OUTPUT_INVALID'), 'A29_PROCESS_OUTPUT_INVALID')

    def test_closed_codes_exact_bytes_and_exit(self):
        for rc, out, err, expected in [(1, b'', b'A29_USAGE\n', 'A29_USAGE'),
                (2, b'', b'A29_USAGE\n', 'A29_PROCESS_OUTPUT_INVALID'),
                (1, b'x', b'A29_USAGE\n', 'A29_PROCESS_OUTPUT_INVALID'),
                (1, b'', b'A29_USAGE A29_PRIVATE_CANARY\n', 'A29_PROCESS_OUTPUT_INVALID'),
                (1, b'', b'A29_USAGE\nA29_PRIVATE_CANARY', 'A29_PROCESS_OUTPUT_INVALID')]:
            self.assertEqual(g.closed_refusal(rc, out, err, {'A29_USAGE'}, 'A29_PROCESS_OUTPUT_INVALID'), expected)

    def test_both_pipes_drained_and_bounded(self):
        with self.assertRaisesRegex(RuntimeError, '^A29_PROCESS_OUTPUT_INVALID$'):
            self.run_child("import os; os.write(1,b'x'*70000); os.write(2,b'y'*70000)")

    def test_timeout_closed(self):
        with self.assertRaisesRegex(RuntimeError, '^A29_PROCESS_TIMEOUT$'):
            self.run_child('import time; time.sleep(10)', timeout=0.1)

    def test_descendant_inherited_pipes_share_one_deadline(self):
        with tempfile.TemporaryDirectory(prefix='a29-pipe-', dir=os.environ.get('TMPDIR')) as tmp:
            pidfile = Path(tmp) / 'owned-descendant.pid'
            code = ("import subprocess,sys;from pathlib import Path;"
                    "p=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(8)'],stdout=sys.stdout,stderr=sys.stderr);"
                    "Path(" + repr(str(pidfile)) + ").write_text(str(p.pid),encoding='ascii')")
            started = time.monotonic()
            try:
                with self.assertRaisesRegex(RuntimeError, '^A29_PROCESS_TIMEOUT$'):
                    self.run_child(code, timeout=0.4)
                self.assertLess(time.monotonic() - started, 2.0)
            finally:
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text(encoding='ascii')), signal.SIGTERM)
                    except ProcessLookupError:
                        pass


if __name__ == '__main__':
    unittest.main()
