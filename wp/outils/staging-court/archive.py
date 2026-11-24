"""Strict uncompressed .wpress reader, preserving wp-content files offline."""
import pathlib
import os
import re
import struct
import tempfile
import unicodedata
import shutil
import zlib
import json
from archive_policy import (DEFAULT_MAX_BYTES, DEFAULT_MAX_ENTRIES, DEFAULT_MAX_SQL_BYTES, CHUNK,
                            excluded, unknown_upload, secret_candidate)


def header_fields(header):
    crc = header[-8:] if re.fullmatch(rb'[0-9a-fA-F]{8}', header[-8:]) else None
    raw_fields = struct.unpack('255s14s12s4088s8s', header)[:4] if crc else struct.unpack('255s14s12s4096s', header)
    fields = []
    for raw in raw_fields:
        value, _, padding = raw.partition(b'\0')
        if padding.strip(b'\0'):
            raise Refusal('ARCHIVE_HEADER')
        try:
            fields.append(value.decode('utf-8', 'strict'))
        except UnicodeError:
            raise Refusal('ARCHIVE_HEADER') from None
    return fields, crc


def eof_block(header):
    if header == bytes(4377):
        return True
    return (header[:255] == bytes(255) and header[269:4369] == bytes(4100)
            and re.fullmatch(rb'[0-9a-fA-F]{8}', header[-8:])
            and re.fullmatch(rb'[0-9]{1,14}', header[255:269].rstrip(b'\0')))


def skip_payload(stream, length):
    if not stream.seekable():
        raise Refusal('ARCHIVE_SEEK_REQUIRED')
    stream.seek(length, 1)


def check_space(root, needed):
    root = pathlib.Path(root)
    while not root.exists():
        root = root.parent
    if shutil.disk_usage(root).free < needed + 256 * CHUNK:
        raise Refusal('DISK_SPACE_INSUFFICIENT')


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
            elif (parts[0] == 'uploads' and len(parts) > 2 and parts[1] not in ('', '.', '..')
                  and len(parts[1]) <= 255 and not any(unicodedata.category(c) in ('Cc', 'Cf') for c in parts[1])
                  and '\\' not in parts[1]):
                zone = 'uploads/' + parts[1]  # directory name is required for the explicit operator decision
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


def archive_path(prefix, name):
    # AI1WM dirname('package.json') is '.', not an unsafe interior segment.
    if prefix in ('.', './'):
        prefix = ''
    elif prefix.startswith('./'):
        prefix = prefix[2:]
    return prefix + '/' + name if prefix else name


def path_rules(relative, seen, folded, directories):
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
    ancestors = ['/'.join(parts[:i]) for i in range(1, len(parts))]
    if any(parent in seen for parent in ancestors) or relative in directories:
        rules.append('ARCHIVE_PATH_FILE_DIRECTORY_COLLISION')
    directories.update(ancestors)
    if ':' in relative and 'ARCHIVE_PATH_DRIVE' not in rules:
        rules.append('ARCHIVE_PATH_COLON')
    if relative not in seen and relative.casefold() in folded:
        rules.append('ARCHIVE_PATH_CASE_ONLY')
    seen.add(relative)
    folded.add(relative.casefold())
    return rules


