"""A27 closed public schema, canonical JSON/Markdown; no WordPress execution."""
import datetime
import hashlib
import json

UNKNOWN = 'inconnu après neutralisation'
TYPES = ('carte', 'mandat_sepa', 'accord_paypal', 'autre', 'illisible')
EXPIRIES = ('expired', 'within_six_months', 'later', 'illisible')
METRICS = ('subscriptions_unlinked', 'subscriptions_link_unknown', 'tokens_without_living_subscription',
           'tokens_account_unknown', 'accounts_multiple_tokens')
COUNTS = ('automatic', 'cards', 'relations')
GATEWAYS = ('stripe', 'stripe_sepa', 'paypal', 'ppec_paypal', 'ppcp-gateway', 'ppcp-credit-card-gateway',
            'woocommerce_payments', 'bacs', 'cheque', 'cod', 'aucune', 'autre')
MARKDOWN = '# Moyens de paiement enregistrés — lecture seule\n\nComptes seulement ; aucune garantie de renouvellement.\n\n```json\n'


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
        if type(row) is not dict or set(row) != {'gateway', field, 'count'}:
            return False
        if row['gateway'] not in GATEWAYS or row[field] not in allowed or not number(row['count']) or row['count'] < 5:
            return False
        keys.append(row['gateway'] + ':' + row[field])
    return keys == sorted(set(keys))


def projection(data, audit_hash, as_of=None):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts', 'audit_sha256', 'as_of_utc'}:
        return False
    if (data['schema'] != 'imagine-a27-saved-payments-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash or not clock(data['as_of_utc'])
            or as_of is not None and data['as_of_utc'] != as_of):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != set(COUNTS):
        return False
    if data['neutralisation'] == UNKNOWN:
        return all(counts[key] == UNKNOWN for key in COUNTS)
    return (pool_valid(counts['automatic'], 'type', TYPES)
            and pool_valid(counts['cards'], 'expiry', EXPIRIES)
            and pool_valid(counts['relations'], 'metric', METRICS))


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
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'paiements.json', 'paiements.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'paiements.json').read_bytes()
        photo = read(audit.read_bytes())
        data = read(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest(), photo['generated_at_utc'])
                and data['storage'] == photo['sections']['commerce']['order_storage']
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'paiements.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False


def final_binding(stdout, output):
    prefix = b'A27_OK paiements.json paiements.md\nA27_FINAL '
    files = {'paiements.json', 'paiements.md'}
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
