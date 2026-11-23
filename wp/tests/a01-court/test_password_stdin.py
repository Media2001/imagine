"""Windows operator automation must consume a pipe, never console getwch."""
import io
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/staging-court'))
import publish


class StdinPassword(unittest.TestCase):
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
