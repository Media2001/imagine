"""Read-only A13 adapter. Never invokes A13.controler/ecrire/main."""
from collections import Counter
from importlib.machinery import SourceFileLoader
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[3]
ISSUES = ('compte_a_creer', 'compte_existant', 'sans_email', 'type_a_decider', 'refuse_a13')
PAYMENTS = ('virement', 'domiciliation_papier', 'autre')
OPTIONS = ('importer_echus', 'resoudre_doublons', 'calculer_prochaine_echeance')
UNKNOWN = 'inconnu après neutralisation'


def a13_module():
    loader = SourceFileLoader('a30_readonly_a13', str(HERE.parent / 'controler-export'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


A13 = a13_module()


def validate_config(config):
    bad = RuntimeError('A30_CONFIG_INVALID')
    if (not isinstance(config, dict) or set(config) != {'version', 'types', 'paiements', 'options'}
            or type(config['version']) is not int or config['version'] != 1
            or not isinstance(config['types'], dict) or not isinstance(config['paiements'], dict)
            or not isinstance(config['options'], dict) or set(config['options']) != set(OPTIONS)):
        raise bad
    if (any(not isinstance(k, str) or not k.strip() or type(v) is not int or not 1 <= v <= 2147483647
            for k, v in config['types'].items())
            or any(not isinstance(k, str) or not k.strip() or v not in PAYMENTS
                   for k, v in config['paiements'].items())
            or any(type(v) is not bool for v in config['options'].values())):
        raise bad
    if any(config['options'].values()):
        raise RuntimeError('A30_OPTION_UNSUPPORTED')
    return config


def read_config(path):
    return validate_config(json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=A13.objet_unique))


def grouped(values):
    counts = Counter(values)
    return {'groups': [{'key': k, 'count': v} for k, v in sorted(counts.items(), key=lambda item: str(item[0]))
                       if v >= 5], 'autres': sum(v for v in counts.values() if v < 5)}


def public_reports(result):
    # Construct new documents; never copy child JSON or text to public files.
    neutral = result['neutralised']
    rows = result['rows']
    unresolved = [r['line'] for r in rows if r['issue'] is None]
    lines = {'schema': 'imagine-a30-lines-v1',
             'issues': {issue: [r['line'] for r in rows if r['issue'] == issue] for issue in ISSUES},
             'rapprochement_inconnu': unresolved}
    if neutral:
        for issue in ISSUES[:2]:
            lines['issues'][issue] = UNKNOWN
    report = {'schema': 'imagine-a30-dry-run-v1', 'read_only': True, 'storage': result['storage'],
              'total': len(rows), 'matching': UNKNOWN if neutral else 'observe',
              'accounts': UNKNOWN if neutral else grouped(r['issue'] for r in rows if r['issue'] in ISSUES[:2]),
              'issues': grouped(r['issue'] for r in rows if r['issue'] is not None),
              'products': grouped(r['product'] if r['product'] is not None else 0 for r in rows),
              'payments': grouped(r['payment'] for r in rows),
              'unresolved_matching': len(unresolved), 'business_options': dict.fromkeys(OPTIONS, False)}
    return report, lines


def validate_result(result, prepared):
    if (not isinstance(result, dict) or set(result) != {'schema', 'storage', 'neutralised', 'rows'}
            or result['schema'] != 'imagine-a30-private-v1' or result['storage'] not in ('classic', 'hpos')
            or type(result['neutralised']) is not bool or not isinstance(result['rows'], list)
            or len(result['rows']) != len(prepared['rows'])):
        return False
    for observed, expected in zip(result['rows'], prepared['rows']):
        if (not isinstance(observed, dict) or set(observed) != {'line', 'issue', 'product', 'payment'}
                or type(observed['line']) is not int or observed['line'] != expected['line']
                or observed['payment'] != expected['payment']
                or (observed['product'] is not None and (type(observed['product']) is not int
                                                        or observed['product'] != expected['product']))):
            return False
        issue = observed['issue']
        if expected['rejected']:
            allowed = ('refuse_a13',)
        elif not expected['email']:
            allowed = ('sans_email',)
        elif observed['product'] is None:
            allowed = ('type_a_decider',)
        elif result['neutralised']:
            allowed = (None,)
        else:
            allowed = ISSUES[:2]
        if issue not in allowed:
            return False
    return True


def read_private(stage, prepared):
    try:
        files = list(stage.iterdir())
        if ({p.name for p in files} != {'result.json'} or len(files) != 1
                or any(p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 16777216 for p in files)):
            raise ValueError
        result = json.loads(files[0].read_bytes(), object_pairs_hook=A13.objet_unique)
        if not validate_result(result, prepared):
            raise ValueError
        return result
    except (ValueError, OSError, TypeError, KeyError):
        raise RuntimeError('A30_REPORT_INVALID') from None


def safe_source(source, site=None):
    source = Path(source)
    if source.is_symlink():
        raise RuntimeError('A30_OUTPUT_UNSAFE')
    source = source.resolve(strict=True)
    if not source.is_file() or source.is_relative_to(REPOSITORY):
        raise RuntimeError('A30_OUTPUT_UNSAFE')
    # Reject any repository, not just this checkout. Does not execute Git.
    if any((parent / '.git').exists() for parent in source.parents):
        raise RuntimeError('A30_OUTPUT_UNSAFE')
    if site is not None:
        site = Path(site).resolve(strict=True)
        parent = source.parent
        if (parent == site or site in parent.parents or parent in site.parents):
            raise RuntimeError('A30_OUTPUT_UNSAFE')
    return source


def publish(source, summary, lines):
    source = safe_source(source)
    targets = [source.with_name(source.stem + suffix) for suffix in ('.a30-resume.json', '.a30-lignes.json')]
    if any(p.exists() or p.is_symlink() for p in targets):
        raise RuntimeError('A30_OUTPUT_EXISTS')
    created = []
    try:
        for path, value in zip(targets, (summary, lines)):
            with path.open('x', encoding='utf-8', newline='\n') as stream:
                created.append(path)
                import os
                os.chmod(path, 0o600)
                stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return targets


def prepare(source, mapping, at, config):
    # Exact A13 functions and ordering; no alternate decoder or lenient CSV parser.
    correspondence = A13.lire_config(Path(mapping))
    text, _ = A13.decoder(Path(source).read_bytes(), correspondence['encodage'])
    records, _ = A13.lire_csv(text, correspondence['separateur'])
    header = records[0][1]
    if any(n not in header for n in correspondence['colonnes'].values() if n is not None):
        raise A13.Refus('Correspondance : colonne configurée absente du CSV.')
    rejected, bad, _, _ = A13.analyser(records, correspondence, at)
    defects = {line for line, _ in rejected}
    indexes = {k: header.index(v) if v is not None else None for k, v in correspondence['colonnes'].items()}
    rows = []
    for line, row in records[1:]:
        def value(key):
            return row[indexes[key]].strip() if indexes[key] is not None else ''
        rows.append({'line': line, 'rejected': line in defects,
                     'email': value('email') if line not in defects else '',
                     'product': config['types'].get(value('type_abonnement')),
                     'payment': config['paiements'].get(value('mode_paiement'), 'autre')})
    return {'a13_code': 1 if bad else 0, 'rows': rows}
