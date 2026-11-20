#!/usr/bin/python3
"""Trusted offline entrypoints. Imported PHP is never copied or executed."""
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import sys

PROTOCOL = 'staging-offline-v1'
ROOT = Path('/var/www/html')
SOCKET = '/run/mysqld/mysqld.sock'
WORKFLOW = Path('/workflow/wp/outils')
TRUSTED = Path('/opt/staging')


class Refusal(ValueError):
    pass


def read_archive(stream, *, max_bytes=512 * 1024 * 1024, max_entries=100000):
    """Read the documented uncompressed 4377-byte format; discard ALL file payloads.

    Only database.sql is retained in memory, not on the web volume. Encrypted,
    compressed, multi-volume and malformed archives have no fallback.
    """
    seen, sql, total = set(), None, 0
    for _ in range(max_entries + 1):
        header = stream.read(4377)
        if len(header) != 4377:
            raise Refusal('ARCHIVE_TRUNCATED')
        if header == bytes(4377):
            if stream.read(1) or sql is None:
                raise Refusal('ARCHIVE_INVALID')
            return sql, len(seen)
        raw_name, raw_size, raw_mtime, raw_prefix = struct.unpack('255s14s12s4096s', header)
        def field(raw):
            value, _, padding = raw.partition(b'\0')
            if padding.strip(b'\0'):
                raise Refusal('ARCHIVE_HEADER')
            try:
                return value.decode('utf-8', 'strict')
            except UnicodeError:
                raise Refusal('ARCHIVE_HEADER') from None
        name, size, stamp, prefix = map(field, (raw_name, raw_size, raw_mtime, raw_prefix))
        if (not name or '/' in name or name in ('.', '..') or not re.fullmatch(r'[0-9]{1,14}', size)
                or not re.fullmatch(r'[0-9]{1,12}', stamp)):
            raise Refusal('ARCHIVE_HEADER')
        path = prefix + '/' + name if prefix else name
        parts = path.split('/')
        if (path.startswith('/') or any(p in ('', '.', '..') for p in parts)
                or any(ord(c) < 32 or c in '\\:' for c in path) or path.casefold() in seen):
            raise Refusal('ARCHIVE_PATH')
        seen.add(path.casefold())
        if len(seen) > max_entries:
            raise Refusal('ARCHIVE_LIMIT')
        length = int(size)
        total += length
        if total > max_bytes or (path == 'database.sql' and length > 64 * 1024 * 1024):
            raise Refusal('ARCHIVE_LIMIT')
        remaining, blocks = length, []
        while remaining:
            data = stream.read(min(remaining, 1024 * 1024))
            if not data:
                raise Refusal('ARCHIVE_TRUNCATED')
            if path == 'database.sql':
                blocks.append(data)
            remaining -= len(data)
        if path == 'database.sql':
            sql = b''.join(blocks)
    raise Refusal('ARCHIVE_LIMIT')


TOKEN = re.compile(r"(?P<space>\s+)|(?P<comment>--[^\n]*|\#[^\n]*)|(?P<id>`[a-zA-Z0-9_]+`)|(?P<string>'(?:[^'\\]|\\.|'')*')|(?P<number>-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)|(?P<word>[A-Za-z_][A-Za-z0-9_]*)|(?P<symbol>[(),;=+])", re.S)
CREATE_WORDS = set(('TINYINT SMALLINT MEDIUMINT INT INTEGER BIGINT DECIMAL NUMERIC FLOAT DOUBLE REAL BIT BOOL BOOLEAN DATE DATETIME TIMESTAMP TIME YEAR CHAR VARCHAR BINARY VARBINARY TINYBLOB BLOB MEDIUMBLOB LONGBLOB TINYTEXT TEXT MEDIUMTEXT LONGTEXT JSON ENUM SET UNSIGNED SIGNED ZEROFILL NOT NULL DEFAULT AUTO_INCREMENT PRIMARY KEY UNIQUE INDEX FULLTEXT SPATIAL USING BTREE HASH COMMENT COLLATE CHARACTER INNODB UTF8 UTF8MB3 UTF8MB4 LATIN1 UTF8MB4_UNICODE_CI UTF8MB4_UNICODE_520_CI UTF8MB4_GENERAL_CI UTF8_GENERAL_CI LATIN1_SWEDISH_CI CURRENT_TIMESTAMP').split())


