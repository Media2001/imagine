"""A30 process boundary and final-file validation; no PHP executed here."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/bascule/a30'))
import core


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a30-boundary-', dir=os.environ['TMPDIR'])
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.prepared = {'a13_code': 0, 'rows': [
            {'line': 2, 'email': 'fictif@example.org', 'rejected': False, 'product': 910001, 'payment': 'virement'},
            {'line': 3, 'email': '', 'rejected': False, 'product': 910001, 'payment': 'virement'}]}
        self.result = {'schema': 'imagine-a30-private-v1', 'storage': 'classic', 'neutralised': False,
                       'rows': [{'line': 2, 'issue': 'compte_existant', 'product': 910001, 'payment': 'virement'},
                                {'line': 3, 'issue': 'sans_email', 'product': 910001, 'payment': 'virement'}]}

    def test_child_schema_and_precedence_are_checked_after_exit(self):
        self.assertTrue(hasattr(core, 'validate_result'), 'A30 exact child schema validator missing')
        self.assertTrue(core.validate_result(self.result, self.prepared))
        mutations = [lambda d: d.update(private='PRIVATE'),
                     lambda d: d['rows'][0].update(private='PRIVATE'),
                     lambda d: d['rows'][0].update(line=True),
                     lambda d: d['rows'][0].update(issue='PRIVATE'),
                     lambda d: d['rows'][0].update(product=777),
                     lambda d: d['rows'][1].update(issue='compte_a_creer'),
                     lambda d: d['rows'][0].update(issue=None),
                     lambda d: d['rows'].reverse(), lambda d: d.update(storage='PRIVATE')]
        for mutate in mutations:
            d = copy.deepcopy(self.result); mutate(d)
            self.assertFalse(core.validate_result(d, self.prepared))

    def test_private_directory_extra_valid_json_and_late_files_are_rejected(self):
        self.assertTrue(hasattr(core, 'read_private'), 'A30 post-shutdown file boundary missing')
        stage = self.work / 'stage'; stage.mkdir()
        p = stage / 'result.json'; p.write_text(json.dumps(self.result), encoding='utf-8')
        self.assertEqual(self.result, core.read_private(stage, self.prepared))
        (stage / 'private.txt').write_text('PRIVATE', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'A30_REPORT_INVALID'):
            core.read_private(stage, self.prepared)
        (stage / 'private.txt').unlink()
        d = copy.deepcopy(self.result); d['private'] = 'PRIVATE'
        p.write_text(json.dumps(d), encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'A30_REPORT_INVALID'):
            core.read_private(stage, self.prepared)

    def test_outputs_are_adjacent_exclusive_utf8_and_contain_no_row_values(self):
        self.assertTrue(hasattr(core, 'publish'), 'A30 safe output writer missing')
        source = self.work / 'input.csv'; source.write_text('SOURCE PRIVATE', encoding='utf-8')
        summary, lines = core.public_reports(self.result)
        paths = core.publish(source, summary, lines)
        self.assertEqual({'input.a30-resume.json', 'input.a30-lignes.json'}, {p.name for p in paths})
        self.assertTrue(all(p.parent == source.parent for p in paths))
        text = ''.join(p.read_text(encoding='utf-8') for p in paths)
        self.assertNotIn('PRIVATE', text); self.assertNotIn('@', text)
        with self.assertRaisesRegex(RuntimeError, 'A30_OUTPUT_EXISTS'):
            core.publish(source, summary, lines)
        self.assertEqual('SOURCE PRIVATE', source.read_text(encoding='utf-8'))

    def test_valid_schema_shutdown_change_is_rejected_by_content_binding(self):
        self.assertTrue(hasattr(core, 'valid_binding'), 'A30 final digest binding missing')
        import hashlib
        stage = self.work / 'bound'; stage.mkdir()
        path = stage / 'result.json'; path.write_text(json.dumps(self.result), encoding='utf-8')
        success = b'A30_OK ' + hashlib.sha256(path.read_bytes()).hexdigest().encode() + b'\n'
        self.assertTrue(core.valid_binding(success, stage))
        changed = copy.deepcopy(self.result); changed['rows'][0]['issue'] = 'compte_a_creer'
        self.assertTrue(core.validate_result(changed, self.prepared))
        path.write_text(json.dumps(changed), encoding='utf-8')
        self.assertFalse(core.valid_binding(success, stage))
        self.assertFalse(core.valid_binding(success + b'PRIVATE', stage))

    def test_shared_guard_owns_stdout_stderr_display_shutdown_and_bound(self):
        spec = importlib.util.spec_from_file_location('a30_guard', ROOT / 'wp/outils/bascule/stream_guard.py')
        guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
        cases = ["import os; os.write(1,b'PRIVATE')", "import os; os.write(2,b'PRIVATE')", "print('PRIVATE')",
                 "import atexit; atexit.register(lambda: print('PRIVATE'))",
                 "import os,atexit; atexit.register(lambda: os.write(2,b'PRIVATE'))"]
        for script in cases:
            code, out, err = guard.supervise([sys.executable, '-c', script], os.environ.copy(), self.work, None)
            self.assertIn(b'PRIVATE', out + err)  # test witness stays in RAM
            self.assertEqual('A30_PROCESS_OUTPUT_INVALID', guard.closed_refusal(code, out, err, set(), 'A30_PROCESS_OUTPUT_INVALID'))
        with self.assertRaisesRegex(RuntimeError, 'A30_PROCESS_OUTPUT_INVALID'):
            guard.supervise([sys.executable, '-c', "import os; os.write(1,b'X'*70000)"],
                            os.environ.copy(), self.work, None, invalid='A30_PROCESS_OUTPUT_INVALID')


if __name__ == '__main__':
    unittest.main(verbosity=2)
