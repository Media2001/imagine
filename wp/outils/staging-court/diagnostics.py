"""Closed external-command diagnostics. Never serialize argv or raw output."""
import re
import subprocess


class CommandFailure(RuntimeError):
    def __init__(self, code, stage, **detail):
        super().__init__(code)
        self.failure = {'stage': stage, 'code': code, **detail}


def statement_coordinate(payload):
    # Only identifiers in grammar positions; never infer names from error text.
    head = re.match(rb'\s*(CREATE\s+TABLE|INSERT\s+INTO|UPDATE|DROP\s+TABLE(?:\s+IF\s+EXISTS)?)\s+`([A-Za-z0-9_]{1,64})`', payload, re.I)
    if head:
        return {'statement': head[1].split()[0].decode().upper(), 'table': head[2].decode()}
    word = re.match(rb'\s*(SET|START|COMMIT)\b', payload, re.I)
    return {'statement': word[1].decode().upper() if word else 'UNKNOWN', 'table': None}


def database_error(stderr, sql_path=None):
    match = re.search(rb'^ERROR\s+([0-9]{1,6})(?:\s+\(([0-9A-Z]{5})\))?(?:\s+at\s+line\s+([0-9]{1,12}))?\s*:', stderr, re.M)
    result = {'errno': int(match[1]) if match else None,
              'sqlstate': match[2].decode() if match and match[2] else None,
              'line': int(match[3]) if match and match[3] else None,
              'statement': 'UNKNOWN', 'table': None}
    if sql_path is not None and result['line']:
        # Normalized SQL has one statement per physical line (newlines escaped).
        with open(sql_path, 'rb') as source:
            for number, line in enumerate(source, 1):
                if number == result['line']:
                    result.update(statement_coordinate(line[:4096]))
                    break
    return result


def php_error(stderr):
    # PHP formats only; the message/stack/arguments are intentionally discarded.
    found = re.search(rb'(?:Fatal error:\s*(?:Uncaught\s+)?|Uncaught\s+)([A-Za-z_][A-Za-z0-9_\\]{0,150})', stderr)
    where = re.search(rb'\s+in\s+([^\r\n]+?)(?::| on line )([0-9]+)(?:\r?\n|$)', stderr)
    result = {'class': found[1].decode() if found else 'PHPFailure', 'file': None, 'line': None}
    if where:
        path = where[1].decode('utf-8', 'replace').replace('\\', '/')
        relative = path.split('/wp-content/', 1)[-1] if '/wp-content/' in path else None
        if relative and re.fullmatch(r'[A-Za-z0-9_./-]{1,400}', relative) and '..' not in relative.split('/'):
            result['file'] = relative
        result['line'] = int(where[2])
    return result


def execute(args, *, stage='external_command', timeout=300, check=True, sql_path=None, database=False, php=False, **kwargs):
    try:
        result = subprocess.run(args, timeout=timeout, **kwargs)
    except subprocess.TimeoutExpired:
        raise CommandFailure('COMMAND_TIMEOUT', stage, timeout_seconds=timeout) from None
    except OSError as error:
        raise CommandFailure('COMMAND_START_REFUSED', stage, os_errno=error.errno) from None
    if check and result.returncode:
        detail = {'exit': result.returncode}
        if database:
            detail['database'] = database_error(result.stderr or b'', sql_path)
        if php:
            detail['php'] = php_error(result.stderr or b'')
        raise CommandFailure('DATABASE_COMMAND_REFUSED' if database else 'EXTERNAL_COMMAND_REFUSED', stage, **detail)
    return result
