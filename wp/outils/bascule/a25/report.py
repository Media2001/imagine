"""Closed visitor report schema: reject forged data before publication."""
import hashlib
import json

UNKNOWN = 'inconnu après neutralisation'
INDETERMINATE = 'couverture indéterminée'
EDITORIAL_WARNING = 'avertissement éditorial permanent, non mesuré sur la copie inspectée'
MARKDOWN = '# Données des visiteurs — lecture seule\n\nComptes seulement ; aucune suppression ni durée de conservation.\n\n```json\n'
STATES = ('0', '1', 'spam', 'trash', 'post-trashed', 'autre')


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def pool_valid(pool, states):
    if type(pool) is not dict or set(pool) != {'groups', 'autres'} or not number(pool['autres']):
        return False
    if type(pool['groups']) is not list:
        return False
    keys = []
    for row in pool['groups']:
        if type(row) is not dict or set(row) != {'year', 'state', 'count'}:
            return False
        if (not number(row['year']) or row['year'] not in [0] and not 1000 <= row['year'] <= 9999
                or row['state'] not in states or not number(row['count']) or row['count'] < 5):
            return False
        keys.append(str(row['year']) + ':' + row['state'])
    return keys == sorted(set(keys))


def projection(data, audit_hash):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts', 'forms', 'audit_sha256'}:
        return False
    if (data['schema'] != 'imagine-a25-visitor-retention-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash):
        return False
    forms = data['forms']
    if (type(forms) is not dict or set(forms) != {'listed_extensions', 'other_tables', 'coverage',
                                                'clear_messages_after_import', 'clear_messages_after_import_label'}
            or forms['listed_extensions'] not in ([], ['Fluent Forms']) or not number(forms['other_tables'])
            or forms['coverage'] not in ('heuristique bornée', INDETERMINATE)
            or forms['clear_messages_after_import'] is not True
            or forms['clear_messages_after_import_label'] != EDITORIAL_WARNING):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != {'comments', 'forms', 'guests'}:
        return False
    comments = counts['comments']
    if type(comments) is not dict or set(comments) != {'all', 'email', 'ip', 'account'}:
        return False
    for key in ('all', 'email', 'ip', 'account'):
        if data['neutralisation'] == UNKNOWN and key in ('email', 'ip'):
            if comments[key] != UNKNOWN:
                return False
        elif not pool_valid(comments[key], STATES):
            return False
    if data['neutralisation'] == UNKNOWN:
        if counts['forms'] != UNKNOWN:
            return False
    elif forms['coverage'] == INDETERMINATE:
        if counts['forms'] != INDETERMINATE:
            return False
    elif not pool_valid(counts['forms'], ('Fluent Forms', 'autre')):
        return False
    return pool_valid(counts['guests'], ('guest',))


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'visiteurs.json', 'visiteurs.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'visiteurs.json').read_bytes()
        data = json.loads(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest())
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'visiteurs.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False
