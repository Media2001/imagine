"""Boundary doubles for publication; explicitly NOT PHP/native evidence."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from test_report import fixture

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationBoundaryTests(unittest.TestCase):
    def run_case(self, case):
        front = load('a26_front_double', ROOT / 'wp/outils/bascule/a26/confine.py')
        report = load('a26_report_double', ROOT / 'wp/outils/bascule/a26/report.py')
        real_guard = load('a26_guard_double', ROOT / 'wp/outils/bascule/stream_guard.py')
        fence = types.SimpleNamespace(disjoint_output=lambda parent, site, repo:
            parent != site and site not in parent.parents and parent not in site.parents)
        with tempfile.TemporaryDirectory(prefix='a26-boundary-double-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            site, parent = base / 'site', base / 'reports'
            site.mkdir()
            parent.mkdir()
            (parent / 'audit').mkdir()
            audit = parent / 'audit/audit.json'
            audit.write_bytes(b'{}\n')
            target = parent / 'public'
            def supervise(command, env, stage, actual_fence, **kwargs):
                self.assertEqual(command[0], 'php')  # Observed as data only: PHP is NOT launched.
                self.assertEqual(env['A26_CONFINED'], '1')
                result = stage / 'result'
                result.mkdir()
                data = fixture(report)
                data['audit_sha256'] = hashlib.sha256(audit.read_bytes()).hexdigest()
                raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
                (result / 'tiers.json').write_bytes(raw)
                (result / 'tiers.md').write_bytes(report.MARKDOWN.encode() + raw + b'```\n')
                hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in result.iterdir()}
                stdout = b'A26_OK tiers.json tiers.md\nA26_FINAL ' + json.dumps(hashes, separators=(',', ':')).encode() + b'\n'
                stderr = b''
                if case == 'stdout':
                    stdout += b'A26_STDOUT_PRIVATE_CANARY'
                elif case == 'stderr':
                    stderr = b'A26_STDERR_PRIVATE_CANARY'
                elif case == 'file':
                    (result / 'tiers.md').write_bytes(b'A26_FILE_PRIVATE_CANARY')
                elif case == 'valid_counts':
                    data['families']['mesure'] = {'active': 2, 'identifier': 'oui'}
                    raw = (json.dumps(data, ensure_ascii=False, indent=4) + '\n').encode('utf-8')
                    (result / 'tiers.json').write_bytes(raw)
                    (result / 'tiers.md').write_bytes(report.MARKDOWN.encode() + raw + b'```\n')
                return 0, stdout, stderr
            guard = types.SimpleNamespace(supervise=supervise, closed_refusal=real_guard.closed_refusal)
            modules = {'a26_common_guard': guard, 'a26_a12_fence': fence, 'a26_public_report': report}
            argv = ['confine.py', '--wp-path=' + str(site), '--audit=' + str(audit), '--output=' + str(target)]
            output = io.StringIO()
            with patch.object(front, 'load', side_effect=lambda name, path: modules[name]), patch.object(sys, 'argv', argv), contextlib.redirect_stdout(output):
                if case == 'nominal':
                    self.assertEqual(front.main(), 0)
                else:
                    want = 'A26_PROCESS_OUTPUT_INVALID' if case in ('stdout', 'stderr') else 'A26_REPORT_INVALID'
                    with self.assertRaisesRegex(RuntimeError, '^' + want + '$'):
                        front.main()
            self.assertEqual(target.exists(), case == 'nominal')
            self.assertEqual(list(parent.glob('.a26-private-*')), [])
            self.assertEqual(output.getvalue(), 'A26_OK tiers.json tiers.md\n' if case == 'nominal' else '')
            self.assertFalse(any(b'CANARY' in p.read_bytes() for p in parent.rglob('*') if p.is_file()))

    def test_nominal_publication_double(self):
        self.run_case('nominal')

    def test_direct_stdout_double(self):
        self.run_case('stdout')

    def test_direct_stderr_double(self):
        self.run_case('stderr')

    def test_final_file_canary_double(self):
        self.run_case('file')

    def test_schema_valid_number_mutation_double(self):
        self.run_case('valid_counts')

    def test_real_shared_guardian_process_bytes_and_closed_refusal(self):
        guard = load('a26_real_guardian', ROOT / 'wp/outils/bascule/stream_guard.py')
        with tempfile.TemporaryDirectory(prefix='a26-real-stream-', dir=os.environ.get('TMPDIR')) as tmp:
            command = [sys.executable, '-B', '-c', "import sys; sys.stdout.buffer.write(b'A26_PRIVATE_CANARY'); sys.stderr.buffer.write(b'A26_PRIVATE_CANARY')"]
            code, stdout, stderr = guard.supervise(command, dict(os.environ), Path(tmp), None)
            self.assertEqual((code, stdout, stderr), (0, b'A26_PRIVATE_CANARY', b'A26_PRIVATE_CANARY'))
            self.assertEqual(guard.closed_refusal(code, stdout, stderr, {'A26_USAGE'}, 'A26_PROCESS_OUTPUT_INVALID'), 'A26_PROCESS_OUTPUT_INVALID')


if __name__ == '__main__':
    unittest.main()
