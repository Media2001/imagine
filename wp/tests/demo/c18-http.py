"""C18 real native HTTP; no bodies, cookies or subscriber data in JSON receipts."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv, importlib.util, io, json, re, sys
from html import unescape
from urllib.parse import urlencode
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c18


def transport():
    spec = importlib.util.spec_from_file_location('c18_http_transport', Path(__file__).with_name('c12-http.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(label='http-final'):
    c18.c17.profils.guard('imagine-test-demo')
    h = transport()
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {p: h.login(accounts[p]) for p in ('E-ABO', 'E-ADMIN', 'E-REDAC', 'A-CARTE')}
    checks = {}
    path = '/wp-admin/admin.php?page=imagine-extractions'
    endpoint = '/wp-admin/admin-post.php'
    status, headers, page = h.fetch(path, clients['E-ABO'])
    checks['page_referent_native'] = status == 200 and '<h1>Extractions</h1>' in page
    if not checks['page_referent_native']:
        c18.save(label, {'checks': checks, 'total': len(checks), 'failures': [k for k,v in checks.items() if v is not True]})
        raise RuntimeError('C18 extraction screen absent')
    before = c18.state()
    journal = lambda: c18.wp(r'echo wp_json_encode(Imagine\Site\ExtractionsAdmin::journal());')
    events_before = journal()
    checks['pas_reglages_referent'] = 'page=imagine-reglages' not in page and 'page=imagine-extractions' in page
    checks['age_et_etiquette_grises'] = all(re.search(r'<option[^>]*value="'+v+r'"[^>]*disabled[^>]*>[^<]*à venir', page) for v in ['age','etiquette'])
    fields = {'action': 'imagine_extraire_abonnes', 'extraction': 'localite', 'pays': 'FR', 'code_postal': ''}
    for p in ('E-REDAC', 'A-CARTE'):
        s, head, text = h.fetch(path, clients[p])
        checks['page_refusee_' + p] = '<h1>Extractions</h1>' not in text
        s, head, _ = h.fetch(endpoint, clients[p], urlencode(dict(fields, _wpnonce='invalide')).encode())
        checks['export_refuse_' + p] = s == 403 and 'text/csv' not in head.get('content-type', '')
    s, head, _ = h.fetch(endpoint, data=urlencode(fields).encode())
    checks['anonyme_refuse'] = s == 403 and 'text/csv' not in head.get('content-type', '')
    for key, value in [('nonce_absent', {}), ('nonce_invalide', {'_wpnonce':'invalide'}), ('nonce_tableau', {'_wpnonce[]':'invalide'})]:
        s, head, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(fields, **value)).encode())
        checks[key] = s == 403 and 'text/csv' not in head.get('content-type', '')
    checks['refus_sans_journal'] = events_before == journal()
    fixture = c18.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["subscriptions"]);')
    c09_ids = {str(v) for v in fixture.values()}
    today = datetime.now(timezone.utc).date()
    cases = [
        ('localite', {'pays':'FR','code_postal':''}, 'A-ETRANGER', 'A-CARTE'),
        ('mode', {'mode_paiement':'bacs'}, 'A-VIR', 'A-PAPIER'),
        ('mode', {'mode_paiement':'imagine_papier'}, 'A-PAPIER', 'A-VIR'),
        ('echeance', {'du':str(today),'au':str(today+timedelta(days=30))}, 'A-ECHEANCE', 'A-EXPIRE'),
        ('etat', {'etat':'En délai de grâce'}, 'A-GRACE', 'A-SUSP'),
        ('etat', {'etat':'Suspendu'}, 'A-SUSP', 'A-GRACE'),
        ('etat', {'etat':'Expiré'}, 'A-EXPIRE', 'A-CARTE'),
        ('etat', {'etat':'Actif'}, 'A-CARTE', 'A-SUSP'),
        ('localite', {'pays':'','code_postal':''}, 'A-SANSMAIL', None),
    ]
    exports = []
    for i, (kind, filters, wanted, excluded) in enumerate(cases):
        prefix = str(i+1) + '_' + kind
        params = dict(extraction=kind, **filters)
        s, _, html = h.fetch(path + '&' + urlencode(params), clients['E-ABO'])
        nonce = re.search(r'name="_wpnonce" value="([^"]+)"', html)
        count = re.search(r'data-imagine-extraction-nombre="(\d+)"', html)
        checks[prefix+'_apercu'] = s == 200 and bool(nonce and count)
        if not nonce or not count:
            continue
        payload = dict(fields, **params, _wpnonce=unescape(nonce.group(1)))
        # Fields from another extraction must not be sent by the real form.
        payload = dict(action=fields['action'], **params, _wpnonce=unescape(nonce.group(1)))
        s, head, body = h.fetch(endpoint, clients['E-ABO'], urlencode(payload).encode())
        csvpath = c18.PROOF / ('extraction-' + prefix + '.csv')
        if s == 200 and head.get('content-type','').startswith('text/csv'):
            csvpath.write_text(body, encoding='utf-8', newline='')
            with csvpath.open(encoding='utf-8', newline='') as stream:
                rows = list(csv.DictReader(stream))
        else:
            rows = []
        checks[prefix+'_CSV_reel_et_nombre'] = s == 200 and head.get('content-type','').startswith('text/csv') and len(rows) == int(count.group(1))
        ids = {r.get('abonnement_id') for r in rows}
        checks[prefix+'_profil_attendu_et_exclusion'] = str(fixture[wanted]) in ids and (excluded is None or str(fixture[excluded]) not in ids)
        if kind == 'localite' and filters['pays'] == 'FR':
            checks[prefix+'_C09_etranger_seul'] = ids & c09_ids == {str(fixture['A-ETRANGER'])}
        if kind == 'mode':
            checks[prefix+'_C09_mode_exact'] = ids & c09_ids == {str(fixture[wanted])} and all(r['mode_paiement'] == filters['mode_paiement'] for r in rows)
        if kind == 'etat':
            checks[prefix+'_etat_exact'] = all(r['etat'] == filters['etat'] for r in rows)
        if kind == 'echeance':
            checks[prefix+'_bornes_exactes'] = all(filters['du'] <= r['echeance_utc'][:10] <= filters['au'] for r in rows)
        if wanted == 'A-SANSMAIL':
            checks['sans_email_technique_absent_du_CSV'] = all(r['email'] == '' for r in rows if r['abonnement_id'] == str(fixture[wanted]))
        checks[prefix+'_flux_prive'] = 'no-store' in head.get('cache-control','') and head.get('x-content-type-options') == 'nosniff' and 'attachment;' in head.get('content-disposition','')
        checks[prefix+'_aucune_colonne_sensible'] = bool(rows) and set(rows[0]) == set(['abonnement_id','compte_id','prenom','nom','email','destinataire','rue','complement','code_postal','ville','pays','formule','mode_paiement','etat','echeance_utc'])
        checks[prefix+'_CSV_formules_protegees'] = all(re.match(r'[\x00-\x20]*[=+@-]', str(cell)) is None for row in rows for cell in row.values())
        event = journal()[0]
        checks[prefix+'_journal_metadata_seules'] = set(event) == {'qui_id','qui_login','quand_utc','extraction','lignes'} and event['qui_login'] == accounts['E-ABO']['login'] and event['extraction'] == kind and event['lignes'] == len(rows)
        exports.append({'case': prefix, 'rows': len(rows), 'csv': csvpath.name})
        if i == 0:
            good_payload = payload
    if 'good_payload' in locals():
        for name, change in [('jeton_lie_filtres', {'pays':'BE'}), ('jeton_lie_extraction', {'extraction':'mode','mode_paiement':'bacs'}), ('age_indisponible', {'extraction':'age'}), ('filtre_tableau', {'pays[]':'FR','pays':None})]:
            bad = dict(good_payload)
            bad.update(change)
            bad = {k:v for k,v in bad.items() if v is not None}
            s, head, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(bad).encode())
            checks[name] = s in (400,403) and 'text/csv' not in head.get('content-type','')
        s, head, _ = h.fetch(endpoint+'?'+urlencode(good_payload), clients['E-ABO'])
        checks['GET_refuse'] = s == 405 and 'text/csv' not in head.get('content-type','')
    s, _, admin = h.fetch(path, clients['E-ADMIN'])
    checks['administrateur_autorise'] = s == 200 and '<h1>Extractions</h1>' in admin
    journal_html = re.search(r'Journal des extractions.*?</table>', admin, re.S)
    checks['journal_affiche_sans_contenu'] = bool(journal_html) and 'Personnage Fictif' not in journal_html.group(0) and '@example.org' not in journal_html.group(0)
    checks['journal_exactement_un_par_export'] = len(journal()) == len(events_before) + len(exports)
    checks['natif_exactement_preserve'] = before == c18.state()
    c18.readback()
    result = {'at': datetime.now(timezone.utc).isoformat(), 'checks': checks, 'total': len(checks), 'failures': [k for k,v in checks.items() if v is not True], 'exports': exports}
    c18.save(label, result)
    print(json.dumps(result, ensure_ascii=False))
    if result['failures']:
        raise RuntimeError('C18 HTTP checks failed: ' + ', '.join(result['failures']))
    return result


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else 'http-final')
