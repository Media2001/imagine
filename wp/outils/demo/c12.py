"""C12, cible fictive unique ; aucun constructeur global, aucune preuve hors C12."""
import argparse
import base64
import importlib.util
import io
import json
import runpy
import sys
import unittest
from pathlib import Path
import c10

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/Decouverte.php', 'plugins/imagine-site/DecouverteReglages.php',
         'plugins/imagine-site/Paywall.php']  # Bootstrap C13 conservé, jamais réinstallé ici.


def upload(rel, source):
    data = source.read_bytes()
    c10.b00.upload(rel, data)
    code = '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo base64_encode(file_get_contents($p));'
    if c10.b00.wp('eval', code)['stdout'].strip() != base64.b64encode(data).decode():
        raise RuntimeError('Readback différent : ' + rel)


def runtime():
    upload('imagine-demo-build/c12-runtime.php', ROOT / 'wp/tests/demo/c12-runtime.php')
    result = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c12-runtime.php";', check=False)
    checks = json.loads(result['stdout'])
    print('C12 PHP :', sum(v is True for v in checks.values()), '/', len(checks), '; échecs :', [k for k, v in checks.items() if v is not True])
    if result['code'] or result['stderr'] or not all(v is True for v in checks.values()):
        raise SystemExit(1)
    return checks


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'wp/tests/demo' / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def regression(http):
    # Réutiliser la recette PHP C11 sans appeler son runner, qui écrit hors de C12.
    upload('imagine-demo-build/c11-runtime.php', ROOT / 'wp/tests/demo/c11-runtime.php')
    r = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c11-runtime.php";', check=False)
    checks = json.loads(r['stdout'])
    if r['stderr'] or r['code']:
        raise RuntimeError('Non-régression PHP C11 échouée')
    fetch = module('c11_http_transport', 'c11-verifier.py').fetch
    from b00_fixtures import fixture_data, dummy_pdf
    m = http.wp('echo wp_json_encode(get_option("imagine_demo_manifest"));')
    accounts = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))['accounts']
    client = http.login(accounts['actif'])
    path = '/?imagine_pdf=' + str(m['demo-2026-t4'])
    status, headers, body = fetch(http.BASE, path, client)
    expected = dummy_pdf(next(i['label'] for i in fixture_data()['issues'] if i['slug'] == 'demo-2026-t4'))
    checks['HTTP_pdf_abonne_octets_exacts'] = status == 200 and body == expected and 'no-store' in headers.get('cache-control', '')
    status, _, body = fetch(http.BASE, path)
    checks['HTTP_pdf_anonyme_ferme_apres_abonne'] = status == 200 and b'%PDF-' not in body and b'data-imagine-pdf-bloc="connexion"' in body
    status, _, body = fetch(http.BASE, '/wp-content/uploads/imagine-demo/demo-2026-t4.pdf')
    checks['HTTP_ancienne_URL_pdf_toujours_fermee'] = status in (403, 404) and b'%PDF-' not in body
    status, _, body = fetch(http.BASE, '/wp-json/wp/v2/media/' + str(m['demo-2026-t4-pdf']))
    checks['HTTP_REST_media_pdf_toujours_ferme'] = status in (401, 403, 404) and b'%PDF-' not in body
    print('C11 ciblé :', sum(v is True for v in checks.values()), '/', len(checks))
    if not all(v is True for v in checks.values()):
        raise RuntimeError('Non-régression C11 : ' + str([k for k, v in checks.items() if v is not True]))
    return checks


def run(tests_only=False, check_only=False):
    phpunit = runpy.run_path(str(ROOT / 'wp/outils/demo/c12-unit.py'))['run']()
    _, manifest = c10.guard()  # Identité read-only AVANT toute écriture cible.
    if not tests_only and not check_only:
        for rel in FILES:
            upload(rel, ROOT / 'wp' / rel)
        for name in ['c12-seed.php', 'c12-profils.php', 'c09-seed.php', 'c09-profils.json']:
            upload('imagine-demo-build/' + name, ROOT / 'wp/outils/demo' / name)
        c10.b00.wp('eval', '(static function(){require WP_CONTENT_DIR . "/imagine-demo-build/c12-seed.php";})();')
        c10.b00.wp('eval', 'require_once WP_CONTENT_DIR . "/imagine-demo-build/c12-profils.php";$f=get_option("imagine_c09_fixture");foreach(["V-DEC","V-DEC-FIN"] as $k){Imagine\\Demo\\C12\\profil($f["users"][$k],$k);}echo "ok";')
        result = json.loads(c10.b00.wp('eval', '$f=get_option("imagine_c09_fixture");$out=[];foreach(["V-DEC","V-DEC-FIN"] as $k){$id=$f["users"][$k];$out[$k]=["verified"=>get_user_meta($id,"imagine_email_confirme",true)==="1","state"=>Imagine\\Site\\Decouverte::etat($id)];}echo wp_json_encode($out);')['stdout'])
        if not all(row['verified'] for row in result.values()) or result['V-DEC-FIN']['state'] is None:
            raise RuntimeError('Profils C12 non relus')
    for rel in FILES:
        actual = c10.b00.wp('eval', 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . ' + json.dumps('/' + rel) + '));')['stdout'].strip()
        if actual != base64.b64encode((ROOT / 'wp' / rel).read_bytes()).decode():
            raise RuntimeError('Code cible différent : ' + rel)
    results = {'PHPUnit_C12': phpunit, 'PHP_C12': runtime()}
    if tests_only:
        return results
    http = module('c12_http', 'c12-http.py')
    results['HTTP_C12'] = http.verify()
    results['C11_cible'] = regression(http)
    sys.path[:0] = [str(p) for p in (ROOT / 'production/B-01/validation').glob('*.whl')]
    transcript = io.StringIO()
    local = unittest.TextTestRunner(stream=transcript, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(ROOT / 'wp/tests/demo'), pattern='test_*.py'))
    print('Unitaires locaux :', local.testsRun, '; succès :', local.wasSuccessful())
    if not local.wasSuccessful():
        print(transcript.getvalue())
        raise RuntimeError('Régression unitaire locale')
    results['unitaires'] = {'total': local.testsRun, 'succes': local.wasSuccessful()}
    results['manifestes_preserves'] = manifest == c10.guard()[1]
    if results['manifestes_preserves'] is not True:
        raise RuntimeError('Manifeste C08/B00 différent')
    results['total_controles'] = sum(len(v) for k, v in results.items() if k in ['PHP_C12', 'HTTP_C12', 'C11_cible']) + local.testsRun + phpunit['tests']
    results['statut'] = 'VERT'
    out = ROOT / 'production/C-12/resultats.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print('C12 VERT :', results['total_controles'], 'contrôles/tests ; résultats :', out)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-only', action='store_true', help='Recette PHP C12 seule (diagnostic)')
    parser.add_argument('--check-only', action='store_true', help='Rejeu complet, sans réinstaller ni réinitialiser les profils')
    args = parser.parse_args()
    run(args.tests_only, args.check_only)

