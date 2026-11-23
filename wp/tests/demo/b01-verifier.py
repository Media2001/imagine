"""Recette réelle B-01 sur la cible fixe de B-00, sans reseed."""
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
from construire import request_api, wp, upload, SLUG
from b01_html import validate_html, BeautifulSoup

PROOF = ROOT / 'production/B-01'


def run():
    site = request_api('GET', '/api/sites/' + SLUG)
    if site['slug'] != SLUG or site['status'] != 'running':
        raise RuntimeError('Cible B-01 non autorisée ou arrêtée')
    upload('imagine-demo-build/b01-inventory.php', Path(__file__).with_name('b01-inventory.php').read_bytes())
    runtime = wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b01-inventory.php";', check=False)
    inventory = json.loads(runtime['stdout'])
    inventory['exit_code'] = runtime['code']
    inventory['stderr'] = runtime['stderr']
    (PROOF / 'runtime.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding='utf-8')
    base = inventory['base'].rstrip('/')
    if urlparse(base).netloc != urlparse(site['url']).netloc:
        raise RuntimeError('Adresse publique divergente')
    checks = []
    pages = []
    cases = {}
    def check(name, ok, detail=None):
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})
    def add(key, url, kind, expected=200, data=None):
        cases[url] = {'key': key, 'url': url, 'kind': kind, 'expected': expected, 'data': data}
    add('accueil', base + '/', 'accueil')
    for kind, url in zip(['kiosque', 'agenda', 'partenaires'], inventory['archives']):
        add(kind, url, kind)
    for group, kind in [('issues', 'numero'), ('articles', 'article'), ('themes', 'thematique'), ('events', 'evenement'), ('partners', 'partenaire')]:
        for row in inventory[group]:
            add(kind + '-' + str(row['id']), row['url'], kind, data=row)
    add('page-simple', inventory['page'], 'page')
    add('recherche', base + '/?s=fictif', 'recherche')
    add('recherche-vide', base + '/?s=b01-aucun-resultat-xyz', 'recherche-vide')
    add('404', base + '/b01-page-inexistante-xyz/', '404', 404)
    add('index', base + '/?post_type=post', 'index')
    check('runtime sortie sans erreur', runtime['code'] == 0 and not runtime['stderr'], runtime['stderr'])
    for item in inventory['checks']:
        check('runtime : ' + item['name'], item['ok'])
    html_dir = PROOF / 'http'
    html_dir.mkdir(parents=True, exist_ok=True)
    soups = {}
    for url, case in cases.items():
        if urlparse(url).netloc != urlparse(base).netloc:
            raise RuntimeError('Une URL sort de la cible fictive')
        try:
            response = urlopen(url, timeout=60)
        except HTTPError as error:
            response = error
        raw = response.read()
        text = raw.decode('utf-8')
        soup = BeautifulSoup(text, 'html.parser')
        soups[case['key']] = soup
        file = 'http/' + case['key'] + '.html'
        (PROOF / file).write_bytes(raw)
        errors = validate_html(text)
        key = case['key']
        check(key + ' : HTTP attendu', response.code == case['expected'], response.code)
        check(key + ' : contenu HTML', 'text/html' in response.headers.get('Content-Type', ''))
        check(key + ' : HTML5 et sémantique sans erreur', not errors, errors)
        check(key + ' : aucun diagnostic PHP', not any(x in text for x in ['Fatal error:', 'Warning:', 'Parse error:', 'Notice:', 'Deprecated:']))
        check(key + ' : texte réservé absent anonymement', 'CONTENU_FICTIF_RESERVE_' not in text)
        check(key + ' : CSS du thème chargé', 'imagine-tokens-css' in text and 'imagine-structure-css' in text)
        check(key + ' : pas de police externe du thème', not any(x in text for x in ['fonts.googleapis.com', 'fonts.gstatic.com']))
        row = case['data']
        if row:
            check(key + ' : titre propre au contenu', row['title'] in soup.h1.get_text())
        if case['kind'] == 'article':
            body = soup.select('[data-imagine-body="article"]')
            check(key + ' : point de sortie du corps unique', len(body) == 1)
            check(key + ' : auteur et chapô', row['author'] in text and row['excerpt'] in soup.get_text())
            check(key + ' : lien au numéro', bool(soup.find('a', href=next(i['url'] for i in inventory['issues'] if i['id'] == row['issue']))))
            for term in row['terms']:
                check(key + ' : lien thématique ' + str(term), bool(soup.find('a', href=next(t['url'] for t in inventory['themes'] if t['id'] == term))))
            check(key + ' : corps ouvert complet ou verrou natif réservé',
                  ('post_password' in str(body[0]) and 'CONTENU_FICTIF_RESERVE_' not in str(body[0])) if row['reserved']
                  else 'CONTENU_FICTIF_OUVERT_' in str(body[0]) and 'Scène fictive 5.' in str(body[0]))
        elif case['kind'] == 'numero':
            check(key + ' : couverture avec texte alternatif', bool(soup.select('main .imagine-cover img[alt]')))
            actual = [int(e['data-imagine-id']) for e in soup.select('main li[data-imagine-id]')]
            check(key + ' : sommaire exact du numéro', actual == [a['id'] for a in row['articles']], actual)
            check(key + ' : PDF réel associé', bool(soup.find('a', href=row['pdf'])))
        elif case['kind'] == 'thematique':
            actual = {int(e['data-imagine-id']) for e in soup.select('main li[data-imagine-id]')}
            expected = {a['id'] for a in row['articles']}
            check(key + ' : articles exacts de cette thématique fictive', actual == expected, sorted(actual))
        elif case['kind'] == 'recherche-vide':
            check(key + ' : état vide explicite', 'Aucun contenu pour le moment.' in text)
        pages.append({k: v for k, v in case.items() if k != 'data'} | {
            'http': response.code, 'content_type': response.headers.get('Content-Type'),
            'html_file': file, 'sha256': hashlib.sha256(raw).hexdigest(), 'html_errors': errors,
        })
    kiosk_ids = [int(e['data-imagine-id']) for e in soups['kiosque'].select('main li[data-imagine-id]')]
    check('kiosque : tous les numéros triés par sortie décroissante', kiosk_ids == [x['id'] for x in inventory['issues']], kiosk_ids)
    check('kiosque : hors-série inclus', any(x['type'] == 'hors-serie' and x['id'] in kiosk_ids for x in inventory['issues']))
    home_ids = [int(e['data-imagine-id']) for e in soups['accueil'].select('main li[data-imagine-id]')]
    check('accueil : dernier numéro réel en premier', home_ids[0] == inventory['issues'][0]['id'])
    check('accueil : cinq derniers articles', len(home_ids) == 6)
    for anchor in ['imagine-thematiques', 'imagine-agenda', 'imagine-abonnement']:
        check('accueil : entrée ' + anchor, bool(soups['accueil'].find(id=anchor)))
    for group, key in [('events', 'agenda'), ('partners', 'partenaires')]:
        actual = {int(e['data-imagine-id']) for e in soups[key].select('main li[data-imagine-id]')}
        check(key + ' : liste exacte', actual == {e['id'] for e in inventory[group]})
    resources = []
    for row in inventory['issues']:
        with urlopen(row['pdf'], timeout=30) as response:
            content = response.read()
            ok = response.status == 200 and content.startswith(b'%PDF-')
            check('PDF numéro ' + str(row['id']), ok)
            resources.append({'url': row['pdf'], 'status': response.status, 'sha256': hashlib.sha256(content).hexdigest()})
    for path in ['style.css', 'assets/tokens.css']:
        url = base + '/wp-content/themes/imagine/' + path
        with urlopen(url, timeout=30) as response:
            actual = response.read()
            check('CSS source exacte ' + path, actual == (ROOT / 'wp/themes/imagine' / path).read_bytes())
            resources.append({'url': url, 'status': response.status, 'sha256': hashlib.sha256(actual).hexdigest()})
    failures = [c for c in checks if not c['ok']]
    report = {'at': datetime.now(timezone.utc).isoformat(), 'scope': SLUG,
              'status': 'VERIFIED' if not failures else 'FAILED',
              'validator': 'html5lib 1.1 (algorithme HTML5) + contrôles sémantiques B-01, validation locale, pas certification W3C ou WCAG',
              'http_pages': len(pages), 'http_resources': len(resources), 'assertions': len(checks),
              'passed': len(checks) - len(failures), 'failed': len(failures), 'checks': checks,
              'pages': pages, 'resources': resources}
    (PROOF / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['checks','pages','resources']}, ensure_ascii=False, indent=2))
    for failure in failures:
        print(json.dumps(failure, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