def sql_plan(payload):
    try:
        text = payload.decode('utf-8', 'strict')
    except UnicodeError:
        raise Refusal('SQL_ENCODING') from None
    tokens, position = [], 0
    while position < len(text):
        match = TOKEN.match(text, position)
        if not match:
            raise Refusal('SQL_GRAMMAR')
        if match.lastgroup not in ('space', 'comment'):
            tokens.append((match.lastgroup, match.group()))
        position = match.end()
    groups, group = [], []
    for token in tokens:
        if token[1] == ';':
            if group:
                groups.append(group)
            group = []
        else:
            group.append(token)
    if group:
        raise Refusal('SQL_TERMINATOR')
    creates, inserts, statements = set(), [], []
    def ident(t):
        if t[0] != 'id' or len(t[1]) > 66:
            raise Refusal('SQL_IDENTIFIER')
        return t[1][1:-1]
    for group in groups:
        v = [t[1].upper() if t[0] == 'word' else t[1] for t in group]
        if v in (['SET', 'NAMES', 'UTF8MB4'], ['SET', 'NAMES', 'UTF8'],
                 ['SET', 'FOREIGN_KEY_CHECKS', '=', '0'], ['SET', 'FOREIGN_KEY_CHECKS', '=', '1']):
            continue
        if v[:4] == ['DROP', 'TABLE', 'IF', 'EXISTS'] and len(group) == 5:
            ident(group[4])
            continue
        if v[:2] == ['CREATE', 'TABLE'] and len(group) > 8:
            table = ident(group[2])
            if table in creates or v[3] != '(':
                raise Refusal('SQL_TABLE')
            depth, end = 0, None
            for i in range(3, len(group)):
                if v[i] == '(':
                    depth += 1
                elif v[i] == ')':
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
                elif group[i][0] == 'word' and v[i] not in CREATE_WORDS:
                    raise Refusal('SQL_DDL')
            if end is None or depth != 0:
                raise Refusal('SQL_DDL')
            tail = ' '.join(v[end + 1:])
            if not re.fullmatch(r'ENGINE = INNODB(?: (?:DEFAULT )?(?:CHARSET|CHARACTER SET) = (?:UTF8MB4|UTF8|UTF8MB3|LATIN1))?(?: COLLATE = [A-Z0-9_]+)?(?: AUTO_INCREMENT = [0-9]+)?', tail):
                raise Refusal('SQL_DDL')
            creates.add(table)
        elif v[:2] == ['INSERT', 'INTO'] and len(group) > 5:
            table, i = ident(group[2]), 3
            if v[i] == '(':
                i += 1
                while True:
                    ident(group[i]); i += 1
                    if v[i] == ')':
                        i += 1
                        break
                    if v[i] != ',':
                        raise Refusal('SQL_INSERT')
                    i += 1
            if v[i] != 'VALUES':
                raise Refusal('SQL_INSERT')
            i += 1
            while i < len(group):
                if v[i] != '(':
                    raise Refusal('SQL_INSERT')
                i += 1
                while True:
                    if group[i][0] not in ('number', 'string') and v[i] != 'NULL':
                        raise Refusal('SQL_INSERT_LITERAL')
                    i += 1
                    if v[i] == ')':
                        i += 1
                        break
                    if v[i] != ',':
                        raise Refusal('SQL_INSERT')
                    i += 1
                if i == len(group):
                    break
                if v[i] != ',':
                    raise Refusal('SQL_INSERT')
                i += 1
                if i == len(group):
                    raise Refusal('SQL_INSERT')
            inserts.append(table)
        else:
            raise Refusal('SQL_STATEMENT')
        statements.append(' '.join(t[1] for t in group))
    prefixes = [t[:-7] for t in creates if t.endswith('_options')]
    if len(prefixes) != 1 or not prefixes[0] or any(not t.startswith(prefixes[0]) for t in creates):
        raise Refusal('SQL_PREFIX')
    if any(t not in creates for t in inserts):
        raise Refusal('SQL_TABLE')
    return {'prefix': prefixes[0], 'statements': statements}
