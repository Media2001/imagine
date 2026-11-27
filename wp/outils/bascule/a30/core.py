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
