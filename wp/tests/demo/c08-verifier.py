"""Étanchéité HTTP réelle C08; aucune preuve ne contient cookie, nonce ou mot de passe."""
from pathlib import Path
import hashlib
import http.cookiejar
import json
import re
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c08

WITNESS = 'Les lucioles violettes de C08 gardent le secret du village fictif.'
AUTO_WITNESS = 'Les lanternes argentées de C08 composent un autre récit fictif.'


class Sharing(HTMLParser):
    def __init__(self):
        super().__init__()
        self.descriptions = {}
        self.schema = []
        self.in_schema = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and (a.get('name') in ('description', 'twitter:description') or a.get('property') == 'og:description'):
            self.descriptions[a.get('name') or a.get('property')] = a.get('content', '')
        self.in_schema = tag == 'script' and a.get('type') == 'application/ld+json' or self.in_schema
    def handle_data(self, data):
        if self.in_schema:
            self.schema.append(data)
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_schema = False


def fetch(base, path, client=None, headers=None, data=None):
    if not base.startswith('http://192.168.') or not path.startswith('/') or path.startswith('//'):
        raise ValueError('Cible C08 inattendue')
    client = client or build_opener()
    request = Request(base + path, data=data, headers={'User-Agent': 'Imagine-C08-recette/1.0', **(headers or {})})
    try:
        response = client.open(request, timeout=45)
    except HTTPError as error:
        response = error
    body = response.read()
    return {'status': response.code, 'headers': {k.lower(): v for k, v in response.headers.items()
            if k.lower() in ['cache-control', 'vary', 'etag', 'last-modified', 'content-type']},
            'bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest()}, body.decode('utf-8', errors='replace')


def login(base, account):
    jar = http.cookiejar.CookieJar()
    client = build_opener(HTTPCookieProcessor(jar))
    fetch(base, '/wp-login.php', client)
    meta, body = fetch(base, '/wp-login.php', client, data=urlencode({
        'log': account['login'], 'pwd': account['password'], 'redirect_to': base + '/c08-article-reserve-article/', 'testcookie': '1'}).encode())
    if meta['status'] != 200 or not any(cookie.name.startswith('wordpress_logged_in_') for cookie in jar):
        raise RuntimeError('Connexion fictive C08 non vérifiée.')
    return client


def verify(label='http'):
    site, guard = c08.guard()
    base = site['url'].rstrip('/')
    fixture = json.loads(c08.b00.wp('eval', 'echo wp_json_encode(get_option("imagine_c08_fixture"));')['stdout'])
    aid = str(fixture['article'])
    article = '/c08-article-reserve-article/'
    proof = c08.PROOF / 'http'
    proof.mkdir(parents=True, exist_ok=True)
    checks, responses = {}, {}

    def check_response(name, path, client=None, headers=None, expected=(200,), full=False, save=False):
        meta, text = fetch(base, path, client, headers)
        responses[name] = {'path': path, **meta}
        checks[name + ':status'] = meta['status'] in expected
        checks[name + ':temoin'] = (WITNESS in text) == full
        checks[name + ':autre_temoin_absent'] = AUTO_WITNESS not in text
        checks[name + ':sans_erreur_php'] = not any(x in text for x in ['Fatal error', 'critical error', 'Warning:', 'Uncaught Error'])
        cc = meta['headers'].get('cache-control', '').lower()
        checks[name + ':cache_prive'] = 'private' in cc and 'no-store' in cc and 'no-cache' in cc
        checks[name + ':sans_validateur_partage'] = not any(x in meta['headers'] for x in ['etag', 'last-modified'])
        if save:
            # Sources publiques anonymes seulement, jamais d'HTML authentifié avec nonce.
            (proof / (name + '.html')).write_text(text, encoding='utf-8')
        return text

    text = check_response('anonyme-page', article, save=True)
    checks['anonyme:bloc_connexion'] = 'data-imagine-bloc="connexion"' in text
    checks['anonyme:extrait_public'] = 'Extrait public C08' in text
    share = Sharing(); share.feed(text)
    checks['partage:trois_balises'] = set(share.descriptions) == {'description', 'og:description', 'twitter:description'}
    checks['partage:temoin_absent'] = WITNESS not in json.dumps(share.descriptions) + ''.join(share.schema)
    try:
        schema = json.loads(''.join(share.schema))
        checks['partage:balisage_payant'] = schema['@type'] == 'NewsArticle' and schema['isAccessibleForFree'] is False and schema['hasPart']['cssSelector'] == '.imagine-paywall-body' and 'articleBody' not in schema
    except (ValueError, KeyError, TypeError):
        checks['partage:balisage_payant'] = False
    paths = {
        'rest-item': '/wp-json/wp/v2/posts/' + aid,
        'rest-collection': '/wp-json/wp/v2/posts?' + urlencode({'include': str(fixture['article']) + ',' + str(fixture['automatique']), '_embed': '1'}),
        'rest-champs': '/wp-json/wp/v2/posts/' + aid + '?_fields=content,excerpt',
        'rest-embed': '/wp-json/wp/v2/posts/' + aid + '?context=embed',
        'rest-route-alternative': '/?rest_route=/wp/v2/posts/' + aid,
        'rest-recherche': '/wp-json/wp/v2/search?search=C08',
        'rss2': '/?feed=rss2', 'rss': '/?feed=rss', 'atom': '/?feed=atom', 'rdf': '/?feed=rdf',
        'recherche': '/?s=C08', 'extrait-automatique': '/c08-article-reserve-automatique/',
        'embed-page': article + 'embed/', 'apercu': '/?p=' + aid + '&preview=true',
        'page-multipage': article + '?page=2', 'page-amp-inactif': article + '?amp=1',
    }
    for name, path in paths.items():
        body = check_response(name, path, save=True)
        if name in ['rss2', 'rss', 'atom', 'rdf', 'rest-collection']:
            checks[name + ':fixture_effectivement_presente'] = 'c08-article-reserve-article' in body
        if name == 'recherche':
            checks[name + ':reponse_recherche_valide'] = '<h1' in body and ('data-imagine-id=' in body or 'Aucun contenu pour le moment.' in body)
        if name == 'extrait-automatique':
            checks[name + ':repli_neutre'] = 'Cet article est réservé aux abonnés.' in body
    oembed = '/wp-json/oembed/1.0/embed?' + urlencode({'url': base + article})
    check_response('oembed', oembed, expected=(200, 401, 404), save=True)
    check_response('rest-contexte-edition-interdit', '/wp-json/wp/v2/posts/' + aid + '?context=edit', expected=(401, 403))
    check_response('rest-revisions-interdites', '/wp-json/wp/v2/posts/' + aid + '/revisions', expected=(401, 403))
    check_response('faux-googlebot', article, headers={'User-Agent': 'Googlebot/2.1', 'X-Forwarded-For': '66.249.66.1', 'X-Real-IP': '66.249.66.1'}, save=True)
    check_response('faux-bingbot', article, headers={'User-Agent': 'bingbot/2.0'}, save=True)
    # Des validateurs arbitraires ne doivent jamais provoquer un 304 réutilisable.
    check_response('conditionnelle-anonyme', article, headers={'If-None-Match': '"c08"', 'If-Modified-Since': 'Tue, 01 Jan 2030 00:00:00 GMT'})
    check_response('conditionnelle-flux', '/?feed=rss2', headers={'If-Modified-Since': 'Tue, 01 Jan 2030 00:00:00 GMT'})
    def check_search(name, term, expected_id, client=None, nonce=None):
        for route, path in {
            'html': '/?' + urlencode({'s': term}),
            'rest-posts': '/wp-json/wp/v2/posts?' + urlencode({'search': term, 'per_page': 100}),
            'rest-search': '/wp-json/wp/v2/search?' + urlencode({'search': term, 'per_page': 100}),
        }.items():
            meta, body = fetch(base, path, client, {'X-WP-Nonce': nonce} if nonce else {})
            key = name + ':' + route
            responses[key] = {'path': path, **meta}
            checks[key + ':200'] = meta['status'] == 200
            ids = ([int(x) for x in re.findall(r'data-imagine-id="(\d+)"', body)]
                   if route == 'html' else [row['id'] for row in json.loads(body)])
            checks[key + ':appariement_exact'] = (int(aid) in ids) == expected_id
            checks[key + ':cache_prive'] = all(x in meta['headers'].get('cache-control', '') for x in ['private', 'no-store'])
            # Le formulaire/titre HTML réaffiche légitimement la recherche saisie.
            # C'est l'ID et les cartes de résultat, pas cette réflexion, qui font oracle.
            if route != 'html' and not expected_id:
                checks[key + ':sans_fragment_corps'] = WITNESS not in body

    checks['fixture:aucun_password_natif'] = json.loads(c08.b00.wp('eval',
        'echo wp_json_encode(get_post(' + aid + ')->post_password === "");')['stdout']) is True
    check_search('anonyme-phrase-temoin', '"' + WITNESS + '"', False)
    check_search('anonyme-titre-public', '"Article réservé fictif article"', True)
    check_search('anonyme-extrait-public', '"Extrait public C08"', True)
    check_search('anonyme-mots-corps', 'lucioles violettes', False)
    credentials = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    for key in ['actif', 'grace', 'sans-droit']:
        client = login(base, credentials['accounts'][key])
        text = check_response(key + '-page', article, client, full=key != 'sans-droit')
        checks[key + ':bloc'] = ('data-imagine-bloc="regularisation"' in text if key == 'grace' else
                                'data-imagine-bloc="abonnement"' in text if key == 'sans-droit' else 'data-imagine-bloc=' not in text)
        # Readback natif d'un nonce REST lié à la vraie session; aucune valeur conservée.
        nonce_meta, nonce = fetch(base, '/wp-admin/admin-ajax.php?action=rest-nonce', client)
        checks[key + ':nonce_natif'] = nonce_meta['status'] == 200 and len(nonce.strip()) == 10
        check_search(key + '-phrase-temoin', '"' + WITNESS + '"', key != 'sans-droit', client, nonce.strip())
        check_response(key + '-rest', '/wp-json/wp/v2/posts/' + aid, client, headers={'X-WP-Nonce': nonce.strip()}, full=key != 'sans-droit')
        check_response('anonyme-apres-' + key, article)
    # Un cookie natif B00 de mot de passe n'accorde plus le droit C08.
    base_credentials = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
    password_client = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    fetch(base, '/wp-login.php?action=postpass', password_client, data=urlencode({'post_password': base_credentials['article_password']}).encode())
    check_response('cookie-mot-de-passe-non-droit', article, password_client)
    # Contrôle positif : pas une panne qui masquerait tous les articles.
    check_response('article-ouvert', '/demo-2026-t1-ouvert/')
    checks['article_ouvert:complet'] = 'CONTENU_FICTIF_OUVERT_DEMO-2026-T1_4' in fetch(base, '/demo-2026-t1-ouvert/')[1]
    failures = [name for name, ok in checks.items() if not ok]
    record = {'scope': c08.b00.SLUG, 'url': base, 'total': len(checks), 'passed': len(checks)-len(failures),
              'failed': len(failures), 'failures': failures, 'checks': checks, 'responses': responses}
    (c08.PROOF / (label + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: record[k] for k in ['scope', 'total', 'passed', 'failed', 'failures']}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return record


if __name__ == '__main__':
    verify(sys.argv[1] if len(sys.argv) > 1 else 'http')
