"""Closed A31 public schema; only native PHP computes business counts."""
import hashlib
import json

UNKNOWN = 'inconnu après neutralisation'
STATUSES = ('pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed', 'checkout-draft', 'autre')
NATURES = ('parent', 'renewal', 'switch', 'resubscribe', 'none', 'illisible')
UNREADABLE_AFTER_IMPORT = ('natures',)
READABLE_AFTER_IMPORT = ('years', 'statuses', 'orphan_renewals', 'structural_links', 'refunds', 'oldest_year')
COUNTS = READABLE_AFTER_IMPORT + UNREADABLE_AFTER_IMPORT
MARKDOWN = '# Historique des commandes — lecture seule\n\nNombres seulement ; aucune réparation.\n\n```json\n'


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def year(value):
    return type(value) is int and 1000 <= value <= 9999 or value == 'illisible'


def pool_valid(pool, fields):
    if type(pool) is not dict or set(pool) != {'groups', 'autres'} or not number(pool['autres']) or type(pool['groups']) is not list:
        return False
    keys = []
    for row in pool['groups']:
        if type(row) is not dict or set(row) != set(fields) | {'count'} or not number(row['count']) or row['count'] < 5:
            return False
        if any(not predicate(row[key]) for key, predicate in fields.items()):
            return False
        keys.append(tuple(str(row[key]) for key in fields))
    return keys == sorted(set(keys))


def projection(data, audit_hash):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts', 'audit_sha256'}:
        return False
    if (data['schema'] != 'imagine-a31-history-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != set(COUNTS):
        return False
    schemas = {'years': {'year': year}, 'statuses': {'year': year, 'status': lambda v: v in STATUSES},
               'natures': {'nature': lambda v: v in NATURES},
               'orphan_renewals': {'metric': lambda v: v == 'renewals_missing_subscription'},
               'structural_links': {'metric': lambda v: v in ('living_without_parent', 'orders_missing_account', 'orders_link_unknown')},
               'refunds': {'year': year}}
    for key, fields in schemas.items():
        if data['neutralisation'] == UNKNOWN and key in UNREADABLE_AFTER_IMPORT:
            if counts[key] != UNKNOWN:
                return False
        elif not pool_valid(counts[key], fields):
            return False
    oldest = counts['oldest_year']
    years = counts['years']
    if oldest is None:
        return not years['groups'] and years['autres'] == 0
    if oldest in ('fusionne', 'illisible'):
        return bool(years['groups'] or years['autres'])
    return (type(oldest) is int and 1000 <= oldest <= 9999
            and any(row['year'] == oldest for row in years['groups'])
            and all(type(row['year']) is int and row['year'] >= oldest for row in years['groups']))


def read(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'commandes.json', 'commandes.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'commandes.json').read_bytes()
        photo, data = read(audit.read_bytes()), read(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest())
                and data['storage'] == photo['sections']['commerce']['order_storage']
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'commandes.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False


def final_binding(stdout, output):
    prefix = b'A31_OK commandes.json commandes.md\nA31_FINAL '
    files = {'commandes.json', 'commandes.md'}
    try:
        if not stdout.startswith(prefix) or not stdout.endswith(b'\n') or output.is_symlink() or not output.is_dir():
            return False
        if {p.name for p in output.iterdir()} != files or any(
                p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        digest = read(stdout[len(prefix):-1])
        return type(digest) is dict and set(digest) == files and digest == {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    except (OSError, ValueError, TypeError):
        return False
