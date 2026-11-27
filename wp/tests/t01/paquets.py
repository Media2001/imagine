"""T03 packet replay. CLI only in T01; local tests inject the process boundary."""
import json
from pathlib import Path, PurePosixPath
import re

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


def replay(root, execute=None):
    result = {'verified': 0, 'failures': [], 'excluded': []}
    for lot in sorted((root / 'production').iterdir()):
        if not LOT.fullmatch(lot.name):
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
        except (OSError, ValueError, TypeError):
            result['failures'].append({'lot': lot.name, 'control': 'DECLARATION_INVALID'})
    return result
