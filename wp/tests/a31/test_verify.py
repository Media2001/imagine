"""Production entrypoint must honestly refuse incomplete/no native evidence."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / 'production/A-31/verify.py'


class VerifyTests(unittest.TestCase):
    def call(self, args=(), encoding='utf-8'):
        self.assertTrue(SCRIPT.is_file(), 'A31 no-argument production verifier missing')
        p = subprocess.run([sys.executable, '-B', str(SCRIPT), *args], cwd=ROOT, capture_output=True,
                           text=True, encoding=encoding, errors='strict', timeout=30,
                           env={**os.environ, 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': '0' if encoding == 'cp1252' else '1',
                                'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(p.stderr, '')
        data = json.loads(p.stdout)
        self.assertEqual(data['exit_code'], p.returncode)
        return data

    def test_noarg_partial_honest_refusal_or_genuine_complete(self):
        data = self.call()
        if not (ROOT / 'production/A-31/manifest.json').exists():
            self.assertEqual((data['exit_code'], data['code']), (1, 'A31_PARTIAL_EVIDENCE'))
        self.assertIs(data['readiness_claimed'], False)

    def test_no_argument_escape_to_python_only(self):
        data = self.call(['--python-only'])
        self.assertEqual((data['exit_code'], data['code']), (1, 'A31_ARGUMENTS_REFUSED'))

    def test_cp1252_closed_refusal(self):
        data = self.call(['--evidence=A31_PRIVÉ_🔐_CANARY'], 'cp1252')
        self.assertEqual(data['code'], 'A31_ARGUMENTS_REFUSED')

    def test_rejeu_exact_closed_convention(self):
        path = ROOT / 'production/A-31/rejeu.json'
        self.assertTrue(path.is_file(), 'A31 declaration missing before delivery')
        data = json.loads(path.read_bytes())
        self.assertEqual(set(data), {'schema', 'entrypoint', 'requires', 'logs', 'controls'})
        self.assertEqual(data['schema'], 1)
        self.assertEqual(data['entrypoint'], 'verify.py')
        self.assertEqual(data['requires'], [])
        self.assertEqual(len(data['logs']), len(set(data['logs'])))
        self.assertEqual(len(data['controls']), len(set(data['controls'])))
        for value in data['logs']:
            self.assertTrue(value.startswith('production/A-31/'))
            self.assertTrue(value.endswith('.log'))
            self.assertNotIn('..', Path(value).parts)
        for code in data['controls']:
            self.assertRegex(code, r'^[A-Za-z][A-Za-z0-9_:.-]{0,159}$')

    def emitted_verdict(self, code):
        # Rendering/collector boundary unit test only, not fabricated native evidence.
        spec = importlib.util.spec_from_file_location('a31_emitted_production', SCRIPT)
        production = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(production)
        output = io.StringIO()
        with mock.patch.object(production, 'verify', return_value=code), contextlib.redirect_stdout(output):
            exit_code = production.main()
        spec = importlib.util.spec_from_file_location('a31_real_t03_parser', ROOT / 'wp/tests/t01/paquets.py')
        collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(collector)
        process = subprocess.CompletedProcess(['verify.py'], exit_code, output.getvalue().encode('utf-8'), b'')
        return collector.parse_verdict(process, production.CODES)

    def test_real_t03_parser_accepts_success_envelope(self):
        self.assertIsNone(self.emitted_verdict('A31_PACKAGE_PASS'))

    def test_real_t03_parser_preserves_all_closed_refusals(self):
        for code in ('A31_ARGUMENTS_REFUSED', 'A31_PARTIAL_EVIDENCE', 'A31_PACKAGE_DRIFT',
                     'A31_PARENT_GATES_MISSING', 'A31_NATIVE_PACKET_INVALID', 'A31_PACKET_INVALID'):
            with self.subTest(code=code):
                self.assertEqual(self.emitted_verdict(code), code)

    def test_receipt_rejects_boolean_exit_or_empty_checks(self):
        spec = importlib.util.spec_from_file_location('a31_test_verifier', ROOT / 'wp/tests/a31/verify.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for value in ({}, {'exit_code': False, 'checks': [{'check': 'x', 'status': 'PASS'}]},
                      {'exit_code': 0, 'checks': []}, {'exit_code': 0, 'checks': [{'check': 'x', 'status': 'FAIL'}]}):
            self.assertFalse(m.receipt_valid(value))


if __name__ == '__main__':
    unittest.main()
