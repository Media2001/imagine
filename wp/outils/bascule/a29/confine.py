#!/usr/bin/env python3
"""A29: A22 bounded stream guardian + A12 disconnected Landlock fence."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SUCCESS = b'A29_OK taches.json taches.md\n'
CODES = frozenset(json.loads((HERE / 'refusals.json').read_text(encoding='utf-8')))
DROPINS = ('wp-content/db.php', 'wp-content/object-cache.php', 'wp-content/advanced-cache.php',
           'wp-content/sunrise.php', 'wordfence-waf.php', '.user.ini')
REFUSALS = set(CODES) | {'A11_DROPIN_UNSUPPORTED ' + json.dumps({'file': name}, separators=(',', ':')) for name in DROPINS}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    options = {}
    for arg in sys.argv[1:]:
        key, sep, value = arg.partition('=')
        if not sep or not value or key not in {'--wp-path', '--audit', '--output'} or key in options:
            raise RuntimeError('A29_USAGE')
        options[key] = value
    if len(options) != 3:
        raise RuntimeError('A29_USAGE')
    if not (HERE.parent / 'stream_guard.py').is_file():
        raise RuntimeError('A29_SUPERVISOR_UNAVAILABLE')
    guard = load('a29_common_guard', HERE.parent / 'stream_guard.py')
    fence = load('a29_a12_fence', HERE.parent / 'a12/confine.py')
    report = load('a29_public_report', HERE / 'report.py')
    site = Path(options['--wp-path']).resolve(strict=True)
    parent = Path(options['--output']).parent.resolve(strict=True)
    output = parent / Path(options['--output']).name
    candidate = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent
    repo = candidate if (candidate / 'wp/outils/bascule/audit').is_file() else HERE.parent
    if not site.is_dir() or not re.fullmatch(r'[A-Za-z0-9_-]+', output.name) or not fence.disjoint_output(parent, site, repo):
        raise RuntimeError('A29_OUTPUT_UNSAFE')
    if output.exists() or output.is_symlink():
        raise RuntimeError('A29_OUTPUT_EXISTS')
    audit = Path(options['--audit'])
    if (audit.is_symlink() or not audit.is_file() or audit.stat().st_size > 16777216
            or audit.resolve().parent.parent != parent):
        raise RuntimeError('A29_AUDIT_GUARD')
    # The child can write only inside this private directory; publication is parent-only.
    with tempfile.TemporaryDirectory(prefix='.a29-private-', dir=parent) as temporary:
        stage = Path(temporary)
        os.chmod(stage, 0o700)
        (stage / 'audit').mkdir(mode=0o700)
        staged_audit = stage / 'audit/audit.json'
        shutil.copyfile(audit, staged_audit)
        staged_output = stage / 'result'
        command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d', 'error_log=/dev/null', '-d',
                   'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                   str(HERE / 'inventorier-taches'), '--wp-path=' + str(site),
                   '--audit=' + str(staged_audit), '--output=' + str(staged_output)]
        code, stdout, stderr = guard.supervise(command, {**os.environ, 'A29_CONFINED': '1'}, stage, fence,
                                               invalid='A29_PROCESS_OUTPUT_INVALID', expired='A29_PROCESS_TIMEOUT')
        protocol = rb'A29_OK taches\.json taches\.md\nA29_FINAL \{"taches\.json":"[a-f0-9]{64}","taches\.md":"[a-f0-9]{64}"\}\n'
        if code != 0 or stderr or re.fullmatch(protocol, stdout) is None:
            raise RuntimeError(guard.closed_refusal(code, stdout, stderr, REFUSALS, 'A29_PROCESS_OUTPUT_INVALID'))
        if not report.final_binding(stdout, staged_output) or not report.complete_report(staged_output, audit):
            raise RuntimeError('A29_REPORT_INVALID')
        staged_output.rename(output)
    sys.stdout.write(SUCCESS.decode('ascii'))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        message = str(error) if isinstance(error, RuntimeError) and str(error) in REFUSALS else 'A29_CONFINEMENT_FAILED'
        print(message, file=sys.stderr)
        sys.exit(1)
