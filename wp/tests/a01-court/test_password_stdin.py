"""Windows operator automation must consume a pipe, never console getwch."""
import io
import json
from pathlib import Path
import sys
import unittest
import tempfile
import subprocess
from unittest import mock
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/staging-court'))
import publish


class StdinPassword(unittest.TestCase):
    def test_pipe_is_captured_before_wsl_can_drain_it(self):
        events = []
        with tempfile.TemporaryDirectory(dir=Path.home() / 'AppData/Local/hermes/cache/scratch') as folder:
            root = Path(folder)
            archive = root / 'fiction.wpress'
            archive.write_bytes(b'Fictitious metadata seam only')
            with mock.patch.multiple(publish, ROOT=root, HERE=root,
                    archive_capacity_on_engine=lambda *args: events.append('capacity') or {},
                    read_admin_password=lambda flag: events.append('password') or 'entierement-fictif-0123456789',
                    fresh_runner=lambda name: {}, offline_isolation=lambda name: {},
                    call=lambda *a, **k: subprocess.CompletedProcess([], 0, b'', b''),
                    archive_core_preflight=lambda *a: {'ok': False, 'code': 'SOURCE_EXPECTED_CORE_VERSION_MISMATCH'},
                    remove_owned=lambda name: {'name': name, 'absent': True}), \
                 mock.patch('publication_preflight.collect', side_effect=lambda: events.append('collect') or {'tool_source_manifest': {}}), \
                 mock.patch.object(sys, 'argv', ['publish.py', '--operator-ced', '--archive', str(archive),
                    '--name', 'imagine-test-a01-pipe', '--production-url', 'https://source.invalid', '--password-stdin']):
                self.assertEqual(1, publish.main())
            self.assertEqual('password', events[0], 'WSL consumes inherited stdin, capture the pipe first')
            report = next(root.rglob('result.json')).read_text()
            self.assertNotIn('entierement-fictif-0123456789', report)

    def test_explicit_pipe_reads_new_password_without_getpass(self):
        value = 'entierement-fictif-0123456789'
        stream = io.TextIOWrapper(io.BytesIO((value + '\r\n').encode()))
        with mock.patch.object(sys, 'stdin', stream), mock.patch.object(publish.getpass, 'getpass', side_effect=AssertionError('No console read')):
            self.assertEqual(value, publish.read_admin_password(True))

    def test_default_remains_interactive_getpass(self):
        with mock.patch.object(publish.getpass, 'getpass', return_value='entierement-fictif-0123456789') as prompt:
            self.assertEqual('entierement-fictif-0123456789', publish.read_admin_password(False))
            prompt.assert_called_once()

    def test_invalid_or_long_pipe_is_refused(self):
        for data in (b'short\n', b'x' * 73 + b'\n', b'a' * 20 + b'\0\n', b'\xff' * 20 + b'\n'):
            with mock.patch.object(sys, 'stdin', io.TextIOWrapper(io.BytesIO(data))):
                with self.assertRaisesRegex(RuntimeError, '^ADMIN_PASSWORD_REFUSED$'):
                    publish.read_admin_password(True)

    def test_pipe_flag_never_enables_echoing_console_read(self):
        stream = mock.Mock()
        stream.isatty.return_value = True
        with mock.patch.object(sys, 'stdin', stream):
            with self.assertRaisesRegex(RuntimeError, '^PASSWORD_STDIN_PIPE_REQUIRED$'):
                publish.read_admin_password(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
