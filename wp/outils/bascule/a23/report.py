"""Closed A23 publication schema. No site-derived text is permitted."""
import hashlib
import json
from pathlib import Path

MARKDOWN = '# Comptes des lecteurs — lecture seule\n\nComptes seulement ; aucune activation ni décision de reprise.\n\n```json\n'
UNKNOWN = 'inconnu après neutralisation'
LABELS = {
    'families': ['phpass', 'phpass_h', 'wordpress_bcrypt', 'bcrypt', 'argon2i', 'argon2id', 'autre', 'vide'],
    'emails': ['email_empty', 'email_malformed', 'email_shared_case_insensitive'],
    'logins': ['login_equals_email', 'login_case_collision'],
    'without_commerce': ['without_order_or_subscription'],
}


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def pool_valid(pool, labels, accounts, partition=False):
    if type(pool) is not dict or set(pool) != {'groups', 'autres'}:
        return False
    if type(pool['groups']) is not list or not number(pool['autres']):
        return False
    seen = []
    total = pool['autres']
    for group in pool['groups']:
        if type(group) is not dict or set(group) != {'label', 'accounts'}:
            return False
        label, count = group['label'], group['accounts']
        if label not in labels or label in seen or not number(count) or not 5 <= count <= accounts:
            return False
        seen.append(label)
        total += count
    return (seen == sorted(seen, key=labels.index) and pool['autres'] <= 4 * (len(labels) - len(seen))
            and (total == accounts if partition else total <= accounts * len(labels)))


def projection(data, audit_hash):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'counts', 'audit_sha256'}:
        return False
    if (data['schema'] != 'imagine-a23-reader-accounts-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash):
        return False
    counts = data['counts']
    if type(counts) is not dict or set(counts) != {'readers', 'live_readers', 'without_commerce'}:
        return False
    for name in ('readers', 'live_readers'):
        section = counts[name]
        if type(section) is not dict or set(section) != {'accounts', 'families', 'emails', 'logins'}:
            return False
        if not number(section['accounts']):
            return False
        for key in ('families', 'emails', 'logins'):
            if data['neutralisation'] == UNKNOWN:
                if section[key] != UNKNOWN:
                    return False
            elif not pool_valid(section[key], LABELS[key], section['accounts'], key == 'families'):
                return False
    n = counts['readers']['accounts']
    return (counts['live_readers']['accounts'] <= n
            and pool_valid(counts['without_commerce'], LABELS['without_commerce'], n))


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != {'comptes.json', 'comptes.md'}:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'comptes.json').read_bytes()
        data = json.loads(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest())
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'comptes.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False