def audit(stream, max_bytes=DEFAULT_MAX_BYTES, max_entries=DEFAULT_MAX_ENTRIES, retain_sql=False,
          on_chunk=None, on_metadata=None, max_sql_bytes=DEFAULT_MAX_SQL_BYTES):
    """Streaming, inert bytes; metadata indices only, no complete SQL/media."""
    findings = Findings()
    seen, folded, directories = set(), set(), set()
    total = entries = database_bytes = 0
    package = sql = None
    complete = False
    excluded_zones, uploads, plugins, themes = {}, {}, set(), set()
    start = stream.tell()
    def result():
        value = findings.report(entries, complete)
        value.update(total_bytes=total, database_bytes=database_bytes, archive_bytes=stream.tell() - start,
                     crc_policy='retained-entry CRC when present; excluded bytes never read; EOF size checked; whole-archive CRC deferred',
                     excluded=list(excluded_zones.values()), inventory={'plugins': sorted(plugins), 'themes': sorted(themes), 'uploads': list(uploads.values())})
        return {'report': value, 'package': package, 'sql': sql}
    while entries <= max_entries:
        offset = stream.tell() - start
        header = stream.read(4377)
        if len(header) != 4377:
            findings.add('ARCHIVE_TRUNCATED')
            break
        if eof_block(header):
            complete = True
            if header != bytes(4377) and int(header[255:269].rstrip(b'\0')) != offset:
                findings.add('ARCHIVE_EOF_SIZE')
            if stream.read(1):
                findings.add('ARCHIVE_TRAILING_DATA')
            if 'database.sql' not in seen:
                findings.add('ARCHIVE_DATABASE_MISSING', 'database.sql')
            break
        entries += 1
        try:
            (name, size, stamp, prefix), crc = header_fields(header)
        except Refusal:
            findings.add('ARCHIVE_HEADER')
            name, size, stamp, prefix = (x.partition(b'\0')[0].decode('utf-8', 'replace') for x in struct.unpack('255s14s12s4096s', header))
            crc = None
        relative = archive_path(prefix, name)
        parts = relative.split('/')
        if not name or '/' in name or not re.fullmatch(r'[0-9]{1,12}', stamp):
            findings.add('ARCHIVE_HEADER', relative)
        if not re.fullmatch(r'[0-9]{1,14}', size):
            findings.add('ARCHIVE_SIZE_INVALID', relative)
            break
        for code in path_rules(relative, seen, folded, directories):
            findings.add(code, relative, blocking=code not in ('ARCHIVE_PATH_COLON', 'ARCHIVE_PATH_CASE_ONLY'))
        length = int(size)
        total += length
        if relative == 'database.sql':
            database_bytes += length
        metadata_limited = (relative == 'database.sql' and length > max_sql_bytes) or (relative == 'package.json' and length > CHUNK)
        if entries > max_entries or total > max_bytes or metadata_limited:
            findings.add('ARCHIVE_LIMIT', relative)
        if relative == 'multisite.json':
            findings.add('MULTISITE_UNSUPPORTED', relative)
        safe_dir = len(parts) > 2 and re.fullmatch(r'[\w-]{1,100}', parts[1], re.ASCII)
        if parts[0] == 'plugins' and safe_dir:
            plugins.add(parts[1])
        elif parts[0] == 'themes' and safe_dir:
            themes.add(parts[1])
        elif parts[0] == 'uploads' and len(parts) > 2:
            folder = location(relative)['zone'].partition('/')[2]
            row = uploads.setdefault(folder, {'directory': folder, 'count': 0, 'bytes': 0})
            row['count'] += 1; row['bytes'] += length
            if unknown_upload(relative):
                findings.add('UPLOADS_DIRECTORY_REVIEW_REQUIRED', relative)
        if excluded(relative):
            zone = location(relative)['zone']
            row = excluded_zones.setdefault(zone, {'zone': zone, 'count': 0, 'bytes': 0})
            row['count'] += 1; row['bytes'] += length
            skip_payload(stream, length)
            continue
        chunks = []
        retain = relative == 'package.json' or (retain_sql and relative == 'database.sql' and length <= CHUNK)
        if retain_sql and relative == 'database.sql' and length > CHUNK:
            findings.add('SQL_STREAM_REQUIRED', relative)
        remaining, checksum = length, 0
        while remaining:
            data = stream.read(min(remaining, CHUNK))
            if not data:
                findings.add('ARCHIVE_TRUNCATED', relative)
                if on_chunk is not None:
                    on_chunk(relative, b'', True)
                return result()
            if crc:
                checksum = zlib.crc32(data, checksum)
            if on_chunk is not None and not metadata_limited:
                on_chunk(relative, data, False)
            if retain and not metadata_limited:
                chunks.append(data)
            remaining -= len(data)
        if crc and f'{checksum:08x}'.encode() != crc.lower():
            findings.add('ARCHIVE_CRC_MISMATCH', relative)
        if on_chunk is not None and not metadata_limited:
            on_chunk(relative, b'', True)
        if retain and not metadata_limited:
            payload = b''.join(chunks)
            if relative == 'package.json':
                try:
                    manifest = json.loads(payload)
                    if isinstance(manifest, dict) and (manifest.get('Encrypted') or manifest.get('Compression', {}).get('Enabled')):
                        findings.add('ARCHIVE_ENCODING_UNSUPPORTED', relative)
                except (ValueError, TypeError, AttributeError, RecursionError):
                    pass  # malformed metadata is diagnosed by the manifest consumer
            if on_metadata is not None:
                on_metadata(relative, payload)
            elif relative == 'package.json':
                package = payload
            else:
                sql = payload
        if entries > max_entries:
            break
    return result()


