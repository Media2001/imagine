"""Strict uncompressed .wpress reader, preserving wp-content files offline."""
import pathlib
import re
import struct
import tempfile
import unicodedata
from collections import Counter


EXTENSIONS = frozenset('php css js jpg jpeg png gif webp avif svg ico txt md json sql xml html htm pdf zip gz wpress log csv ttf woff woff2 eot mp3 mp4 ogg wav bin'.split())


def location(relative):
    """Only allowed directory zones and known extensions; never a basename."""
    parts = relative.split('/')
    zone = '(racine)'
    if len(parts) > 1:
        zone = '(autre)'
        if parts[0] in ('plugins', 'themes', 'uploads', 'mu-plugins', 'languages'):
            zone = parts[0] + '/(racine)'
            if len(parts) > 2 and re.fullmatch(r'[\w-]{1,100}', parts[1], re.ASCII):
                zone = parts[0] + '/' + parts[1]
    suffix = parts[-1].rsplit('.', 1)[-1].lower() if '.' in parts[-1] else ''
    return {'zone': zone, 'extension': '.' + suffix if suffix in EXTENSIONS else '(autre)'}


class Findings:
    def __init__(self):
        self.rules = {}

    def add(self, code, relative=None, blocking=True, **schema):
        rule = self.rules.setdefault(code, {'code': code, 'count': 0, 'blocking': blocking, 'locations': []})
        rule['count'] += 1
        where = location(relative) if relative is not None else schema
        if where:
            existing = next((v for v in rule['locations'] if all(v.get(k) == x for k, x in where.items())), None)
            if existing is None:
                rule['locations'].append(dict(where, count=1))
            else:
                existing['count'] += 1

    def report(self, entries=0, complete=True):
        rules = list(self.rules.values())
        return {'entries': entries, 'complete': complete, 'rules': rules,
                'blockers': [r['code'] for r in rules if r['blocking']],
                'warnings': [r['code'] for r in rules if not r['blocking']]}


def path_rules(relative, seen, folded):
    parts = relative.split('/')
    rules = []
    if relative.startswith('/'):
        rules.append('ARCHIVE_PATH_ABSOLUTE')
    if re.match(r'^[A-Za-z]:', relative):
        rules.append('ARCHIVE_PATH_DRIVE')
    if '' in parts:
        rules.append('ARCHIVE_PATH_EMPTY')
    if '.' in parts:
        rules.append('ARCHIVE_PATH_DOT')
    if '..' in parts:
        rules.append('ARCHIVE_PATH_PARENT')
    if '\\' in relative:
        rules.append('ARCHIVE_PATH_BACKSLASH')
    if any(unicodedata.category(c) == 'Cc' for c in relative):
        rules.append('ARCHIVE_PATH_CONTROL')
    if relative in seen:
        rules.append('ARCHIVE_PATH_DUPLICATE')
    if parts[0].casefold() in ('wp-config.php', 'wp-admin', 'wp-includes', 'wp-content'):
        rules.append('ARCHIVE_LAYOUT_UNSUPPORTED')
    # A regular file cannot also be the ancestor of another file.
    if any('/'.join(parts[:i]) in seen for i in range(1, len(parts))) or any(p.startswith(relative + '/') for p in seen):
        rules.append('ARCHIVE_PATH_FILE_DIRECTORY_COLLISION')
    if ':' in relative and 'ARCHIVE_PATH_DRIVE' not in rules:
        rules.append('ARCHIVE_PATH_COLON')
    if relative not in seen and relative.casefold() in folded:
        rules.append('ARCHIVE_PATH_CASE_ONLY')
    seen.add(relative)
    folded.add(relative.casefold())
    return rules


