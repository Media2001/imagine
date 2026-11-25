"""C15 actual authenticated HTTP, no cookies/nonces/secrets in evidence."""
from pathlib import Path
import csv
from html import unescape
import importlib.util
import io
import json
import re
import sys
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c15


def transport():
    return c15.load_test('c12-http')


def verify():
    c15.profils.guard('imagine-test-demo')
    h = transport()
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {k: h.login(accounts[k]) for k in ('E-ABO', 'E-ADMIN', 'E-REDAC', 'A-CARTE')}
    path = '/wp-admin/admin.php?page=imagine-echeances'
    endpoint = '/wp-admin/admin-post.php'
    checks = {}; pages = {}
    for role in ('E-ABO', 'E-ADMIN'):
        for view in ('echeances', 'attente', 'virements', 'mandats', 'echecs'):
            status, headers, text = h.fetch(path + '&vue=' + view, clients[role])
            pages[role, view] = text
            native = c15.wp('echo wp_json_encode(array_column(Imagine\\Site\\EcheancesNatives::lire(' + json.dumps(view) + ',30),"id"));')
            shown = [int(n) for n in re.findall(r'data-imagine-echeance="(\d+)"', text)]
            checks['vue_native_' + role + '_' + view] = status == 200 and '<h1>Échéances</h1>' in text and shown == native and bool(native)
            checks['prive_sans_IBAN_' + role + '_' + view] = 'no-store' in headers.get('cache-control', '') and re.search(r'\biban\b', text, re.I) is None
        text = pages[role, 'mandats']
        checks['menu_Imagine_unique_' + role] = len(re.findall(r'id="toplevel_page_imagine"', text)) == 1
    checks['referent_sans_reglages'] = 'page=imagine-reglages' not in pages['E-ABO', 'mandats']
    for role in ('E-REDAC', 'A-CARTE'):
        _, _, text = h.fetch(path, clients[role])
        checks['page_refusee_' + role] = '<h1>Échéances</h1>' not in text and 'data-imagine-echeance=' not in text
    fields = {'action': 'imagine_exporter_mandats', 'jours': '30'}
    for role in ('E-REDAC', 'A-CARTE'):
        status, headers, _ = h.fetch(endpoint, clients[role], urlencode(dict(fields, _wpnonce='invalide')).encode())
        checks['export_refuse_' + role] = status == 403 and 'text/csv' not in headers.get('content-type', '')
    status, _, _ = h.fetch(endpoint, data=urlencode(fields).encode())
    checks['export_anonyme_refuse'] = status == 403
    for name, extra in [('absent', {}), ('invalide', {'_wpnonce': 'invalide'}), ('tableau', {'_wpnonce[]': 'invalide'})]:
        status, headers, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(fields, **extra)).encode())
        checks['export_nonce_' + name] = status == 403 and 'text/csv' not in headers.get('content-type', '')
    for role in ('E-ABO', 'E-ADMIN'):
        nonce = re.search(r'name="action" value="imagine_exporter_mandats".*?name="_wpnonce" value="([^"]+)"', pages[role, 'mandats'], re.S)
        checks['formulaire_export_' + role] = nonce is not None
        if nonce:
            payload = dict(fields, _wpnonce=unescape(nonce.group(1)))
            status, headers, text = h.fetch(endpoint, clients[role], urlencode(payload).encode())
            rows = list(csv.reader(io.StringIO(text), delimiter=';'))
            checks['CSV_ouvert_' + role] = status == 200 and len(rows) == 2 and rows[0] == ['Abonné', 'Montant', 'Devise', 'Référence du mandat', 'Échéance (UTC)'] and rows[1][3] == 'A-PAPIER'
            checks['CSV_prive_' + role] = 'private' in headers.get('cache-control', '') and 'no-store' in headers.get('cache-control', '') and headers.get('x-content-type-options') == 'nosniff' and 'attachment;' in headers.get('content-disposition', '')
            checks['CSV_sans_formule_IBAN_' + role] = re.search(r'\biban\b', text, re.I) is None and all(re.match(r'[\x00-\x20]*[=+@-]', cell) is None for row in rows[1:] for cell in row)
            status, _, _ = h.fetch(endpoint + '?' + urlencode(payload), clients[role])
            checks['export_GET_refuse_' + role] = status == 405
            status, _, _ = h.fetch(endpoint, clients[role], urlencode(dict(payload, jours='90')).encode())
            checks['export_nonce_lie_periode_' + role] = status == 403
    c15.save('http', {'scope': 'imagine-test-demo', 'checks': checks, 'total': len(checks), 'failures': [k for k, v in checks.items() if v is not True]})
    print(json.dumps({'total': len(checks), 'failures': [k for k, v in checks.items() if v is not True]}, ensure_ascii=False))
    if not all(v is True for v in checks.values()):
        raise SystemExit(1)
    return checks


if __name__ == '__main__':
    verify()
