"""A31 delivery helpers: read-only checks shared by production and parent reseal."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OWN = ['wp/outils/bascule/a31', 'wp/tests/a31', 'production/A-31']
EXCLUDED = {'production/A-31/manifest.json', 'production/A-31/PRET'}
GATE_NAMES = ('prepare-image', 'global-utf8', 'global-cp1252', 'a20-readonly', 'a21-readonly', 'a22-readonly', 'a28-readonly')
CODES = ('A31_ARGUMENTS_REFUSED', 'A31_PARTIAL_EVIDENCE', 'A31_PACKAGE_DRIFT', 'A31_PARENT_GATES_MISSING',
         'A31_NATIVE_PACKET_INVALID', 'A31_PACKET_INVALID', 'A31_PACKAGE_PASS')


def inventory(roots, excluded=()):
    files = []
    for key in roots:
        path = ROOT / key
        if path.is_symlink() or not path.exists():
            raise ValueError('source')
        entries = [path] if path.is_file() else list(path.rglob('*'))
        if any(p.is_symlink() for p in entries):
            raise ValueError('source')
        files.extend(p for p in entries if p.is_file() and '__pycache__' not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if p.relative_to(ROOT).as_posix() not in excluded}


def read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('packet')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate')
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=pairs)


def gate_logs_valid(folder):
    result = read(folder / 'result.json')
    rows = read(folder / 'commands.json')
    if (type(result.get('exit_code')) is not int or result['exit_code'] != 0
            or result.get('sources_stable') is not True or tuple(r['name'] for r in rows) != GATE_NAMES):
        return False
    for row in rows:
        if type(row.get('exit_code')) is not int or row['exit_code'] != 0 or row.get('sources_stable') is not True:
            return False
        for field in ('stdout', 'stderr'):
            file = folder / row[field]
            if not file.resolve().is_relative_to(folder.resolve()) or file.is_symlink():
                return False
            if hashlib.sha256(file.read_bytes()).hexdigest() != row[field + '_sha256']:
                return False
        if (folder / row['stderr']).read_bytes() != b'':
            return False
        text = (folder / row['stdout']).read_text(encoding='utf-8')
        if row['name'].startswith('global-'):
            matches = re.findall(r'^T01_RESULT (.+)$', text, re.M)
            if len(matches) != 1:
                return False
            marker = json.loads(matches[0])
            if (marker.get('pass') is not True or marker['failures'] != 0 or marker['errors'] != 0
                    or marker['tools']['failures'] != 0 or marker['packets']['failures'] != []
                    or not {'A-22', 'A-28'}.issubset(marker['packets']['lots'])):
                return False
        elif row['name'].endswith('-readonly'):
            obj = json.loads(text)
            if obj.get('exit_code', obj.get('exit')) != 0:
                return False
        elif 'T03 IMAGE PYTHON : offline standard-library probe PASS' not in text:
            return False
    return read(folder / 'sources.json') == inventory(read(folder / 'source-roots.json'))
