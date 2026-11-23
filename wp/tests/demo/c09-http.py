"""C09 : connexions réelles des 27 comptes et vérification HTML sans cookies enregistrés."""
from pathlib import Path
import concurrent.futures
import hashlib
import http.cookiejar
import json
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPCookieProcessor
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import profils

BASE = 'http://192.168.129.32:8085'
ARTICLE = '/c08-article-reserve-article/'
WITNESS = 'Les lucioles violettes de C08 gardent le secret du village fictif.'


class OnlyDemoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != 'http' or urlsplit(newurl).netloc != '192.168.129.32:8085':
            raise ValueError('Redirection hors imagine-test-demo refusée')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(client, path, data=None, ua='Imagine-C09-recette/1.0'):
    if not path.startswith('/') or path.startswith('//'):
        raise ValueError('Chemin HTTP C09 refusé')
    try:
        response = client.open(Request(BASE + path, data=data, headers={'User-Agent': ua}), timeout=45)
    except HTTPError as error:
        response = error
    content = response.read()
    return {'status': response.code, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
            'cache': response.headers.get('Cache-Control', '')}, content.decode('utf-8', 'replace')


def login(account):
    jar = http.cookiejar.CookieJar()
    client = build_opener(OnlyDemoRedirect(), HTTPCookieProcessor(jar))
    fetch(client, '/wp-login.php')
    meta, _ = fetch(client, '/wp-login.php', urlencode({'log': account['login'], 'pwd': account['password'],
        'redirect_to': BASE + ARTICLE, 'testcookie': '1'}).encode())
    if meta['status'] != 200 or not any(c.name.startswith('wordpress_logged_in_') for c in jar):
        raise RuntimeError('Échec de connexion du compte fictif ' + account['login'])
    return client


def run():
    profils.guard('imagine-test-demo')
    root = profils.b00.ROOT
    native = json.loads((root / 'production/C-09/reset.json').read_text(encoding='utf-8'))['native']['proof']
    credentials = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    c08 = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))['accounts']
    jobs = []
    for row in profils.catalogue():
        if row['code'] == 'V-ROBOT':
            continue
        jobs.append((row['code'], credentials.get(row['code']), native[row['code']]['decision']))
    for code, account in c08.items():
        jobs.append(('C08-' + code, account, {'complet': code != 'sans-droit', 'bloc': 'regularisation' if code == 'grace' else 'aucun' if code == 'actif' else 'abonnement'}))

    def verify(job):
        key, account, decision = job
        client = login(account) if account else build_opener(OnlyDemoRedirect())
        meta, text = fetch(client, ARTICLE, ua='Googlebot/2.1' if key == 'V-FAUX' else 'Imagine-C09-recette/1.0')
        checks = {'http200': meta['status'] == 200, 'connexion_native': True,
                  'temoin_selon_decision': (WITNESS in text) == decision['complet'],
                  'sans_erreur_php': not any(x in text for x in ['Fatal error', 'Warning:', 'critical error']),
                  'cache_prive': 'private' in meta['cache'] and 'no-store' in meta['cache']}
        if decision['bloc'] != 'aucun':
            checks['bloc_nomme'] = 'data-imagine-bloc="' + decision['bloc'] + '"' in text
        else:
            checks['bloc_absent'] = 'data-imagine-bloc=' not in text
        return key, {'checks': checks, 'response': meta, 'full': decision['complet']}

    evidence = dict(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(verify, jobs))
    checks = {key + ':' + check: ok for key, proof in evidence.items() for check, ok in proof['checks'].items()}
    result = {'scope': 'imagine-test-demo', 'accounts_c09': len(credentials), 'scenarios_c09': len(jobs)-3,
              'accounts_c08': len(c08), 'total': len(checks), 'failures': [k for k,v in checks.items() if not v], 'evidence': evidence}
    (root / 'production/C-09/http.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'evidence'}, ensure_ascii=False))
    if result['failures']:
        raise RuntimeError('Recette HTTP C09 échouée')
    return result


if __name__ == '__main__':
    run()
