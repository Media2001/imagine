"""Recette HTTP C11 limitée à imagine-test-demo, sans secrets dans les preuves."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10
from b00_fixtures import fixture_data, dummy_pdf


def fetch(base, path, client=None, headers=None, method='GET'):
    if base != 'http://192.168.129.32:8085' or not path.startswith('/') or path.startswith('//'):
        raise ValueError('Cible hors démonstration')
    try:
        response = (client or build_opener()).open(Request(base + path, headers=headers or {}, method=method), timeout=45)
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
            status, headers, body = fetch(base, path)
            checks[slug + ':' + name] = marker not in body and all(hashlib.sha256(body).digest() != hashlib.sha256(w).digest() and w not in body for w in witnesses)
    spec = importlib.util.spec_from_file_location('c08_http', Path(__file__).with_name('c08-verifier.py'))
    http = importlib.util.module_from_spec(spec); spec.loader.exec_module(http)
    credentials = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    active = http.login(base, credentials['accounts']['actif'])
    issue = fixture_data()['issues'][-1]
    status, headers, body = fetch(base, '/?imagine_pdf=' + str(manifest[issue['slug']]), active)
    checks['abonne:pdf_exact'] = status == 200 and body == dummy_pdf(issue['label'])
    result = {'scope': site['slug'], 'checks': checks, 'passed': sum(checks.values()), 'total': len(checks)}
    out = c10.ROOT / 'production/C-11/http.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    verify()
