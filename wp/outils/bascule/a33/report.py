"""Closed A33 publication schema; unknown site types never become labels."""
import hashlib
import json

UNKNOWN = 'inconnu après import'
TYPES = ('article', 'numero', 'post', 'page', 'product', 'product_variation', 'autre')
MARKDOWN = '# Poids des archives — lecture seule\n\nNombres seulement ; aucun déplacement.\n\n```json\n'


def number(v):
    return type(v) is int and 0 <= v <= 2**53 - 1


def year(v):
    return type(v) is int and 1000 <= v <= 9999 or v == 'inconnu'


def media(v, imported):
    if type(v) is not dict or set(v) != {'count', 'present', 'missing', 'known_bytes', 'total_bytes'}:
        return False
    if not all(number(v[k]) for k in ('count', 'present', 'missing', 'known_bytes')):
        return False
    expected = UNKNOWN if imported else 'inconnu fichiers absents'
    return (v['count'] == v['present'] + v['missing']
            and (v['total_bytes'] == expected if v['missing'] else type(v['total_bytes']) is int and v['total_bytes'] == v['known_bytes'])
            and (v['present'] > 0 or v['known_bytes'] == 0))


def projection(d, audit_hash, mapping_hash):
    if type(d) is not dict or set(d) != {'schema', 'read_only', 'imported', 'selected_issues', 'published_outside', 'outside_media_by_year', 'orphan_media', 'recent_media', 'other_media', 'excluded_directories_bytes', 'audit_sha256', 'mapping_sha256'}:
        return False
    if (d['schema'] != 'imagine-a33-archives-v1' or d['read_only'] is not True or type(d['imported']) is not bool
            or not number(d['selected_issues']) or d['selected_issues'] > 10
            or d['audit_sha256'] != audit_hash or d['mapping_sha256'] != mapping_hash
            or d['excluded_directories_bytes'] != (UNKNOWN if d['imported'] else 'non évalué')):
        return False
    for key in ('orphan_media', 'recent_media', 'other_media'):
        if not media(d[key], d['imported']):
            return False
    for key, fields in [('published_outside', {'type', 'year', 'count'}), ('outside_media_by_year', {'year', 'files'})]:
        if type(d[key]) is not list:
            return False
        seen = []
        for r in d[key]:
            if type(r) is not dict or set(r) != fields or not year(r['year']):
                return False
            if key == 'published_outside':
                if r['type'] not in TYPES or not number(r['count']) or r['count'] == 0:
                    return False
                seen.append((r['type'], str(r['year'])))
            else:
                if not media(r['files'], d['imported']) or r['files']['count'] == 0:
                    return False
                seen.append((str(r['year']),))
        if seen != sorted(set(seen)):
            return False
    return True


def read(raw):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate')
            d[k] = v
        return d
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def complete_report(output, audit, mapping):
    try:
        names = {'archives.json', 'archives.md'}
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()} != names:
            return False
        if any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 1048576 for p in output.iterdir()):
            return False
        raw = (output / 'archives.json').read_bytes()
        d = read(raw)
        return (projection(d, hashlib.sha256(audit.read_bytes()).hexdigest(), hashlib.sha256(mapping.read_bytes()).hexdigest())
                and raw == (json.dumps(d, ensure_ascii=False, indent=4, allow_nan=False) + '\n').encode('utf-8')
                and (output / 'archives.md').read_bytes() == MARKDOWN.encode('utf-8') + raw + b'```\n')
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        return False


def final_binding(stdout, output):
    prefix = b'A33_OK archives.json archives.md\nA33_FINAL '
    try:
        if not stdout.startswith(prefix) or not stdout.endswith(b'\n'):
            return False
        d = read(stdout[len(prefix):-1])
        return type(d) is dict and set(d) == {'archives.json', 'archives.md'} and d == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    except (OSError, ValueError, TypeError):
        return False
