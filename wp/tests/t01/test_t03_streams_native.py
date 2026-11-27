"""Real bounded-stream/process-group regressions. Run ONLY in T01 Docker."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True


def setUpModule():
    if sys.platform != 'linux' or not Path('/.dockerenv').is_file():
        raise unittest.SkipTest('PHP and real verifier regressions require T01 Docker')
    for name in ('executer.php', 'paquets.php'):
        child = subprocess.run(['php', '-l', str(Path(__file__).with_name(name))],
                               capture_output=True, timeout=10)
        if child.returncode != 0:
            raise AssertionError(child.stderr.decode('utf-8', errors='replace'))
        print(child.stdout.decode('utf-8').strip(), flush=True)


SPEC = importlib.util.spec_from_file_location('t03_stream_target', Path(__file__).with_name('paquets.py'))
paquets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(paquets)


def live(pid):
    try:
        return Path('/proc/' + str(pid) + '/stat').read_text().split(') ')[1][0] != 'Z'
    except FileNotFoundError:
        return False


@unittest.skipUnless(sys.platform == 'linux' and Path('/.dockerenv').is_file(), 'T01 Docker required')
class RealStreams(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t03-stream-', dir='/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        paquets.PACKET_EXPIRED = False
        self.pids = self.root / 'pids'
        self.verifier = self.root / 'verify.py'
        self.old_signal = signal.signal(signal.SIGTERM, paquets.packet_expired)
        self.addCleanup(signal.signal, signal.SIGTERM, self.old_signal)

    def source(self, action):
        grand = "import os,pathlib,time; p=pathlib.Path(" + repr(str(self.pids)) + "); f=p.open('a'); f.write(str(os.getpid())+'\\n'); f.close(); time.sleep(20)"
        child = "import os,pathlib,subprocess,sys,time; p=pathlib.Path(" + repr(str(self.pids)) + "); p.write_text(str(os.getpid())+'\\n'); subprocess.Popen([sys.executable,'-c'," + repr(grand) + "],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(20)"
        source = "import os,pathlib,subprocess,sys,time\np=pathlib.Path(" + repr(str(self.pids)) + ")\nsubprocess.Popen([sys.executable,'-c'," + repr(child) + "],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\nwhile not p.exists() or len(p.read_text().splitlines())<2: time.sleep(.005)\n" + action
        self.verifier.write_text(source, encoding='utf-8')

    def cleaned(self):
        pids = [int(value) for value in self.pids.read_text().splitlines()]
        for _ in range(100):
            if not any(live(pid) for pid in pids):
                break
            time.sleep(.005)
        survivors = [pid for pid in pids if live(pid)]
        for pid in survivors:
            os.kill(pid, signal.SIGKILL)  # RED cleanup is mandatory as well.
        self.assertEqual(len(pids), 2, 'real child and grandchild recorded')
        self.assertEqual(survivors, [], 'verifier descendants survived')

    def capped(self, channels):
        action = 'for _ in range(512):\n'
        for fd in channels:
            action += '    os.write(' + str(fd) + ",b'x'*4096)\n"
        action += 'time.sleep(.2)\n'
        self.source(action)
        start = time.monotonic()
        try:
            process = paquets.execute_verifier(self.root, self.verifier, timeout=3)
            self.assertLessEqual(len(process.stdout), 1024 * 1024)
            self.assertLessEqual(len(process.stderr), 1024 * 1024)
            self.assertEqual(paquets.parse_verdict(process, ['FIXTURE']), 'VERIFIER_OUTPUT')
            self.assertLess(time.monotonic() - start, 1.5)
        finally:
            self.cleaned()

    def test_stdout_capped_while_reading_and_two_descendants_killed(self):
        self.capped([1])

    def test_stderr_capped_while_reading_and_two_descendants_killed(self):
        self.capped([2])

    def test_simultaneous_channels_cannot_deadlock_or_accumulate(self):
        self.capped([1, 2])

    def test_real_verifier_timeout_kills_its_two_descendants(self):
        self.source('time.sleep(20)\n')
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                paquets.execute_verifier(self.root, self.verifier, timeout=.3)
        finally:
            self.cleaned()

    def test_normal_exit_cannot_leave_its_two_descendants(self):
        self.source("print('{\"exit\":0}')\n")
        try:
            process = paquets.execute_verifier(self.root, self.verifier, timeout=3)
            self.assertIsNone(paquets.parse_verdict(process, ['FIXTURE']))
        finally:
            self.cleaned()

    def test_real_TERM_while_reading_unwinds_group_before_return(self):
        self.source('os.kill(os.getppid(),15)\ntime.sleep(20)\n')
        try:
            with self.assertRaises(paquets.PacketDeadline):
                paquets.execute_verifier(self.root, self.verifier, timeout=3)
        finally:
            self.cleaned()

    def test_real_TERM_after_EOF_unwinds_group_before_return(self):
        self.source('os.close(1)\nos.close(2)\ntime.sleep(.1)\nos.kill(os.getppid(),15)\ntime.sleep(20)\n')
        try:
            with self.assertRaises(paquets.PacketDeadline):
                paquets.execute_verifier(self.root, self.verifier, timeout=3)
        finally:
            self.cleaned()


if __name__ == '__main__':
    unittest.main(verbosity=2)
