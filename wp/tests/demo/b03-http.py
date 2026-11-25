"""B03 HTTP, lecture seule : ni fixture, ni compte, ni droit modifié."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / 'production/B-03'
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c08


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(phase='final'):
    site, _ = c08.guard()
    if site['url'].rstrip('/') != 'http://192.168.129.32:8085':
        raise RuntimeError('Origine B03 refusée')
    http = module('b03_http_transport', 'c12-http.py')
    from b01_html import BeautifulSoup, validate_html
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    client = http.login(accounts['A-CARTE'])
    article = '/c08-article-reserve-article/'
    witness = 'Les lucioles violettes de C08 gardent le secret du village fictif.'
    checks, responses = {}, {}
    for label, visitor, full in [('a-carte', client, True), ('anonyme', None, False)]:
        code, headers, text = http.fetch(article, visitor)
        soup = BeautifulSoup(text, 'html.parser')
        body = soup.select_one('.imagine-paywall-body')
        checks[label + ':HTTP200'] = code == 200
        checks[label + ':texte_selon_droit'] = (witness in text) == full
        checks[label + ':extrait_present'] = bool(soup.select_one('.imagine-chapo'))
        checks[label + ':bloc_paywall'] = full or bool(soup.select_one('[data-imagine-bloc]'))
        checks[label + ':cache_prive'] = 'private' in headers.get('cache-control', '') and 'no-store' in headers.get('cache-control', '')
        checks[label + ':HTML5_semantique'] = not validate_html(text)
        toggle = soup.select_one('button#imagine-reading-toggle')
        checks[label + ':vrai_bouton_lecture'] = bool(toggle and toggle.get('type') == 'button' and toggle.get_text(strip=True) == "Lire l’article")
        tools = soup.select_one('#imagine-reading-tools')
        checks[label + ':sans_JS_bouton_invisible'] = bool(tools and tools.has_attr('hidden'))
        checks[label + ':etat_accessible'] = bool(toggle and toggle.get('aria-pressed') == 'false' and toggle.get('aria-controls') == 'imagine-reading-options')
        checks[label + ':corps_unique'] = len(soup.select('[data-imagine-body="article"]')) == 1 and len(soup.select('.imagine-paywall-body')) == 1
        checks[label + ':temps_calcule_serveur'] = bool(soup.select_one('[data-imagine-reading-time]'))
        checks[label + ':trois_fonds_et_tailles'] = len(soup.select('#imagine-reading-theme option')) == 3 and len(soup.select('#imagine-reading-size option')) == 3
        checks[label + ':barre_progression_nommee'] = bool(soup.select_one('progress#imagine-reading-progress[aria-label][max="100"]'))
        checks[label + ':script_dedie'] = len(soup.select('script[src*="/assets/reading.js"]')) == 1
        checks[label + ':style_dedie'] = len(soup.select('link[href*="/assets/reading.css"]')) == 1
        checks[label + ':sans_erreur_PHP'] = not any(s in text for s in ['Fatal error', 'Warning:', 'critical error'])
        responses[label] = {'status': code, 'bytes': len(text.encode()), 'body_sha256': hashlib.sha256(str(body).encode()).hexdigest(), 'article': article}
    # Les données de la page sont incluses dans le contrôle de la sentinelle ci-dessus.
    for label, path in [('REST', '/wp-json/wp/v2/posts?slug=c08-article-reserve-article'), ('flux', '/feed/'), ('recherche', '/?s=lucioles')]:
        code, _, text = http.fetch(path)
        checks[label + ':anonyme_sans_texte_reserve'] = code == 200 and witness not in text
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'phase': phase, 'checks': checks,
               'total': len(checks), 'failures': [k for k,v in checks.items() if not v], 'responses': responses}
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / ('http-' + phase + '.json')).write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ['phase', 'total', 'failures']}, ensure_ascii=False))
    if receipt['failures']:
        raise SystemExit(1)
    return receipt


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'final')
