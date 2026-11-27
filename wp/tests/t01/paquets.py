"""T03 packet replay. CLI only in T01; local tests inject the process boundary."""
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import subprocess
import sys
from time import monotonic as packet_time

sys.dont_write_bytecode = True

LOT = re.compile(r'[A-Z]-[0-9]{2}')
CONTROL = re.compile(r'[A-Za-z][A-Za-z0-9_:.-]{0,159}')
REQUIREMENTS = {'docker': 'Docker requis', 'network': 'reseau requis',
                'repository-write': 'ecriture depot requise', 'arguments': 'argument requis'}


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('DUPLICATE_KEY')
        value[key] = item
    return value


def no_links(root, relative):
    path = root
    for part in PurePosixPath(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('SYMLINK')
    return path


def declaration(root, lot):
    path = no_links(root, 'production/' + lot + '/rejeu.json')
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('DECLARATION_SIZE')
    data = json.loads(path.read_bytes(), object_pairs_hook=unique)
    if (not isinstance(data, dict) or set(data) != {'schema', 'entrypoint', 'requires', 'logs', 'controls'}
            or type(data['schema']) is not int or data['schema'] != 1 or data['entrypoint'] != 'verify.py'):
        raise ValueError('DECLARATION_SCHEMA')
    for key in ('requires', 'logs', 'controls'):
        values = data[key]
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values) or len(set(values)) != len(values):
            raise ValueError('DECLARATION_LIST')
    if any(v not in REQUIREMENTS for v in data['requires']):
        raise ValueError('REQUIRES')
    if not data['controls'] or any(not CONTROL.fullmatch(v) for v in data['controls']):
        raise ValueError('CONTROL')
    for value in data['logs']:
        path = PurePosixPath(value)
        if (not value.endswith('.log') or path.as_posix() != value or path.is_absolute()
                or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in ('.', '..') for part in path.parts)
                or not value.startswith(('production/' + lot + '/', 'files/rapports/'))):
            raise ValueError('LOG_PATH')
        no_links(root, value)
    return data


STREAM_LIMIT = 1024 * 1024
PACKET_EXPIRED = False


class PacketDeadline(Exception):
    """The PHP envelope expired; unwind verifier cleanup before exiting."""


def packet_expired(signum, frame):
    # Do not raise asynchronously across Popen: its child might exist before
    # the Python handle has been assigned. Unwind from the bounded read loop.
    global PACKET_EXPIRED
    PACKET_EXPIRED = True


def execute_verifier(root, verifier, timeout=90):
    # A private session contains descendants. Both pipes are bounded *as read*,
    # never communicate()/capture_output and never a shell. Even a normally
    # exiting parent cannot leave a writer/descendant alive behind it.
    if PACKET_EXPIRED:
        raise PacketDeadline()
    command = ['/usr/bin/python3', '-B', str(verifier)]
    deadline = packet_time() + timeout
    process = subprocess.Popen(command, cwd=root,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                                    'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                    'HOME': '/tmp', 'TMPDIR': '/tmp', 'XDG_CACHE_HOME': '/tmp'},
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    output = [bytearray(), bytearray()]
    try:
        with selectors.DefaultSelector() as selector:
            for index, stream in enumerate((process.stdout, process.stderr)):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, index)
            while selector.get_map():
                if PACKET_EXPIRED:
                    raise PacketDeadline()
                remaining = deadline - packet_time()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(command, timeout)
                for key, _ in selector.select(min(remaining, 0.05)):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    buffer = output[key.data]
                    if len(chunk) > STREAM_LIMIT - len(buffer):
                        # Discard overflow, return only a fixed closed red. The
                        # finally block kills the whole group immediately.
                        return subprocess.CompletedProcess(command, -9, b'', b'STREAM_LIMIT')
                    buffer.extend(chunk)
        while process.poll() is None:
            if PACKET_EXPIRED:
                raise PacketDeadline()
            remaining = deadline - packet_time()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout)
            try:
                process.wait(timeout=min(remaining, 0.05))
            except subprocess.TimeoutExpired:
                pass
        return subprocess.CompletedProcess(command, process.returncode, bytes(output[0]), bytes(output[1]))
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=1)
        process.stdout.close()
        process.stderr.close()


