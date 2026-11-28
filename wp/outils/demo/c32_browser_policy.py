"""Règles pures C32 : aucun transport, navigateur, cookie-valeur ou accès site."""
import sys
sys.dont_write_bytecode = True

READING_NATIVE = frozenset([
    'sbjs_migrations', 'sbjs_current_add', 'sbjs_first_add',
    'sbjs_current', 'sbjs_first', 'sbjs_udata', 'sbjs_session',
])
STRICT_CHECK = 'lecture_zero_cookie_strict'


def public_paths(fixture, pages, extension):
    """Réutiliser l'identité des URL C26, sans modifier sa matrice close."""
    if extension.get('scope') != 'imagine-test-demo' or any(not extension.get(k) for k in ['pages', 'events']):
        raise ValueError('Inventaire public C26 absent ou vide')
    extra = [r['path'] for kind in ['pages', 'events'] for r in extension[kind]]
    if any(not p.startswith('/') or p.startswith('//') or '?' in p or '#' in p for p in extra):
        raise ValueError('URL C26 non locale')
    return list(dict.fromkeys(
        ['/', fixture['article_path'], fixture['issue_path'], fixture['term_path'], '/evenements/']
        + [r['path'] for r in pages.values()]
        + [r['path'] for r in fixture['posts']]
        + ['/numeros/'+r['slug']+'/' for r in fixture['issues']]
        + extra
    ))


def coverage(observed, expected):
    found, wanted = set(observed), set(expected)
    return {'pass': bool(wanted) and found == wanted and len(observed) == len(found),
            'expected_paths': sorted(wanted), 'missing': sorted(wanted-found), 'extra': sorted(found-wanted)}


def reading_verdict(rows):
    reading = [r for r in rows if r['kind'] == 'lecture']
    names = {n for r in reading for n in r['header_names']} | {c['name'] for r in reading for c in r['browser']}
    return {'pages': len(reading), 'strict_pass': bool(reading) and not names,
            'inventory_pass': bool(reading) and names <= READING_NATIVE,
            'observed_names': sorted(names), 'unexpected_reading_names': sorted(names-READING_NATIVE),
            'allowed_native_names': sorted(READING_NATIVE)}


def _by_key(rows):
    indexed = {r['session_key']: r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError('Clés de session dupliquées')
    return indexed


def restore_sessions(before, current, owned_keys, replace, readback):
    """Restaurer seulement les clés attribuées ; CAS fourni par le transport.

    Toute différence étrangère, y compris une arrivée pendant le nettoyage,
    reste intacte et interdit de déclarer une restauration globale réussie.
    Le résultat public ne contient aucune clé ni valeur de session.
    """
    old, now = _by_key(before), _by_key(current)
    changed = {k for k in old.keys() | now.keys() if old.get(k) != now.get(k)}
    conflicts = 0
    for key in sorted(changed & set(owned_keys)):
        if not replace(key, now.get(key), old.get(key)):
            conflicts += 1
    after = _by_key(readback())
    remaining = {k for k in old.keys() | after.keys() if old.get(k) != after.get(k)}
    foreign = (changed | remaining) - set(owned_keys)
    return {'restored': not remaining and not foreign and conflicts == 0,
            'foreign_changes': len(foreign), 'write_conflicts': conflicts,
            'owned_remaining': len(remaining & set(owned_keys))}