ARCHIVE_REFUSALS = frozenset('ARCHIVE_TRUNCATED ARCHIVE_INVALID ARCHIVE_HEADER ARCHIVE_PATH ARCHIVE_LIMIT ARCHIVE_LAYOUT_UNSUPPORTED MULTISITE_UNSUPPORTED ARCHIVE_TRAILING_DATA ARCHIVE_DATABASE_MISSING ARCHIVE_SIZE_INVALID ARCHIVE_PATH_ABSOLUTE ARCHIVE_PATH_DRIVE ARCHIVE_PATH_EMPTY ARCHIVE_PATH_DOT ARCHIVE_PATH_PARENT ARCHIVE_PATH_BACKSLASH ARCHIVE_PATH_CONTROL ARCHIVE_PATH_DUPLICATE ARCHIVE_PATH_FILE_DIRECTORY_COLLISION ARCHIVE_TARGET_SYMLINK ARCHIVE_CASE_SENSITIVITY_UNVERIFIED ARCHIVE_CASE_INSENSITIVE_TARGET FRESH_CONTENT_REQUIRED UPLOADS_DIRECTORY_REVIEW_REQUIRED DISK_SPACE_INSUFFICIENT ARCHIVE_SEEK_REQUIRED ARCHIVE_CRC_MISMATCH ARCHIVE_EOF_SIZE SQL_STREAM_REQUIRED ARCHIVE_ENCODING_UNSUPPORTED'.split())


class Refusal(ValueError):
    def __init__(self, code, detail=None):
        super().__init__(code)
        self.detail = detail


def probe_case_sensitive(root):
    """Create/read two distinct names on the actual target, then remove both."""
    root = pathlib.Path(root)
    if root.is_symlink() or not root.is_dir():
        raise Refusal('ARCHIVE_TARGET_SYMLINK')
    fd, name = tempfile.mkstemp(prefix='.a01-CaseProbe-', dir=root)
    first = pathlib.Path(name)
    second = first.with_name(first.name.swapcase())
    second_created = False
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(b'A')
        try:
            with second.open('xb') as handle:
                second_created = True
                handle.write(b'B')
        except FileExistsError:
            return False
        return first.read_bytes() == b'A' and second.read_bytes() == b'B' and not first.samefile(second)
    finally:
        if second_created:
            second.unlink()
        first.unlink()


def restore(stream, content, max_bytes=DEFAULT_MAX_BYTES, max_entries=DEFAULT_MAX_ENTRIES, metadata_only=False, case_probe_root=None, report=None, max_sql_bytes=DEFAULT_MAX_SQL_BYTES, sql_path=None):
    start = stream.tell()
    scan = audit(stream, max_bytes, max_entries, max_sql_bytes=max_sql_bytes)
    if report is not None:
        report.update(scan['report'])
    for rule in scan['report']['rules']:
        if rule['blocking']:
            raise Refusal(rule['code'], rule)
    content = pathlib.Path(content) if content is not None else None
    if content is not None and any(p.is_symlink() for p in (content, *content.parents)):
        raise Refusal('ARCHIVE_TARGET_SYMLINK')
    if not metadata_only:
        if content is None or content.exists():
            raise Refusal('FRESH_CONTENT_REQUIRED')
        needed = scan['report']['total_bytes'] - sum(row['bytes'] for row in scan['report']['excluded'])
        check_space(content, needed + 3 * scan['report']['database_bytes'])
        if sql_path is None and scan['report']['database_bytes'] > CHUNK:
            raise Refusal('SQL_STREAM_REQUIRED')
        content.mkdir(parents=True)
    case_rule = next((r for r in scan['report']['rules'] if r['code'] == 'ARCHIVE_PATH_CASE_ONLY'), None)
    if case_rule:
        root = case_probe_root if metadata_only else content
        if root is None:
            raise Refusal('ARCHIVE_CASE_SENSITIVITY_UNVERIFIED', dict(case_rule, code='ARCHIVE_CASE_SENSITIVITY_UNVERIFIED', blocking=True))
        sensitive = probe_case_sensitive(root)
        if report is not None:
            report['target_case_sensitive'] = sensitive
        if not sensitive:
            raise Refusal('ARCHIVE_CASE_INSENSITIVE_TARGET', dict(case_rule, code='ARCHIVE_CASE_INSENSITIVE_TARGET', blocking=True))
    stream.seek(start)
    return _restore_payload(stream, content, max_bytes, max_entries, metadata_only, case_verified=bool(case_rule), case_probe_root=case_probe_root, max_sql_bytes=max_sql_bytes, sql_path=sql_path)


