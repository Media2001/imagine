"""Recette C08 consolidée et rejouable ; toutes les preuves restent dans production/C-08."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'outils/demo'))
import c08


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (c08.PROOF / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def load(name):
    return json.loads((c08.PROOF / name).read_text(encoding='utf-8'))


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), HERE / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def native(name, flags=()):
    source = HERE / (name + '.php')
    remote = 'imagine-demo-build/' + source.name
    c08.b00.upload(remote, source.read_bytes())
    result = c08.b00.wp('eval', 'require WP_CONTENT_DIR . "/' + remote + '";', *flags, check=False)
    data = json.loads(result['stdout'])
    save(name + '.json', {**result, 'data': data})
    if result['code'] or result['stderr'] or data['failures']:
        raise RuntimeError(name + ' en échec : ' + str(data['failures']))
    return remote, source, data


def run():
    site, _ = c08.guard()
    private_paths = [Path.home()/'.imagine-demo'/n for n in ['identifiants.json', 'c08-identifiants.json']]
    private_before = {str(p): digest(p) for p in private_paths}
    # Le reçu original de pré-correction est conservé ; ne jamais le remplacer pour masquer une régression.
    baseline = load('preservation-before.json')
    checks, counts, deployed = {}, {}, {}
    install = c08.run()
    counts['runtime_php'] = json.loads(install['runtime']['stdout'])['total']
    for name, flags in [('c08-corrections-runtime', ()), ('c08-rights', ()),
                         ('c08-no-woo', ('--skip-plugins', '--skip-themes'))]:
        remote, source, data = native(name, flags)
        deployed[remote] = source
        counts[name] = data['total']
    tests = unittest.defaultTestLoader.discover(str(HERE), pattern='test_*.py')
    tests.addTests(unittest.defaultTestLoader.loadTestsFromModule(module('b01-corrections')))
    transcript = io.StringIO()
    local = unittest.TextTestRunner(stream=transcript, verbosity=2).run(tests)
    local_record = {'total': local.testsRun, 'passed': local.testsRun-len(local.failures)-len(local.errors)-len(local.skipped),
                    'failures': [str(t) for t, _ in local.failures + local.errors], 'skipped': len(local.skipped),
                    'output': transcript.getvalue(), 'python': sys.version,
                    'packages': {n: importlib.metadata.version(n) for n in ['beautifulsoup4','html5lib','six','soupsieve','typing_extensions','webencodings']},
                    'wheels_sha256': {p.name: digest(p) for p in (c08.ROOT/'production/B-01/validation').glob('*.whl')}}
    save('local-tests.json', local_record)
    if not local.wasSuccessful() or local.skipped:
        raise RuntimeError('Tests locaux en échec/ignorés')
    counts['local_tests'] = local.testsRun
    # Sérialiser les mutateurs : pas de sonde HTTP pendant une révocation de plan.
    for name, receipt in [('c08-rest-write','rest-write.json'), ('c08-faults','faults.json'),
                          ('c08-idempotence','idempotence.json')]:
        module(name).run()
        data = load(receipt)
        counts[name] = data['total']
        if data['failures']:
            raise RuntimeError(receipt + ' en échec')
    http = module('c08-verifier')
    http.verify()
    counts['http'] = load('http.json')['total']
    module('c08-regression').run()
    counts['regression'] = load('regression.json')['total']
    after = json.loads(c08.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/b00-integre-snapshot.php";')['stdout'])
    save('preservation-after.json', after)
    for key in ['options', 'c10_settings_and_journal_sha256', 'c10_active', 'protected_code', 'c09', 'decisions']:
        checks['preservation:' + key] = after[key] == baseline[key]
    checks['preservation:c09_cardinalites'] = after['c09']['counts'] == {'users':27,'orders':13,'subscriptions':12,'memberships':14}
    checks['preservation:c08_ids_comptes_objets'] = after['c08']['counts'] == baseline['c08']['counts']
    checks['preservation:c08_articles_meta'] = after['c08']['articles_sha256'] == baseline['c08']['articles_sha256']
    checks['preservation:identifiants_prives_octets'] = all(digest(p) == private_before[str(p)] for p in private_paths)
    # B01 : ni le garde de publication ni ses nouveaux requires ne disparaissent.
    b01_before = json.loads((c08.ROOT/'production/B-01/plugin-installation.json').read_text(encoding='utf-8'))
    checks['preservation:b01_bootstrap_et_garde_octets'] = all(digest(c08.ROOT/'wp/plugins/imagine-site'/name) == value for name,value in b01_before['expected'].items())
    b01_sources = json.loads((c08.ROOT/'production/B-01/b01-final-verification.json').read_text(encoding='utf-8'))['sources_sha256']
    allowed_theme = {'wp/themes/imagine/functions.php', 'wp/themes/imagine/parts/paywall-regularisation.php'}
    checks['preservation:b01_sources_hors_raccord_c08'] = all(digest(c08.ROOT/name) == value for name,value in b01_sources.items() if name not in allowed_theme)
    # Le readback général ci-dessous lie également ces deux sources aux octets actuels.
    bootstrap = (c08.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    checks['preservation:b01_numero_require_register'] = "require_once __DIR__ . '/NumeroPublication.php';" in bootstrap and 'NumeroPublication::register();' in bootstrap
    # L'accueil ne doit garder aucun article temporaire des recettes REST/runtime.
    meta, html = http.fetch(site['url'].rstrip('/'), '/')
    from b01_html import BeautifulSoup
    actual_home = [int(n['data-imagine-id']) for n in BeautifulSoup(html, 'html.parser').select('section[aria-labelledby="imagine-latest-posts"] li[data-imagine-id]')]
    checks['preservation:accueil_ids_ordre_apres_nettoyage'] = meta['status'] == 200 and actual_home == [82,81,45,44,43]
    checks['preservation:aucun_canari_article_restant'] = json.loads(c08.b00.wp('eval',
        'global $wpdb;echo wp_json_encode((int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type=\'post\' AND (post_title LIKE \'Canari éphémère C08%\' OR post_title LIKE \'Canari HTTP éphémère C08%\')")===0);')['stdout']) is True
    # Dernière lecture des OCTETS après tous les rejeux, pas seulement résultat d'upload.
    final_install = load('installation.json')
    for remote in final_install['files_sha256']:
        if remote.startswith('imagine-demo-build/'):
            source = c08.ROOT/('wp/outils/demo/c08-seed.php' if remote.endswith('c08-seed.php') else 'wp/tests/demo/c08-runtime.php')
        else:
            source = c08.ROOT/'wp'/remote
        deployed[remote] = source
    expected = {remote: digest(source) for remote, source in deployed.items()}
    code = '$files=json_decode(' + json.dumps(json.dumps(list(expected))) + ',true);$o=[];foreach($files as $f){$p=WP_CONTENT_DIR."/".$f;token_get_all(file_get_contents($p),TOKEN_PARSE);$o[$f]=hash_file("sha256",$p);}echo wp_json_encode($o);'
    actual = json.loads(c08.b00.wp('eval', code)['stdout'])
    checks['readback_final_php_exact'] = expected == actual
    # Aucune valeur privée dans les preuves actuelles ni les sources du lot.
    sources = [c08.ROOT/'wp/plugins/imagine-site'/n for n in ['Paywall.php','README.md','imagine-site.php','NumeroPublication.php']]
    sources += [c08.ROOT/'wp/themes/imagine/functions.php', *sorted((c08.ROOT/'wp/themes/imagine/parts').glob('paywall-*.php'))]
    sources += sorted(HERE.glob('c08*')) + [HERE/'test_c08_scope.py', c08.ROOT/'wp/outils/demo/c08.py', c08.ROOT/'wp/outils/demo/c08-seed.php']
    source_map = {p.relative_to(c08.ROOT).as_posix(): digest(p) for p in sources if p.is_file()}
    passwords = []
    def secrets(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if 'password' in key and isinstance(value, str): passwords.append(value.encode())
                else: secrets(value)
        elif isinstance(data, list):
            for value in data: secrets(value)
    for p in private_paths: secrets(json.loads(p.read_text(encoding='utf-8')))
    candidates = [p for p in c08.PROOF.rglob('*') if p.is_file() and 'historique' not in p.parts]
    candidates += [c08.ROOT/p for p in source_map]
    leaked = [str(p.relative_to(c08.ROOT)) for p in candidates if any(secret and secret in p.read_bytes() for secret in passwords)]
    checks['aucun_secret_prive_dans_livrables'] = not leaked
    counts['final_checks'] = len(checks)
    failures = [k for k, ok in checks.items() if not ok]
    record = {'at': datetime.now(timezone.utc).isoformat(), 'scope': c08.b00.SLUG,
              'status': 'VERIFIED' if not failures else 'FAILED', 'tests': counts, 'total_checks': sum(counts.values()),
              'failures': failures, 'checks': checks, 'deployed_php_files': len(actual), 'remote_sha256': actual,
              'exact_remote_readback': actual == expected, 'source_files': len(source_map), 'source_sha256': source_map,
              'http_responses': len(load('http.json')['responses']), 'home_ids': actual_home,
              'c09_counts_preserved': after['c09']['counts'], 'c08_fixture_counts': load('idempotence.json')['after']['counts'],
              'closed_library_php_files_verified': load('regression.json')['library_php_files'],
              'no_private_password_in_deliverables': not leaked, 'leak_files': leaked,
              'baseline': 'preservation-before.json', 'c08_full_native_projection_changes':
              [k for k in baseline['c08'] if baseline['c08'][k] != after['c08'][k]]}
    save('verification-finale.json', record)
    print(json.dumps({k:record[k] for k in ['status','tests','total_checks','failures','deployed_php_files','http_responses','home_ids']}, ensure_ascii=False, indent=2))
    if failures: raise SystemExit(1)
    return record


if __name__ == '__main__':
    run()
