"""Recette C13 HTTP réelle ; aucune donnée de session dans le résultat."""
from pathlib import Path
import csv
import importlib.util
import io
import json
import re
import sys
from html import unescape
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c13


def helper():
    p = Path(__file__).with_name('c12-http.py')
    spec = importlib.util.spec_from_file_location('c13_http_transport', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify():
    c13.c10.guard()
    h = helper()
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {k: h.login(accounts[k]) for k in ('E-ABO', 'E-ADMIN', 'E-REDAC', 'A-CARTE')}
    page_path = '/wp-admin/admin.php?page=imagine-liste-envoi&numero=DEMO-2027-T1'
    endpoint = '/wp-admin/admin-post.php'
    checks = {}
    pages = {}
    for k in ('E-ABO', 'E-ADMIN'):
        status, headers, text = h.fetch(page_path, clients[k])
        pages[k] = text
        checks['page_native_' + k] = status == 200 and '<h1>Liste d’envoi</h1>' in text and 'DEMO-2027-T1' in text and '2027-01-05' in text
    checks['menu_referent_sans_reglages'] = 'page=imagine-liste-envoi' in pages['E-ABO'] and 'page=imagine-reglages' not in pages['E-ABO']
    fields = {'action': 'imagine_exporter_liste_envoi', 'numero': 'DEMO-2027-T1'}
    before = h.wp(r'echo wp_json_encode(Imagine\Site\ListeEnvoiAdmin::journal());') if 'Liste d’envoi' in pages.get('E-ABO', '') else []
    for k in ('E-REDAC', 'A-CARTE'):
        status, headers, text = h.fetch(page_path, clients[k])
        checks['page_interdite_' + k] = 'name="action" value="imagine_exporter_liste_envoi"' not in text and 'text/csv' not in headers.get('content-type', '')
        status, headers, text = h.fetch(endpoint, clients[k], urlencode(dict(fields, _wpnonce='invalide')).encode())
        checks['export_interdit_' + k] = status == 403 and 'text/csv' not in headers.get('content-type', '')
    status, headers, _ = h.fetch(endpoint, data=urlencode(dict(fields, _wpnonce='invalide')).encode())
    checks['export_anonyme_ferme'] = status == 403 and 'text/csv' not in headers.get('content-type', '')
    for missing in (True, False):
        status, headers, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(fields if missing else dict(fields, _wpnonce='invalide')).encode())
        checks['nonce_absent' if missing else 'nonce_invalide'] = status == 403 and 'text/csv' not in headers.get('content-type', '')
    if not all(checks.values()):
        print(json.dumps({'HTTP': checks}, ensure_ascii=False))
        raise RuntimeError('Échec C13 HTTP avant exports')
    for profile in ('E-ABO', 'E-ADMIN'):
        nonce = re.search(r'name="_wpnonce" value="([^"]+)"', pages[profile])
        if not nonce:
            raise RuntimeError('Nonce export natif absent')
        payload = dict(fields, _wpnonce=unescape(nonce.group(1)))
        status, headers, body = h.fetch(endpoint, clients[profile], urlencode(payload).encode())
        rows = list(csv.reader(io.StringIO(body)))
        expected = h.wp(r'echo wp_json_encode((new Imagine\Pilotage\Envoi\AdministrationFormatExport())->lire()->colonnes);')
        view = h.wp(r'$v=Imagine\Site\EnvoiNatif::apercu("DEMO-2027-T1");echo wp_json_encode(["nombre"=>count($v["liste"]->lignes),"belgique"=>$v["belgique"],"etranger"=>$v["etranger"]]);')
        checks['CSV_reel_' + profile] = status == 200 and headers.get('content-type', '').startswith('text/csv') and rows[0] == expected and len(rows)-1 == view['nombre']
        checks['CSV_prive_' + profile] = 'no-store' in headers.get('cache-control', '') and headers.get('x-content-type-options') == 'nosniff' and 'attachment;' in headers.get('content-disposition', '')
        events = h.wp(r'echo wp_json_encode(Imagine\Site\ListeEnvoiAdmin::journal());')
        event = events[0]
        checks['journal_export_' + profile] = event['qui_login'] == accounts[profile]['login'] and event['numero'] == fields['numero'] and event['lignes'] == len(rows)-1 and bool(event['quand_utc'])
    checks['refus_sans_journal_export'] = len(h.wp(r'echo wp_json_encode(Imagine\Site\ListeEnvoiAdmin::journal());')) == len(before) + 2 if len(before) < 48 else True
    print(json.dumps({'HTTP': checks}, ensure_ascii=False))
    if not all(v is True for v in checks.values()):
        raise RuntimeError('Échec C13 HTTP')
    return checks


if __name__ == '__main__':
    verify()
