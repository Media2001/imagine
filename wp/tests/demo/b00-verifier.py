"""Recette HTTP B-00 : réponses publiques, identités stables, login local fictif.
Aucun cookie, mot de passe ou nonce d'administration n'est écrit dans les preuves.
"""
from pathlib import Path
import argparse
import hashlib
import http.cookiejar
import importlib.util
import json
import re
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor, HTTPRedirectHandler, urlopen

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-00'
spec = importlib.util.spec_from_file_location('b00', ROOT / 'wp/outils/demo/construire.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def response(url, opener=None, data=None, follow=True):
    client = opener or build_opener() if follow else build_opener(NoRedirect())
    request = Request(url, data=data, headers={'User-Agent': 'Imagine-B00-recette-fictive/1.0'})
    try:
        result = client.open(request, timeout=45)
    except HTTPError as error:
        result = error
    body = result.read()
    return {'url': url, 'status': result.code, 'final_url': result.url,
            'headers': {key: result.headers.get(key) for key in ('Content-Type', 'Location', 'X-Robots-Tag') if result.headers.get(key)},
            'body_sha256': hashlib.sha256(body).hexdigest(), 'body_bytes': len(body)}, body


def verify():
    proof_dir = PROOF / 'http'
    proof_dir.mkdir(exist_ok=True)
    site = m.request_api('GET', '/api/sites/' + m.SLUG)
    base = site['url'].rstrip('/')
    m.upload('imagine-demo-build/b00-snapshot.php', (ROOT / 'wp/tests/demo/b00-snapshot.php').read_bytes())
    snapshot = json.loads(m.wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-snapshot.php";')['stdout'])
    initial = json.loads((PROOF / 'tests/b00-snapshot-initial.json').read_text(encoding='utf-8'))
    assertions = {'same_ids_slugs_urls_content_and_assets': snapshot == initial,
                  'no_duplicate': snapshot['duplicates'] == [],
                  'complete_independent_inventory': snapshot['total_tagged'] == snapshot['manifest_posts']}
    rows = snapshot['rows']
    main = {
        'accueil': (base + '/', 'DÉMONSTRATION ENTIÈREMENT FICTIVE'),
        'numero': (rows['demo-2026-t1']['url'], 'Sommaire fictif'),
        'article-reserve': (rows['demo-2026-t1-reserve-1']['url'], 'Article fictif réservé'),
        'article-ouvert': (rows['demo-2026-t1-ouvert']['url'], 'CONTENU_FICTIF_OUVERT_DEMO-2026-T1_4'),
        'administration': (base + '/wp-admin/', 'login'),
        'calendrier': (rows['demo-calendrier']['url'], 'DEMO-2028-T4'),
    }
    responses = {}
    for name, (url, expected) in main.items():
        meta, body = response(url, follow=name != 'administration')
        text = body.decode('utf-8', errors='replace')
        if name == 'administration':
            assertions[name + '_http'] = meta['status'] == 302 and '/wp-login.php?' in meta['headers'].get('Location', '')
        else:
            assertions[name + '_http'] = meta['status'] == 200 and expected in text
            # Réponses anonymes seulement ; pas d'HTML d'administration authentifiée.
            (proof_dir / (name + '.html')).write_bytes(body)
            assertions[name + '_sans_fatal'] = 'Fatal error' not in text and 'critical error' not in text
        if name == 'article-reserve':
            assertions['reserved_body_not_sent'] = 'CONTENU_FICTIF_RESERVE_' not in text and 'post_password' in text
        responses[name] = meta
        (proof_dir / (name + '.json')).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    # Tous les objets et tous les médias, pas seulement les cinq adresses du livrable.
    for key, row in rows.items():
        if key.startswith('user:'):
            continue
        url = row.get('file_url') or row['url']
        meta, body = response(url)
        assertions['objet_' + key] = meta['status'] == 200
        responses['objet_' + key] = meta
        if 'reserve-' in key:
            assertions['fermeture_' + key] = b'CONTENU_FICTIF_RESERVE_' not in body
    reserved = rows['demo-2026-t1-reserve-1']['id']
    for name, url in {
        'rest': base + '/wp-json/wp/v2/posts/' + str(reserved),
        'feed': base + '/feed/',
        'recherche': base + '/?s=Imaginaire',
        'oembed': base + '/wp-json/oembed/1.0/embed?' + urlencode({'url': rows['demo-2026-t1-reserve-1']['url']}),
    }.items():
        meta, body = response(url)
        assertions['etancheite_native_' + name] = b'CONTENU_FICTIF_RESERVE_' not in body
        responses['etancheite_' + name] = meta
    credentials = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
    cookies = http.cookiejar.CookieJar()
    client = build_opener(HTTPCookieProcessor(cookies))
    login_meta, login_body = response(base + '/wp-login.php', opener=client)
    assertions['connexion_formulaire'] = login_meta['status'] == 200 and b'user_login' in login_body
    login_data = urlencode({'log': credentials['admin_user'], 'pwd': credentials['admin_password'],
                           'wp-submit': 'Log In', 'redirect_to': base + '/wp-admin/', 'testcookie': '1'}).encode()
    auth_meta, auth_body = response(base + '/wp-login.php', opener=client, data=login_data)
    assertions['admin_authentifie_200'] = auth_meta['status'] == 200 and '/wp-admin/' in auth_meta['final_url'] and b'id="wpadminbar"' in auth_body
    responses['administration-authentifiee'] = auth_meta
    # Test du corps complet via le verrou natif provisoire avec le secret hors dépôt.
    article_client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    response(base + '/wp-login.php?action=postpass', opener=article_client,
             data=urlencode({'post_password': credentials['article_password']}).encode())
    full_meta, full_body = response(rows['demo-2026-t1-reserve-1']['url'], opener=article_client)
    assertions['article_complet_avec_secret_fictif'] = full_meta['status'] == 200 and b'CONTENU_FICTIF_RESERVE_DEMO-2026-T1_1' in full_body
    failures = [key for key, value in assertions.items() if not value]
    result = {'scope': m.SLUG, 'url': base, 'registry_status': site['status'], 'assertions': assertions,
              'total': len(assertions), 'failures': failures, 'responses': responses}
    (PROOF / 'b00-verification-http-idempotence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'url': base, 'registry_status': site['status'], 'total': len(assertions), 'failures': failures}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    verify()
