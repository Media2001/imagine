"""Common guard tests: real portable child pipes, no host PHP."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PATH=ROOT/'wp/outils/bascule/stream_guard.py'

class CommonGuardTest(unittest.TestCase):
    def load(self):
        self.assertTrue(PATH.is_file(), 'one common stream guard must exist')
        spec=importlib.util.spec_from_file_location('guard',PATH)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        return m

    def child(self,body):
        return [sys.executable,'-B','-c',body]

    def test_common_guard_waits_for_real_child_termination(self):
        guard=self.load()
        code,out,err=guard.supervise(self.child("import atexit,sys; print('OK'); atexit.register(lambda:sys.stderr.write('LATE'))"),
            {**os.environ,'PYTHONIOENCODING':'utf-8'},None,None)
        self.assertEqual((code,out,err),(0,b'OK\n',b'LATE'))

    def test_raw_stream_overflow_refused_without_returning_bytes(self):
        guard=self.load()
        with self.assertRaisesRegex(RuntimeError,'OUTPUT_INVALID'):
            guard.supervise(self.child("import os; os.write(1,b'x'*70000)"),
                {**os.environ,'PYTHONIOENCODING':'utf-8'},None,None)

    def test_timeout_is_closed(self):
        guard=self.load()
        with self.assertRaisesRegex(RuntimeError,'PROCESS_TIMEOUT'):
            guard.supervise(self.child('import time; time.sleep(2)'),
                {**os.environ,'PYTHONIOENCODING':'utf-8'},None,None,timeout=.1)

    def test_stdin_unicode_transport_explicit_child_encoding(self):
        guard=self.load()
        code,out,err=guard.supervise(self.child('import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())'),
            {**os.environ,'PYTHONIOENCODING':'utf-8'},None,None,input_data='é'.encode())
        self.assertEqual((code,out,err),(0,'é'.encode(),b''))

if __name__=='__main__':unittest.main()