def _restore_payload(stream, content, max_bytes=DEFAULT_MAX_BYTES, max_entries=DEFAULT_MAX_ENTRIES, metadata_only=False, case_verified=False, case_probe_root=None, max_sql_bytes=DEFAULT_MAX_SQL_BYTES, sql_path=None):
    seen, folded, directories = set(), set(), set()
    total = 0
    sql = None
    package = None
    content = pathlib.Path(content) if content is not None else None
    # The full read-only audit completed before any payload is restored.
    for _ in range(max_entries + 1):
        header = stream.read(4377)
        if len(header) != 4377:
            raise Refusal('ARCHIVE_TRUNCATED')
        if eof_block(header):
            if stream.read(1) or 'database.sql' not in seen:
                raise Refusal('ARCHIVE_INVALID')
            return sql, package, len(seen)
        (name, size, stamp, prefix), crc = header_fields(header)
        if (not name or '/' in name or name in ('.', '..')
                or not re.fullmatch(r'[0-9]{1,14}', size) or not re.fullmatch(r'[0-9]{1,12}', stamp)):
            raise Refusal('ARCHIVE_HEADER')
        relative = archive_path(prefix, name)
        parts = relative.split('/')
        for code in path_rules(relative, seen, folded, directories):
            if code == 'ARCHIVE_PATH_CASE_ONLY' and not case_verified:
                root = case_probe_root if metadata_only else content
                if root is None:
                    raise Refusal('ARCHIVE_CASE_SENSITIVITY_UNVERIFIED')
                if not probe_case_sensitive(root):
                    raise Refusal('ARCHIVE_CASE_INSENSITIVE_TARGET')
                case_verified = True
            if code not in ('ARCHIVE_PATH_COLON', 'ARCHIVE_PATH_CASE_ONLY'):
                raise Refusal(code, {'code': code, 'count': 1, 'blocking': True, 'locations': [dict(location(relative), count=1)]})
        length = int(size)
        total += length
        if len(seen) > max_entries or total > max_bytes or (relative == 'database.sql' and length > max_sql_bytes):
            raise Refusal('ARCHIVE_LIMIT')
        if unknown_upload(relative):
            raise Refusal('UPLOADS_DIRECTORY_REVIEW_REQUIRED')
        if excluded(relative) or (metadata_only and relative == 'database.sql'):
            skip_payload(stream, length)
            continue
        # The format exports wp-content-relative paths. Never accept a root config/core tree.
        metadata = relative in ('database.sql', 'package.json', 'multisite.json')
        if not metadata and parts[0] in ('wp-config.php', 'wp-admin', 'wp-includes', 'wp-content'):
            raise Refusal('ARCHIVE_LAYOUT_UNSUPPORTED')
        if relative == 'package.json' and length > 1024 * 1024:
            raise Refusal('ARCHIVE_LIMIT')
        target = content.joinpath(*parts) if content is not None else None
        if not metadata and not metadata_only:
            if any(p.is_symlink() for p in (target, *target.parents)):
                raise Refusal('ARCHIVE_TARGET_SYMLINK', {'code': 'ARCHIVE_TARGET_SYMLINK', 'count': 1, 'blocking': True, 'locations': [dict(location(relative), count=1)]})
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = target.open('xb')
        elif relative == 'database.sql' and not metadata_only and sql_path is not None:
            sql = pathlib.Path(sql_path)
            if sql.exists() or any(p.is_symlink() for p in (sql, *sql.parents)):
                raise Refusal('ARCHIVE_TARGET_SYMLINK')
            handle = sql.open('xb')
        else:
            handle = None
        chunks = []
        try:
            remaining = length
            checksum = 0
            while remaining:
                data = stream.read(min(remaining, 1024*1024))
                if not data:
                    raise Refusal('ARCHIVE_TRUNCATED')
                if crc:
                    checksum = zlib.crc32(data, checksum)
                if handle:
                    handle.write(data)
                elif relative == 'package.json' or (relative == 'database.sql' and not metadata_only):
                    if relative == 'database.sql' and length > CHUNK:
                        raise Refusal('SQL_STREAM_REQUIRED')
                    chunks.append(data)
                remaining -= len(data)
            if crc and f'{checksum:08x}'.encode() != crc.lower():
                raise Refusal('ARCHIVE_CRC_MISMATCH')
        finally:
            if handle:
                handle.close()
        if relative == 'database.sql' and not metadata_only and sql_path is None:
            sql = b''.join(chunks)
        elif relative == 'package.json':
            package = b''.join(chunks)
        elif relative == 'multisite.json':
            raise Refusal('MULTISITE_UNSUPPORTED')
    raise Refusal('ARCHIVE_LIMIT')
