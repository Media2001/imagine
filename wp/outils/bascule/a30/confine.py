#!/usr/bin/env python3
"""A30: only A22 owns the child streams; publication follows complete exit."""
from datetime import date
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
import core

HERE = Path(__file__).resolve().parent
CODES = {'A30_USAGE', 'A30_CONFIG_INVALID', 'A30_OPTION_UNSUPPORTED', 'A30_OUTPUT_UNSAFE',
         'A30_OUTPUT_EXISTS', 'A30_CONFINEMENT_REQUIRED', 'A30_AUDIT_GUARD', 'A30_AUDIT_STORAGE_MISMATCH',
         'A30_QUERY_FAILED', 'A30_EXISTING_EMAIL_AMBIGUOUS', 'A30_INPUT_INVALID', 'A30_NATIVE_UNSUPPORTED',
         'A30_INVENTORY_FAILED', 'A30_PROCESS_OUTPUT_INVALID', 'A30_PROCESS_TIMEOUT', 'A30_REPORT_INVALID',
         'A30_CONFINEMENT_FAILED'}
SUCCESS = b'A30_OK\n'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def arguments(argv):
    options = {}
    required = {'--wp-path', '--fichier', '--correspondance', '--types', '--audit', '--au'}
    for arg in argv:
        key, sep, value = arg.partition('=')
        if not sep or not value or key not in required or key in options:
            raise RuntimeError('A30_USAGE')
        options[key] = value
    if set(options) != required:
        raise RuntimeError('A30_USAGE')
    try:
        at = date.fromisoformat(options['--au'])
        if at.isoformat() != options['--au']:
            raise ValueError
    except ValueError:
        raise RuntimeError('A30_USAGE') from None
    return options, at


def main(argv=None):
    options, at = arguments(sys.argv[1:] if argv is None else argv)
    # A13 refuses before any site lookup or PHP call. Its exact messages/codes survive.
    config = core.read_config(options['--types'])
    source = Path(options['--fichier'])
    prepared = core.prepare(source, options['--correspondance'], at, config)
    if sys.platform != 'linux':
        raise RuntimeError('A30_CONFINEMENT_REQUIRED')
    site = Path(options['--wp-path']).resolve(strict=True)
    source = core.safe_source(source, site)
    audit = Path(options['--audit'])
    if audit.is_symlink() or not audit.is_file() or audit.stat().st_size > 16777216:
        raise RuntimeError('A30_AUDIT_GUARD')
    photo = json.loads(audit.read_bytes(), object_pairs_hook=core.A13.objet_unique)
    if (not isinstance(photo, dict) or photo.get('schema') != 'imagine-a02-audit-v1'
            or photo.get('read_only') is not True):
        raise RuntimeError('A30_AUDIT_GUARD')
    try:
        storage = photo['sections']['commerce']['order_storage']
    except (KeyError, TypeError):
        raise RuntimeError('A30_AUDIT_GUARD') from None
    if storage not in ('classic', 'hpos'):
        raise RuntimeError('A30_AUDIT_GUARD')
    guard = load('a30_shared_guard', HERE.parent / 'stream_guard.py')
    fence = load('a30_readonly_fence', HERE.parent / 'a12/confine.py')
    allowed = CODES | set(guard.allowed_messages())
    with tempfile.TemporaryDirectory(prefix='.a30-private-', dir=source.parent) as temporary:
        stage = Path(temporary); os.chmod(stage, 0o700)
        command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d', 'error_log=/dev/null', '-d',
                   'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                   str(HERE / 'observer.php'), '--wp-path=' + str(site), '--output=' + str(stage)]
        code, stdout, stderr = guard.supervise(command, {**os.environ, 'A30_CONFINED': '1'}, stage, fence,
            input_data=json.dumps(prepared, ensure_ascii=True, separators=(',', ':')).encode('ascii'),
            invalid='A30_PROCESS_OUTPUT_INVALID', expired='A30_PROCESS_TIMEOUT')
        if code != 0 or not core.valid_binding(stdout, stage) or stderr:
            raise RuntimeError(guard.closed_refusal(code, stdout, stderr, allowed, 'A30_PROCESS_OUTPUT_INVALID'))
        result = core.read_private(stage, prepared)
        if result['storage'] != storage:
            raise RuntimeError('A30_AUDIT_STORAGE_MISMATCH')
        summary, lines = core.public_reports(result)
        core.publish(source, summary, lines)
    print('A30_OK')
    # Same meaning as A13: code 1 if row-level A13 defects; no additional import decision.
    return prepared['a13_code']


def cli():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')
    try:
        return main()
    except core.A13.Refus as error:
        print('REFUS : ' + str(error), file=sys.stderr)
        return 2
    except (OSError, ValueError):
        print('REFUS : fichier ou correspondance illisible.', file=sys.stderr)
        return 2
    except Exception as error:
        # A11 refusals originate only from exact closed messages checked by A22.
        allowed = CODES
        try:
            allowed = allowed | set(load('a30_errors', HERE.parent / 'stream_guard.py').allowed_messages())
        except Exception:
            pass
        code = str(error) if isinstance(error, RuntimeError) and str(error) in allowed else 'A30_CONFINEMENT_FAILED'
        print(code, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(cli())
