"""A24 closed publication schema, validated only after PHP and both EOFs."""
import hashlib
import json
from pathlib import Path

MARKDOWN = '# Adresses d’expédition — lecture seule\n\nComptes seulement ; aucune adresse ni décision postale.\n\n```json\n'
UNKNOWN = 'inconnu après neutralisation'
FIELDS = ['shipping_' + field for field in ('first_name', 'last_name', 'company', 'country', 'address_1',
          'address_2', 'city', 'state', 'postcode', 'phone')]
COUNTRIES = json.loads((Path(__file__).resolve().parent / 'country_codes.json').read_text(encoding='utf-8'))
METRICS = {'subscriptions', 'shipping_empty', 'empty_with_billing', 'missing_any', 'missing_required',
           'country_absent', 'country_unknown', 'different_from_account', 'account_unavailable'}
ERASED = {'shipping_empty', 'empty_with_billing', 'missing_any', 'different_from_account'}


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def valid_counts(counts, neutral):
    if type(counts) is not dict or set(counts) != METRICS or not number(counts['subscriptions']):
        return False
    total = counts['subscriptions']
    for key, value in counts.items():
        if key == 'missing_required':
            if type(value) is not dict or list(value) != FIELDS:
                return False
            for field, count in value.items():
                if neutral and field != 'shipping_country':
                    if count != UNKNOWN:
                        return False
                elif not number(count) or count > total:
                    return False
        elif neutral and key in ERASED:
            if value != UNKNOWN:
                return False
        elif not number(value) or value > total:
            return False
    if counts['country_absent'] + counts['country_unknown'] > total:
        return False
    if not neutral and (counts['empty_with_billing'] > counts['shipping_empty']
                        or counts['different_from_account'] + counts['account_unavailable'] > total
                        or any(v > counts['missing_any'] for v in counts['missing_required'].values())):
        return False
    return True


def projection(data, audit_hash):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts', 'audit_sha256'}:
        return False
    if (data['schema'] != 'imagine-a24-shipping-addresses-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != {'overall', 'countries'} or type(counts['countries']) is not list:
        return False
    neutral = data['neutralisation'] == UNKNOWN
    if not valid_counts(counts['overall'], neutral):
        return False
    labels = []
    groups = []
    for group in counts['countries']:
        if type(group) is not dict or set(group) != {'country', 'counts'}:
            return False
        label = group['country']
        if type(label) is not str or label not in COUNTRIES + ['country_absent', 'country_unknown', 'autres pays'] or label in labels:
            return False
        section = group['counts']
        if not valid_counts(section, neutral) or section['subscriptions'] < (1 if label == 'autres pays' else 5):
            return False
        labels.append(label)
        groups.append(section)
    expected_order = sorted(label for label in labels if label != 'autres pays') + (['autres pays'] if 'autres pays' in labels else [])
    if labels != expected_order:
        return False
    for key, value in counts['overall'].items():
        if key == 'missing_required':
            for field, count in value.items():
                if count != UNKNOWN and sum(g[key][field] for g in groups) != count:
                    return False
        elif value != UNKNOWN and sum(g[key] for g in groups) != value:
            return False
    return True


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'expedition.json', 'expedition.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'expedition.json').read_bytes()
        data = json.loads(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest())
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'expedition.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False
