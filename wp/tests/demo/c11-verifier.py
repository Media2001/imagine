"""Recette HTTP C11 limitée à imagine-test-demo, sans secrets dans les preuves."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class LocalRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).netloc != '192.168.129.32:8085':
            raise ValueError('Redirection hors démonstration refusée')
        return super().redirect_request(req, fp, code, msg, headers, newurl)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10
from b00_fixtures import fixture_data, dummy_pdf


def fetch(base, path, client=None, headers=None, method='GET'):
    if base != 'http://192.168.129.32:8085' or not path.startswith('/') or path.startswith('//'):
        raise ValueError('Cible hors démonstration')
    client = client or build_opener(LocalRedirect())
    if not any(isinstance(h, LocalRedirect) for h in client.handlers):
        client.add_handler(LocalRedirect())
    try:
        response = client.open(Request(base + path, headers=headers or {}, method=method), timeout=45)
    except HTTPError as error:
        response = error
    return response.code, {k.lower(): v for k, v in response.headers.items()}, response.read()


def verify():
    site, _ = c10.guard()
    base = site['url'].rstrip('/')
    manifest = json.loads(c10.b00.wp('eval', 'echo wp_json_encode(get_option("imagine_demo_manifest"));')['stdout'])
    checks = {}
    witnesses = [dummy_pdf(issue['label']) for issue in fixture_data()['issues']]
    marker = b'IMAGINE - DEMONSTRATION FICTIVE'
    names = json.loads(c10.b00.wp('eval', 'echo wp_json_encode(array_map(static fn($id)=>get_post_meta($id,"_imagine_pdf_blob",true),get_posts(["post_type"=>"imagine_numero","numberposts"=>-1,"fields"=>"ids"])));')['stdout'])
    responses = {}

    def probe(name, path, client=None, headers=None, method='GET', statuses=(200, 401, 403, 404), pdf=None):
        status, hs, body = fetch(base, path, client, headers, method)
        responses[name] = {'status': status, 'bytes': len(body)}
        absent = marker not in body and all(w not in body and hashlib.sha256(body).digest() != hashlib.sha256(w).digest() for w in witnesses)
        checks[name] = status in statuses and (absent if pdf is None else body == pdf)
        checks[name] = checks[name] and not any(x in body for x in [b'Fatal error', b'Warning:', b'Uncaught Error', b'critical error'])
        checks[name] = checks[name] and all(not n or n.encode() not in body for n in names)
        checks[name] = checks[name] and b'/var/www/imagine-private-pdf' not in body
        return status, hs, body

    for issue in fixture_data()['issues']:
        slug = issue['slug']
        aid = manifest[slug + '-pdf']
        paths = {
            'ancien-direct': '/wp-content/uploads/imagine-demo/' + slug + '.pdf',
            'ancien-source': '/wp-content/imagine-demo-build/assets/' + slug + '.pdf',
            'media-rest': '/wp-json/wp/v2/media/' + str(aid),
            'attachment': '/?attachment_id=' + str(aid),
            'media-slug': '/' + slug + '-pdf/',
            'numero': '/numeros/' + slug + '/',
            'endpoint-anonyme': '/?imagine_pdf=' + str(manifest[slug]),
        }
        for name, path in paths.items():
            status, headers, body = probe(slug + ':' + name, path)
            if name in ('endpoint-anonyme', 'numero'):
                checks[slug + ':' + name + ':sans-lien-pdf'] = b'Ouvrir le PDF factice du num' not in body
            if name == 'endpoint-anonyme':
                checks[slug + ':bloc-connexion'] = status == 200 and b'data-imagine-pdf-bloc="connexion"' in body
    for name, path in {
        'liste-uploads': '/wp-content/uploads/imagine-demo/',
        'liste-sources': '/wp-content/imagine-demo-build/assets/',
        'medias': '/wp-json/wp/v2/media?media_type=application&per_page=100',
        'medias-inclusion': '/wp-json/wp/v2/media?include=' + ','.join(str(manifest[i['slug'] + '-pdf']) for i in fixture_data()['issues']),
        'rest-route': '/?rest_route=/wp/v2/media/' + str(manifest['demo-2026-t4-pdf']),
        'rest-recherche': '/wp-json/wp/v2/search?search=PDF',
        'recherche': '/?s=PDF',
        'sitemap': '/wp-sitemap.xml',
        'sitemap-numeros': '/wp-sitemap-posts-imagine_numero-1.xml',
        'sitemap-attachment': '/wp-sitemap-posts-attachment-1.xml',
        'prive-direct': '/imagine-private-pdf/site-1/' + next(n for n in names if n),
    }.items():
        status, hs, body = probe(name, path)
        if name.startswith('liste-'):
            checks[name + ':sans-fichier-pdf'] = b'.pdf' not in body
    spec = importlib.util.spec_from_file_location('c08_http', Path(__file__).with_name('c08-verifier.py'))
    http = importlib.util.module_from_spec(spec); spec.loader.exec_module(http)
    credentials = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    active = http.login(base, credentials['accounts']['actif'])
    for issue in fixture_data()['issues']:
        status, hs, body = probe(issue['slug'] + ':abonne-page-numero', '/numeros/' + issue['slug'] + '/', active)
        checks[issue['slug'] + ':abonne-lien-pdf'] = b'Ouvrir le PDF factice du num' in body
        probe(issue['slug'] + ':abonne-pdf-exact', '/?imagine_pdf=' + str(manifest[issue['slug']]), active, statuses=(200,), pdf=dummy_pdf(issue['label']))
    endpoint = '/?imagine_pdf=' + str(manifest['demo-2026-t4'])
    status, headers, body = probe('abonne-conditionnel', endpoint, active,
        {'If-None-Match': '"c11"', 'If-Modified-Since': 'Tue, 01 Jan 2030 00:00:00 GMT'}, statuses=(200,), pdf=dummy_pdf(fixture_data()['issues'][-1]['label']))
    checks['cache-prive-no-store'] = all(x in headers.get('cache-control', '') for x in ['private', 'no-store'])
    checks['sans-validateurs'] = not any(x in headers for x in ['etag', 'last-modified'])
    checks['pdf-type'] = headers.get('content-type') == 'application/pdf'
    checks['pdf-disposition'] = headers.get('content-disposition', '').startswith('attachment;')
    status, hs, body = probe('abonne-head', endpoint, active, method='HEAD', statuses=(200,))
    checks['head-sans-octets'] = body == b'' and hs.get('content-type') == 'application/pdf'
    status, hs, body = probe('anonyme-apres-abonne', endpoint, statuses=(200,))
    checks['anonyme-apres:bloc'] = b'data-imagine-pdf-bloc="connexion"' in body
    checks['anonyme-apres:cache'] = all(x in hs.get('cache-control', '') for x in ['private', 'no-store'])
    probe('faux-robot', endpoint, headers={'User-Agent': 'Googlebot', 'X-Forwarded-For': '66.249.66.1'}, statuses=(200,))
    without = http.login(base, credentials['accounts']['sans-droit'])
    status, hs, body = probe('connecte-sans-droit', endpoint, without, statuses=(200,))
    checks['sans-droit:bloc'] = b'data-imagine-pdf-bloc="abonnement"' in body
    probe('identifiant-invalide', '/?imagine_pdf[]=39', statuses=(404,))
    probe('identifiant-inconnu', '/?imagine_pdf=999999999', statuses=(404,))
    probe('methode-refusee', endpoint, active, method='POST', statuses=(405,))
    result = {'scope': site['slug'], 'checks': checks, 'responses': responses, 'passed': sum(checks.values()), 'total': len(checks)}
    out = c10.ROOT / 'production/C-11/http.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('HTTP C11 :', result['passed'], '/', result['total'], '; échecs :', [k for k, v in checks.items() if not v])
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    verify()