def audit(stream, max_bytes=1024*1024*1024, max_entries=150000, retain_sql=False):
    """One bounded streaming pass, inert bytes only, no filesystem writes.

    Broken framing/unsafe length cannot be resynchronised: record incomplete
    explicitly, never interpret guessed payload boundaries as another header.
    """
    findings = Findings()
    seen, folded = set(), set()
    total = entries = 0
    package = sql = None
    complete = False
    while entries <= max_entries:
        header = stream.read(4377)
        if len(header) != 4377:
            findings.add('ARCHIVE_TRUNCATED')
            break
        if header == bytes(4377):
            complete = True
            if stream.read(1):
                findings.add('ARCHIVE_TRAILING_DATA')
            if 'database.sql' not in seen:
                findings.add('ARCHIVE_DATABASE_MISSING')
            break
        entries += 1
        raw_fields = struct.unpack('255s14s12s4096s', header)
        fields = []
        bad = False
        for raw in raw_fields:
            value, _, padding = raw.partition(b'\0')
            try:
                fields.append(value.decode('utf-8', 'strict'))
            except UnicodeError:
                fields.append('')
                bad = True
            bad |= bool(padding.strip(b'\0'))
        name, size, stamp, prefix = fields
        if bad or not name or '/' in name or not re.fullmatch(r'[0-9]{1,12}', stamp):
            findings.add('ARCHIVE_HEADER')
        if not re.fullmatch(r'[0-9]{1,14}', size):
            findings.add('ARCHIVE_SIZE_INVALID')
            break
        relative = prefix + '/' + name if prefix else name
        for code in path_rules(relative, seen, folded):
            findings.add(code, relative, blocking=code not in ('ARCHIVE_PATH_COLON', 'ARCHIVE_PATH_CASE_ONLY'))
        length = int(size)
        total += length
        limited = entries > max_entries or total > max_bytes or (relative == 'database.sql' and length > 128*1024*1024) or (relative == 'package.json' and length > 1024*1024)
        if limited:
            findings.add('ARCHIVE_LIMIT', relative)
        if relative == 'multisite.json':
            findings.add('MULTISITE_UNSUPPORTED', relative)
        chunks = []
        remaining = length
        while remaining:
            data = stream.read(min(remaining, 1024*1024))
            if not data:
                findings.add('ARCHIVE_TRUNCATED', relative)
                return {'report': findings.report(entries, False), 'package': package, 'sql': sql}
            if not limited and (relative == 'package.json' or (retain_sql and relative == 'database.sql')):
                chunks.append(data)
            remaining -= len(data)
        if relative == 'package.json' and not limited:
            package = b''.join(chunks)
        elif relative == 'database.sql' and retain_sql and not limited:
            sql = b''.join(chunks)
        if entries > max_entries:
            break
    return {'report': findings.report(entries, complete), 'package': package, 'sql': sql}


class Refusal(ValueError):
    pass


def restore(stream, content, max_bytes=1024 * 1024 * 1024, max_entries=150000, metadata_only=False):
    seen = set()
    total = 0
    sql = None
    package = None
    content = pathlib.Path(content) if content is not None else None
    if not metadata_only:
        if content.exists():
            raise Refusal('FRESH_CONTENT_REQUIRED')
        content.mkdir(parents=True)
    for _ in range(max_entries + 1):
        header = stream.read(4377)
        if len(header) != 4377:
            raise Refusal('ARCHIVE_TRUNCATED')
        if header == bytes(4377):
            if stream.read(1) or 'database.sql' not in seen:
                raise Refusal('ARCHIVE_INVALID')
            return sql, package, len(seen)
        fields = struct.unpack('255s14s12s4096s', header)
        values = []
        for raw in fields:
            value, _, padding = raw.partition(b'\0')
            if padding.strip(b'\0'):
                raise Refusal('ARCHIVE_HEADER')
            try:
                values.append(value.decode('utf-8', 'strict'))
            except UnicodeError:
                raise Refusal('ARCHIVE_HEADER') from None
        name, size, stamp, prefix = values
        if (not name or '/' in name or name in ('.', '..')
                or not re.fullmatch(r'[0-9]{1,14}', size) or not re.fullmatch(r'[0-9]{1,12}', stamp)):
            raise Refusal('ARCHIVE_HEADER')
        relative = prefix + '/' + name if prefix else name
        parts = relative.split('/')
        if (relative.startswith('/') or any(p in ('', '.', '..') for p in parts)
                or any(ord(c) < 32 or c in '\\:' for c in relative) or relative.casefold() in seen):
            raise Refusal('ARCHIVE_PATH')
        seen.add(relative.casefold())
        length = int(size)
        total += length
        if len(seen) > max_entries or total > max_bytes or (relative == 'database.sql' and length > 128*1024*1024):
            raise Refusal('ARCHIVE_LIMIT')
        # The format exports wp-content-relative paths. Never accept a root config/core tree.
        metadata = relative in ('database.sql', 'package.json', 'multisite.json')
        if not metadata and parts[0] in ('wp-config.php', 'wp-admin', 'wp-includes', 'wp-content'):
            raise Refusal('ARCHIVE_LAYOUT_UNSUPPORTED')
        if relative == 'package.json' and length > 1024 * 1024:
            raise Refusal('ARCHIVE_LIMIT')
        target = content.joinpath(*parts) if content is not None else None
        if not metadata and not metadata_only:
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = target.open('xb')
        else:
            handle = None
        chunks = []
        try:
            remaining = length
            while remaining:
                data = stream.read(min(remaining, 1024*1024))
                if not data:
                    raise Refusal('ARCHIVE_TRUNCATED')
                if handle:
                    handle.write(data)
                elif relative == 'package.json' or (relative == 'database.sql' and not metadata_only):
                    chunks.append(data)
                remaining -= len(data)
        finally:
            if handle:
                handle.close()
        if relative == 'database.sql' and not metadata_only:
            sql = b''.join(chunks)
        elif relative == 'package.json':
            package = b''.join(chunks)
        elif relative == 'multisite.json':
            raise Refusal('MULTISITE_UNSUPPORTED')
    raise Refusal('ARCHIVE_LIMIT')