def parse_verdict(process, controls):
    """Return the first named red, or None. Never return verifier text."""
    try:
        if process.stderr or len(process.stdout) > 1024 * 1024:
            raise ValueError('STREAM')
        data = json.loads(process.stdout, object_pairs_hook=unique)
        if not isinstance(data, dict):
            raise ValueError('OBJECT')
        exits = [data[k] for k in ('exit_code', 'exit') if k in data]
        if not exits or any(type(v) is not int or v not in (0, 1) for v in exits) or len(set(exits)) != 1:
            raise ValueError('EXIT')
        red = []
        if 'code' in data:
            if data['code'] not in controls:
                raise ValueError('UNKNOWN_CONTROL')
            red.append(data['code'])
        if 'checks' in data:
            if not isinstance(data['checks'], list) or not data['checks']:
                raise ValueError('CHECKS')
            names = []
            for row in data['checks']:
                if not isinstance(row, dict) or row.get('check') not in controls or row.get('status') not in ('PASS', 'FAIL'):
                    raise ValueError('CHECK')
                names.append(row['check'])
                if row['status'] == 'FAIL':
                    red.append(row['check'])
            if len(set(names)) != len(names):
                raise ValueError('DUPLICATE_CHECK')
        if red:
            return red[0]
        if process.returncode != 0 or exits[0] != 0 or ('status' in data and data['status'] not in ('PASS', 'CANDIDAT_GATE_PARENT')):
            raise ValueError('CONTRADICTION')
        return None
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        return 'VERIFIER_OUTPUT'


def replay(root, execute=None):
    deadline = packet_time() + 120
    result = {'verified': 0, 'lots': [], 'failures': [], 'excluded': []}
    for lot in sorted((root / 'production').iterdir()):
        if not LOT.fullmatch(lot.name):
            continue
        if lot.is_symlink():
            result['failures'].append({'lot': lot.name, 'control': 'DECLARATION_INVALID'})
            continue
        if not (lot / 'verify.py').exists() and not (lot / 'rejeu.json').exists():
            continue
        try:
            no_links(root, 'production/' + lot.name + '/verify.py')
            no_links(root, 'production/' + lot.name + '/rejeu.json')
            if not (lot / 'rejeu.json').is_file():
                result['excluded'].append({'lot': lot.name, 'reason': 'declaration absente'})
                continue
            data = declaration(root, lot.name)
            if data['requires']:
                result['excluded'].append({'lot': lot.name, 'reason': REQUIREMENTS[data['requires'][0]]})
                continue
            if any(not (root / name).is_file() for name in data['logs']):
                result['excluded'].append({'lot': lot.name, 'reason': 'journaux absents'})
                continue
        except (OSError, ValueError, TypeError, RecursionError):
            result['failures'].append({'lot': lot.name, 'control': 'DECLARATION_INVALID'})
            continue
        result['verified'] += 1
        result['lots'].append(lot.name)
        if not (lot / 'verify.py').is_file():
            control = 'VERIFIER_START'
        else:
            try:
                remaining = deadline - packet_time()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired('packet-budget', 120)
                control = parse_verdict((execute or execute_verifier)(root, lot / 'verify.py', min(90, remaining)), data['controls'])
            except subprocess.TimeoutExpired:
                control = 'VERIFIER_TIMEOUT'
            except OSError:
                control = 'VERIFIER_START'
        if control is not None:
            result['failures'].append({'lot': lot.name, 'control': control})
    return result


def main():
    result = {'verified': 0, 'lots': [], 'failures': [], 'excluded': []}
    try:
        # The real filesystem/network enforcement is T01 Docker, not these sentinels.
        if (len(sys.argv) != 1 or sys.platform != 'linux' or not Path('/.dockerenv').is_file()
                or Path(__file__).resolve() != Path('/repo/wp/tests/t01/paquets.py')
                or not Path('/packet-repo/production').is_dir()):
            raise ValueError('RUNNER_CONTEXT')
        signal.signal(signal.SIGTERM, packet_expired)
        result = replay(Path('/packet-repo'))
    except PacketDeadline:
        result['failures'].append({'lot': 'T-03', 'control': 'RUNNER_TIMEOUT'})
    except Exception:
        result['failures'].append({'lot': 'T-03', 'control': 'RUNNER_CONTEXT'})
    print('T03_PACKETS ' + json.dumps(result, ensure_ascii=True, separators=(',', ':')))
    return 0  # Never change the test-suite process status.


if __name__ == '__main__':
    raise SystemExit(main())
