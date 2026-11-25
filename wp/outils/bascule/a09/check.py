"""Read-only A09 redirect plan checker. No automatic redirect handling."""
import csv
import pathlib
import re
from urllib.parse import urlsplit

REPO = pathlib.Path(__file__).resolve().parents[4]
REDIRECTS = {301, 302, 303, 307, 308}


def need(ok, code):
    if not ok:
        raise ValueError(code)


def plain_file(path, code):
    path = pathlib.Path(path).absolute()
    need(not any(p.is_symlink() for p in [path, *path.parents]) and path.is_file(), code)
    need(path.stat().st_size <= 1048576, code)
    return path.resolve()


def relative(value):
    """Conservative ASCII URI paths; normalize percent-encoded unreserved."""
    need(isinstance(value, str) and 0 < len(value) <= 2048, 'A09_PLAN_URL')
    need(not re.search(r'[\\\x00-\x20\x7f-\uffff#]', value), 'A09_PLAN_URL')
    need(value.startswith('/') and not value.startswith('//'), 'A09_PLAN_URL')
    need(not re.search(r'%(?![a-fA-F0-9]{2})', value), 'A09_PLAN_URL')
    need(not re.search(r'%(?:0[0-9a-f]|1[0-9a-f]|20|2f|5c|7f)', value, re.I), 'A09_PLAN_URL')
    value = re.sub(r'%([a-fA-F0-9]{2})', lambda m: chr(int(m[1], 16)) if re.fullmatch(r'[A-Za-z0-9_.~-]', chr(int(m[1], 16))) else '%'+m[1].upper(), value)
    parts = urlsplit(value)
    need(not parts.scheme and not parts.netloc and not parts.fragment and not any(s in ['.', '..'] for s in parts.path.split('/')), 'A09_PLAN_URL')
    return value


def load_plan(path):
    path = plain_file(path, 'A09_PLAN_FILE')
    need(path.is_relative_to(REPO), 'A09_PLAN_NOT_IN_REPOSITORY')
    rows = []
    seen = set()
    try:
        with open(path, encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream, strict=True)
            need(next(reader, None) == ['ancienne', 'cible', 'code'], 'A09_PLAN_HEADER')
            for row in reader:
                need(len(row) == 3 and len(rows) < 1000, 'A09_PLAN_COLUMNS_OR_LIMIT')
                old, target, code = row
                canonical_old, canonical_target = relative(old), relative(target)
                need(code in [str(v) for v in REDIRECTS], 'A09_PLAN_CODE')
                need(canonical_old not in seen, 'A09_PLAN_DUPLICATE_OR_CONFLICT')
                need(canonical_old != canonical_target, 'A09_PLAN_SELF')
                seen.add(canonical_old)
                rows.append({'line': reader.line_num, 'ancienne': old, 'cible': target, 'code': int(code)})
    except (csv.Error, UnicodeError):
        raise ValueError('A09_PLAN_ENCODING_OR_CSV') from None
    need(bool(rows), 'A09_PLAN_EMPTY')
    return rows
