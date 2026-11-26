"""A29 closed public schema and final-byte binding. No site execution."""
import datetime
import hashlib
import json

UNKNOWN = 'inconnu après neutralisation'
INDETERMINATE = 'attribution indéterminée'
FAMILIES = ('renouvellement', 'nouvelle_tentative', 'fin_abonnement', 'email',
            'entretien_woocommerce', 'entretien_wordpress', 'autre')
COUNTS = ('pending', 'overdue', 'failed', 'renewal_weeks', 'other_tasks', 'other_active_extensions')
MARKDOWN = '# Tâches planifiées — lecture seule\n\nComptes seulement ; aucune tâche exécutée.\n\n```json\n'


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def clock(value):
    if type(value) is not str:
        return False
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y-%m-%dT%H:%M:%S+00:00') == value
    except ValueError:
        return False


def pool_valid(pool, field, allowed):
    if type(pool) is not dict or set(pool) != {'groups', 'autres'} or not number(pool['autres']) or type(pool['groups']) is not list:
        return False
    keys = []
    for row in pool['groups']:
        if type(row) is not dict or set(row) != {field, 'count'}:
            return False
        value = row[field]
        if type(value) not in (str, int) or type(value) is bool or value not in allowed or not number(row['count']) or row['count'] < 5:
            return False
        keys.append(value)
    return keys == sorted(set(keys))


def rare_scalar(value):
    return value == 'moins de cinq' or number(value) and (value == 0 or value >= 5)


def projection(data, audit_hash, as_of=None):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts',
                                              'audit_sha256', 'as_of_utc', 'failed_scope', 'window'}:
        return False
    if (data['schema'] != 'imagine-a29-scheduled-tasks-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['failed_scope'] != 'action_scheduler_only' or data['window'] != 'eight_rolling_utc_weeks'
            or data['audit_sha256'] != audit_hash or not clock(data['as_of_utc'])
            or as_of is not None and data['as_of_utc'] != as_of):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != set(COUNTS):
        return False
    if data['neutralisation'] == UNKNOWN:
        return all(counts[key] == UNKNOWN for key in COUNTS)
    return (all(pool_valid(counts[key], 'family', FAMILIES) for key in ('pending', 'overdue', 'failed'))
            and pool_valid(counts['renewal_weeks'], 'week', tuple(range(1, 9)))
            and rare_scalar(counts['other_tasks'])
            and (counts['other_active_extensions'] == INDETERMINATE or rare_scalar(counts['other_active_extensions'])))


def read(raw):
    def pairs(items):
        d = {}
        for key, value in items:
            if key in d:
                raise ValueError('duplicate')
            d[key] = value
        return d
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'taches.json', 'taches.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'taches.json').read_bytes()
        photo = read(audit.read_bytes())
        data = read(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest(), photo['generated_at_utc'])
                and data['storage'] == photo['sections']['commerce']['order_storage']
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'taches.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False


def final_binding(stdout, output):
    prefix = b'A29_OK taches.json taches.md\nA29_FINAL '
    files = {'taches.json', 'taches.md'}
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
