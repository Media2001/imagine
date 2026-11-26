"""Closed aggregate-only schema, canonical bytes, and final file binding."""
import hashlib
import json

UNKNOWN = 'inconnu après neutralisation'
FAMILIES = ('mesure', 'pixel', 'consentement', 'partage', 'carte', 'video', 'audio', 'polices', 'formulaire_externe', 'anti_robot')
SERVICES = ('youtube', 'vimeo', 'dailymotion', 'soundcloud', 'spotify', 'mixcloud', 'google_maps', 'openstreetmap', 'facebook', 'instagram', 'twitter', 'tiktok', 'autre')
MARKDOWN = '# Ressources tierces — lecture seule\n\nDéclarations et intégrations statiques ; ni requêtes observées ni conformité.\n\n```json\n'
FILES = {'tiers.json', 'tiers.md'}


def number(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def counts(value):
    return type(value) is dict and set(value) == set(SERVICES) and all(number(n) for n in value.values())


def projection(data, audit_hash):
    if type(data) is not dict or set(data) != {'schema', 'read_only', 'storage', 'neutralisation', 'families', 'content', 'audit_sha256'}:
        return False
    if (data['schema'] != 'imagine-a26-third-parties-v1' or data['read_only'] is not True
            or data['storage'] not in ('classic', 'hpos') or data['neutralisation'] not in ('observe', UNKNOWN)
            or data['audit_sha256'] != audit_hash):
        return False
    families = data['families']
    if type(families) is not dict or set(families) != set(FAMILIES):
        return False
    for row in families.values():
        if type(row) is not dict or set(row) != {'active', 'identifier'}:
            return False
        if not (number(row['active']) or (data['neutralisation'] == UNKNOWN and row['active'] == UNKNOWN)):
            return False
        if row['identifier'] not in ('oui', 'non', 'illisible', UNKNOWN):
            return False
        if row['identifier'] == UNKNOWN and data['neutralisation'] != UNKNOWN:
            return False
        if row['active'] == UNKNOWN and row['identifier'] != UNKNOWN:
            return False
        if row['active'] == 0 and row['identifier'] != 'non':
            return False
    content = data['content']
    if data['neutralisation'] == UNKNOWN:
        return content == UNKNOWN
    if type(content) is not dict or set(content) != {'all', 'selection'} or not counts(content['all']):
        return False
    selection = content['selection']
    if type(selection) is not dict or set(selection) != {'mode', 'years', 'last_ten'}:
        return False
    if selection['mode'] == 'dix_derniers':
        return selection['years'] == [] and counts(selection['last_ten']) and all(selection['last_ten'][k] <= content['all'][k] for k in SERVICES)
    if selection['mode'] != 'annee' or selection['last_ten'] is not None or type(selection['years']) is not list:
        return False
    years = []
    summed = dict.fromkeys(SERVICES, 0)
    for row in selection['years']:
        if type(row) is not dict or set(row) != {'year', 'counts'} or type(row['year']) is not int or not (row['year'] == 0 or 1000 <= row['year'] <= 9999) or not counts(row['counts']):
            return False
        years.append(row['year'])
        for key in SERVICES:
            summed[key] += row['counts'][key]
    return years == sorted(set(years)) and summed == content['all']


def complete_report(output, audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != FILES:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'tiers.json').read_bytes()
        data = json.loads(raw)
        return (projection(data, hashlib.sha256(audit.read_bytes()).hexdigest())
                and raw == (json.dumps(data, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'tiers.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False


def final_binding(stdout, output):
    prefix = b'A26_OK tiers.json tiers.md\nA26_FINAL '
    try:
        if not stdout.startswith(prefix) or not stdout.endswith(b'\n') or output.is_symlink() or not output.is_dir():
            return False
        if {p.name for p in output.iterdir()} != FILES or any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        digest = json.loads(stdout[len(prefix):-1])
        return type(digest) is dict and set(digest) == FILES and digest == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    except (ValueError, OSError, TypeError):
        return False
