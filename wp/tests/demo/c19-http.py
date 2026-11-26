"""C19 real GET/HEAD/refusals, row counts C15/C18, browser menu path."""
from pathlib import Path
from datetime import datetime, timezone
from html import unescape
import importlib.util, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c19


def transport():
    spec = importlib.util.spec_from_file_location('c19_transport', Path(__file__).with_name('c12-http.py'))
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    return h


def numbers(html):
    out = {}
    for key, section in re.findall(r'<section data-imagine-indicateur="([^"]+)">(.*?)</section>', html, re.S):
        out[key] = {unescape(name): int(value) for name, value in re.findall(r'<td data-imagine-mesure="([^"]+)">(\d+)</td>', section)}
    return out


def run(label='http-final', browser=False):
    c19.c18.c17.profils.guard('imagine-test-demo')
    h = transport()
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {p: h.login(accounts[p]) for p in ('E-ABO', 'E-ADMIN', 'E-REDAC', 'A-CARTE')}
    before = c19.state()
    checks = {}
    path = '/wp-admin/admin.php?page=imagine-tableau-de-bord'
    status, headers, page = h.fetch(path, clients['E-ABO'])
    vals = numbers(page)
    checks['referent_ecran_natif'] = status == 200 and '<h1>Tableau de bord</h1>' in page and len(vals) == 4
    if not checks['referent_ecran_natif']:
        c19.save(label, {'checks': checks})
        raise RuntimeError('C19 screen missing or denied')
    content = re.search(r'<div class="wrap" data-imagine-tableau>(.*?)</tbody></table></div>', page, re.S).group(1)
    checks['aucune_donnee_personnelle_dans_ecran'] = all(v not in content for v in ('@', 'Personnage', 'Fictif', 'data-abonnement', 'compte_id', 'Rue '))
    checks['aucun_formulaire_ni_script_ecran'] = '<form' not in content and '<script' not in content
    checks['sept_indicateurs_grises_sans_chiffre'] = len(re.findall('data-imagine-a-venir', content)) == 7 and len(re.findall('— à venir', content)) == 7 and 'color:#646970;background:#f0f0f1' in content
    checks['moyen_paiement_grise_sans_formule'] = 'Par moyen de paiement' in content and 'Distinction mode/moyen à arrêter à l’atelier.' in content
    checks['prive_no_store'] = 'no-store' in headers.get('cache-control', '')
    checks['menu_sans_reglages'] = 'page=imagine-tableau-de-bord' in page and 'page=imagine-reglages' not in page
    for id, section in re.findall(r'<section data-imagine-indicateur="([^"]+)">(.*?)</section>', page, re.S):
        checks['phrase_' + id] = bool(re.search(r'</table><p>[^<]{80,}</p>', section))
    s, _, html = h.fetch('/wp-admin/admin.php?page=imagine-extractions&extraction=etat&etat=Actif', clients['E-ABO'])
    count = re.search(r'data-imagine-extraction-nombre="(\d+)"', html)
    checks['actifs_egal_apercu_C18'] = s == 200 and bool(count) and int(count.group(1)) == vals['actifs']['total']
    # Exact same-filter intersections are checked against native rows by c19-runtime.php.
    for days in ('30', '90', '180'):
        s, _, html = h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue=echeances&jours=' + days, clients['E-ABO'])
        checks['echeances_' + days + '_egal_lignes_HTTP_C15'] = s == 200 and len(re.findall('data-imagine-echeance=', html)) == vals['echeances'][days]
    s, _, html = h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue=echecs&jours=30', clients['E-ABO'])
    checks['echecs_egal_lignes_HTTP_C15'] = s == 200 and len(re.findall('data-imagine-echeance=', html)) == vals['echecs']['total']
    s, _, _ = h.fetch(path, clients['E-ABO'], data=b'action=save&total=9999')
    checks['POST_autorise_refuse_405'] = s == 405
    for profile in ('E-REDAC', 'A-CARTE'):
        s, _, html = h.fetch(path, clients[profile])
        checks['refus_GET_403_' + profile] = s == 403 and not numbers(html)
        s, _, html = h.fetch(path, clients[profile], data=b'action=save')
        checks['refus_POST_403_' + profile] = s == 403 and not numbers(html)
    s, _, html = h.fetch(path)
    checks['anonyme_aucun_nombre'] = not numbers(html) and '<h1>Tableau de bord</h1>' not in html
    s, _, html = h.fetch(path, clients['E-ADMIN'])
    checks['admin_autorise'] = s == 200 and numbers(html) == vals
    s, _, html = h.fetch(path, clients['E-ABO'], method='HEAD')
    checks['HEAD_sans_corps'] = s == 200 and html == ''
    s, _, html = h.fetch(path + '&total=9999&compte_id=1&extraction=age', clients['E-ABO'])
    checks['parametres_sans_effet'] = s == 200 and numbers(html) == vals
    capture = None
    blocked = []
    if browser:
        from playwright.sync_api import sync_playwright
        jar = next(handler.cookiejar for handler in clients['E-ABO'].handlers if hasattr(handler, 'cookiejar'))
        with sync_playwright() as pw:
            chromium = pw.chromium.launch(headless=True)
            try:
                context = chromium.new_context(viewport={'width': 1280, 'height': 1000}, locale='fr-BE')
                def route(r):
                    if r.request.url.startswith(h.BASE + '/'):
                        r.continue_()
                    else:
                        blocked.append(r.request.url.split('?')[0])
                        r.abort()
                context.route('**/*', route)
                context.add_cookies([{'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path, 'secure': c.secure} for c in jar])
                tab = context.new_page()
                tab.goto(h.BASE + '/wp-admin/admin.php?page=imagine-extractions', wait_until='networkidle')
                tab.locator('#adminmenu a[href="admin.php?page=imagine-tableau-de-bord"]').click()
                tab.wait_for_load_state('networkidle')
                checks['navigateur_vrai_menu_Imagine'] = tab.locator('[data-imagine-tableau] h1').inner_text() == 'Tableau de bord'
                checks['navigateur_sept_grises_visibles'] = tab.locator('[data-imagine-a-venir]').count() == 7
                checks['navigateur_quatre_tables_chiffrees'] = tab.locator('[data-imagine-indicateur] table').count() == 4
                capture = 'tableau-de-bord-referent.png'
                tab.screenshot(path=str(c19.PROOF / capture), full_page=True)
                context.close()
            finally:
                chromium.close()
    after = c19.state()
    c19.save(label + '-before', before)
    c19.save(label + '-after', after)
    checks['natif_et_options_inchanges'] = before == after
    if before != after:
        print('State differences:', [k for k in before if before[k] != after[k]])
        for key in ('option_fingerprints', 'native_fingerprints'):
            print(key, [k for k in before[key].keys() | after[key].keys() if before[key].get(k) != after[key].get(k)])
    c19.readback()
    result = {'at': datetime.now(timezone.utc).isoformat(), 'checks': checks, 'total': len(checks),
        'failures': [k for k, v in checks.items() if v is not True], 'valeurs': vals,
        'capture': capture, 'outside_demo_requests_blocked': blocked, 'visual_approval': False, 'fixture_reset': False}
    c19.save(label, result)
    print(json.dumps(result, ensure_ascii=False))
    assert not result['failures'], result['failures']
    return result


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'http-final', '--browser' in sys.argv)
