"""Strict uncompressed .wpress reader, preserving wp-content files offline."""
import pathlib
import re
import struct


class Refusal(ValueError):
    pass


def restore(stream, content, max_bytes=1024 * 1024 * 1024, max_entries=150000):
    seen = set()
    total = 0
    sql = None
    package = None
    content = pathlib.Path(content)
    if content.exists():
        raise Refusal('FRESH_CONTENT_REQUIRED')
    content.mkdir(parents=True)
    for _ in range(max_entries + 1):
        header = stream.read(4377)
        if len(header) != 4377:
            raise Refusal('ARCHIVE_TRUNCATED')
        if header == bytes(4377):
            if stream.read(1) or sql is None:
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
        target = content.joinpath(*parts)
        if not metadata:
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
                elif relative in ('database.sql', 'package.json'):
                    chunks.append(data)
                remaining -= len(data)
        finally:
            if handle:
                handle.close()
        if relative == 'database.sql':
            sql = b''.join(chunks)
        elif relative == 'package.json':
            package = b''.join(chunks)
        elif relative == 'multisite.json':
            raise Refusal('MULTISITE_UNSUPPORTED')
    raise Refusal('ARCHIVE_LIMIT')
