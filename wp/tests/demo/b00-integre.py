"""Recette intégrée B00 : preuves exclusivement production/B-00.
--rejouer effectue vraiment le seed C08 puis le CLI construire.py ; sinon lecture/HTTP.
Les recettes tierces sont importées intactes, leurs sorties restent dans ce lot.
"""
from pathlib import Path
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import construire as b00
import c08

ROOT = b00.ROOT
PROOF = ROOT / 'production/B-00'
TESTS = Path(__file__).resolve().parent


def save(name, value):
    path = PROOF / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), TESTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native(name, prefix=''):
    path = TESTS / (name + '.php')
    b00.upload('imagine-demo-build/' + path.name, path.read_bytes())
    result = b00.wp('eval', prefix + 'require WP_CONTENT_DIR . "/imagine-demo-build/' + path.name + '";', check=False)
    data = json.loads(result['stdout'])
    save('tests/' + name + '-actuel.json', {'exit': result['code'], 'stderr': result['stderr'], 'result': data})
    return result, data


def snapshot():
    return json.loads(b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/b00-integre-snapshot.php";')['stdout'])


def run(replay=False):
    site, _ = c08.guard()
    if site['url'].rstrip('/') != 'http://192.168.129.32:8085':
        raise RuntimeError('Cible B00 différente')
    if replay:
        # Même fonction et même branche que c08.py --seed ; seul le dossier de reçus est redirigé.
        c08.PROOF = PROOF / 'rejeu-c08-seed'
        c08.PROOF.mkdir(parents=True, exist_ok=True)
        c08.run(seed=True)
        result = subprocess.run([sys.executable, str(ROOT / 'wp/outils/demo/construire.py'), '--preuve', 'reconstruction'],
                                capture_output=True, text=True, encoding='utf-8', timeout=900)
        (PROOF / 'tests/b00-post-c08-reconstruction.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
        if result.returncode:
            raise RuntimeError('Reconstruction CLI post-C08 échouée')
    protected = snapshot()
    checks, suites = {}, {}
    stream = io.StringIO()
    suite = unittest.TestSuite()
    for pattern in ['test_b00*.py', 'test_c08_scope.py', 'test_c09_profils.py', 'test_c10_scope.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(TESTS), pattern=pattern))
    local = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    local_data = {'total': local.testsRun, 'failures': len(local.failures), 'errors': len(local.errors),
                  'skipped': len(local.skipped), 'output': stream.getvalue()}
    save('tests/b00-unitaires-actuels.json', local_data)
    checks['unitaires_sans_ignore'] = local.wasSuccessful() and not local.skipped
    suites['unitaires'] = local.testsRun
    for name in ['b00-recette', 'b00-corrections-runtime', 'c08-runtime', 'c10-runtime']:
        raw, data = native(name)
        checks[name] = raw['code'] == 0 and not raw['stderr'] and not data['failures']
        suites[name] = data['total']
    # C09 contient deux assertions J+30/J+45 à +/-300s. Rejouées une heure plus
    # tard sans reseed, elles sont rouges par construction, pas par régression.
    # Horloge DU TEST UNIQUEMENT calée sur son reçu de reset original, inchangé.
    # Aucune horloge de WP/Woo/C08 ni donnée native n'est modifiée.
    reset = json.loads((ROOT / 'production/C-09/reset.json').read_text(encoding='utf-8'))
    anchor = int(datetime.fromisoformat(reset['at']).timestamp())
    prefix = 'namespace Imagine\\Demo\\C09Tests { function time(): int { return ' + str(anchor) + '; } } namespace { '
    raw = b00.wp('eval', prefix + 'require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php"; }', check=False)
    data = json.loads(raw['stdout'])
    save('tests/b00-c09-horloge-fixture.json', {'fixture_clock_at': reset['at'], 'reason': 'J+30/J+45, sans reset des droits',
         'exit': raw['code'], 'stderr': raw['stderr'], 'result': data})
    checks['c09_natif_horloge_fixture_explicite'] = raw['code'] == 0 and not raw['stderr'] and not data['failures']
    suites['c09-runtime-horloge-fixture'] = data['total']
    c09_native = data
    http_b00 = load('b00-verifier').verify()
    checks['http-b00'] = not http_b00['failures']
    suites['http-b00'] = http_b00['total']
    c08.PROOF = PROOF / 'regression-c08'
    c08.PROOF.mkdir(parents=True, exist_ok=True)
    http_c08 = load('c08-verifier').verify()
    checks['http-c08-etancheite-proprietaire'] = not http_c08['failures']
    suites['http-c08'] = http_c08['total']
    load('c08-regression').run()
    regression = json.loads((c08.PROOF / 'regression.json').read_text(encoding='utf-8'))
    checks['regression-c08-b00'] = not regression['failures']
    suites['regression-c08-b00'] = regression['total']
    c09_http = load('c09-http')
    credentials = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
    before_credentials = json.loads((Path.home() / '.imagine-demo/identifiants-b00-avant-corrections.json').read_text(encoding='utf-8'))
    checks['credentials_b00_enrichis_exacts'] = credentials == before_credentials and len(credentials['c09_accounts']) == 27
    def account_http(entry):
        key, account = entry
        client = c09_http.login(account)
        meta, text = c09_http.fetch(client, c09_http.ARTICLE)
        expected = c09_native['proof'][key]['decision']
        result = {'connexion_et_http200': meta['status'] == 200,
                  'corps_selon_droit_natif': (c09_http.WITNESS in text) == expected['complet'],
                  'bloc_selon_droit_natif': ('data-imagine-bloc=' not in text if expected['bloc'] == 'aucun' else 'data-imagine-bloc="' + expected['bloc'] + '"' in text),
                  'sans_erreur_php': not any(x in text for x in ['Fatal error', 'Warning:', 'critical error'])}
        return key, {'checks': result, 'response': meta}
    accounts = dict(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(account_http, credentials['c09_accounts'].items()))
    flat = {key + ':' + name: ok for key, value in accounts.items() for name, ok in value['checks'].items()}
    save('tests/b00-c09-http.json', {'total': len(flat), 'failures': [k for k,v in flat.items() if not v], 'accounts': accounts})
    suites['http-c09-27-comptes'] = len(flat)
    checks['http_c09_27_connexions'] = len(accounts) == 27 and all(flat.values())
    c10_checks = {}
    for key in ['E-ADMIN', 'E-REDAC', 'E-ABO', 'V-INSCRIT']:
        client = c09_http.login(credentials['c09_accounts'][key])
        meta, text = c09_http.fetch(client, '/wp-admin/admin.php?page=imagine-reglages')
        c10_checks[key + ':autorisation'] = meta['status'] == (200 if key == 'E-ADMIN' else 403)
        if key == 'E-ADMIN':
            for token in ['Journal des modifications', 'À confirmer par Imagine', 'Accès', 'Liste d’envoi']:
                c10_checks['rendu:' + token] = token in text
            c10_checks['huit_champs'] = text.count('class="imagine-reglage"') == 8
    save('tests/b00-c10-http-lecture.json', {'total': len(c10_checks), 'checks': c10_checks, 'failures': [k for k,v in c10_checks.items() if not v]})
    suites['http-c10-lecture'] = len(c10_checks)
    checks['c10_http_lecture_sans_enregistrement'] = all(c10_checks.values())
    original = json.loads((PROOF / 'tests/b00-integre-avant.json').read_text(encoding='utf-8'))
    final = snapshot()
    save('tests/b00-integre-final.json', final)
    checks['c09_comptes_objets_dates_droits_exacts'] = original['c09'] == final['c09']
    checks['c08_c09_ids_plans_exacts'] = original['options'] == final['options']
    checks['c09_decisions_exactes'] = original['decisions'] == final['decisions']
    checks['c10_options_journal_exacts'] = original['c10_settings_and_journal_sha256'] == final['c10_settings_and_journal_sha256']
    checks['c10_bootstrap_actif_preserve'] = final['c10_active'] is True
    checks['sources_c09_c10_closes_exactes'] = original['protected_code'] == final['protected_code']
    checks['recette_ne_modifie_pas_droits_et_options'] = protected == final
    build = json.loads((PROOF / 'b00-reconstruction.json').read_text(encoding='utf-8'))
    idem = next(x['result'] for x in build['steps'] if x['name'] == 'idempotence-interne')
    checks['reconstruction_post_c08_reelle_identique'] = build['status'] == 'VERIFIED_RUNTIME' and idem['identical'] is True
    failures = [key for key, ok in checks.items() if not ok]
    sources = sorted(set([ROOT / 'wp/outils/demo/construire.py', ROOT / 'wp/plugins/imagine-site/Paywall.php',
        *list((ROOT / 'wp/outils/demo').glob('b00*.*')), *list(TESTS.glob('b00*.*')), *list(TESTS.glob('test_b00*.py'))]))
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()}
    tokens = []
    def collect(value, key=''):
        if isinstance(value, dict):
            for k, v in value.items(): collect(v, k)
        elif isinstance(value, str) and 'password' in key and len(value) >= 12:
            tokens.append(value.encode())
    collect(credentials)
    collect(json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8')))
    files = [p for p in [*PROOF.rglob('*'), *sources] if p.is_file() and p.suffix != '.pyc']
    leaked = [p.relative_to(ROOT).as_posix() for p in files if any(t in p.read_bytes() for t in tokens)]
    checks['aucun_secret_dans_livraison'] = not leaked
    failures = [key for key, ok in checks.items() if not ok]
    record = {'scope': b00.SLUG, 'at': datetime.now(timezone.utc).isoformat(), 'status': 'VERIFIED' if not failures else 'FAILED',
              'checks': checks, 'total': len(checks), 'failures': failures, 'suites': suites,
              'suite_assertions': sum(suites.values()), 'c09_counts': final['c09']['counts'],
              'sources_sha256': hashes, 'secret_scan': {'files_checked': len(files), 'matches': leaked},
              'c09_clock_note': 'Horloge du test calée sur reset original ; 2 assertions relatives impossibles en horloge murale tardive, aucun reset ni modification métier.'}
    save('b00-final-verification.json', record)
    print(json.dumps({k: record[k] for k in ['status', 'total', 'failures', 'suites', 'suite_assertions', 'c09_counts', 'secret_scan']}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rejouer', action='store_true')
    run(parser.parse_args().rejouer)
