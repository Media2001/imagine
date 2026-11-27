"""Local closure contracts; no PHP, image mutation or shared-runner write."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile
import unittest

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t03_qualification', BASE / 'qualifier-corrections.py')
qualification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualification)
spec = importlib.util.spec_from_file_location('t03_reader', BASE / 'verify-corrections.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class ClosureContracts(unittest.TestCase):
    def test_reader_requires_measured_tmpdir_absence(self):
        self.assertTrue(hasattr(reader, 'verify_console'), 'reader must verify the clean-session measurement')
        for context, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
            valid = {'stdout': encoding, 'utf8_mode': mode, 'tmpdir_present': False}
            reader.verify_console(valid, context)
            for invalid in ({'stdout': encoding, 'utf8_mode': mode}, {**valid, 'tmpdir_present': True}):
                with self.assertRaisesRegex(ValueError, 'CLEAN_WINDOWS_SESSION_NOT_MEASURED'):
                    reader.verify_console(invalid, context)

    def test_clean_windows_children_in_both_consoles(self):
        self.assertTrue(hasattr(qualification, 'console_environment'),
                        'qualification must construct a clean child environment')
        for context, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
            with self.subTest(context=context):
                inherited = {**os.environ, 'TMPDIR': 'MUST_NOT_REACH_CHILD'}
                environment = qualification.console_environment(context, inherited)
                process = subprocess.run(
                    [sys.executable, '-B', '-c',
                     "import json,os,sys;print(json.dumps({'tmpdir_present':'TMPDIR' in os.environ,'stdout':sys.stdout.encoding,'mode':sys.flags.utf8_mode}))"],
                    env=environment, capture_output=True, check=True)
                actual = json.loads(process.stdout)
                self.assertEqual(actual, {'tmpdir_present': False, 'stdout': encoding, 'mode': mode})
                self.assertEqual(inherited['TMPDIR'], 'MUST_NOT_REACH_CHILD')


if __name__ == '__main__':
    unittest.main()
