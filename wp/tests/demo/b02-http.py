"""B02 : vrais cookies, parcours natifs, adresse postale modifiée puis restaurée."""
from pathlib import Path
from html import unescape
import json
import re
import sys
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b02
import c14


def verify(allow_address_edit=False):
    c14.c10.guard()
    http = c14.module('b02_transport', 'c12-http.py')
    binary = c14.module('b02_pdf', 'c11-verifier.py').fetch
    wp = b02.wp
    f = wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    base = wp('echo wp_json_encode(parse_url(wc_get_page_permalink("myaccount"),PHP_URL_PATH));')
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    checks = {}
    clients = {}
    for key in ['A-CARTE', 'A-SEPA4', 'A-SUSP', 'P-NUMERO']:
        client = http.login(accounts[key])
        clients[key] = client
        status, headers, body = http.fetch(base, client)
        checks[key + '_dashboard_HTTP'] = status == 200 and 'data-imagine-mon-compte' in body
        checks[key + '_cache_prive'] = all(v in headers.get('cache-control', '') for v in ['private', 'no-store'])
        for section in ['abonnement', 'echeances', 'numeros', 'coordonnees', 'factures']:
            checks[key + '_section_' + section] = 'id="imagine-compte-' + section + '"' in body
        if key in f['subscriptions']:
            sid = f['subscriptions'][key]
            checks[key + '_souscription_propre_HTTP'] = 'data-imagine-abonnement="' + str(sid) + '"' in body
        if key == 'A-SEPA4':
            table = re.search(r'<table data-imagine-echeancier=.*?</table>', body, re.S)
            checks['4x_quatre_lignes_HTTP'] = bool(table) and table.group(0).count('<th scope="row">') == 4
            checks['4x_deux_payees_deux_a_venir_dates_non_raccordees_HTTP'] = 'Date non raccordée' in body and body.count('>Payée<') == 2 and body.count('>À venir<') == 2
        if key == 'A-SUSP':
            checks['suspendu_bandeau_HTTP'] = 'data-imagine-regularisation' in body and 'Suspendu' in body
            checks['suspendu_echeance_echouee_fictive_HTTP'] = 'Échéance échouée' in body
            checks['suspendu_sans_PDF_HTTP'] = '?imagine_pdf=' not in body
        if key in ['A-CARTE', 'P-NUMERO']:
            links = re.findall(r'href="([^"]*imagine_pdf=[0-9]+)"', body)
            checks[key + '_PDF_lien_present'] = bool(links)
            if links:
                path = '/' + unescape(links[0]).split(http.BASE + '/', 1)[-1]
                code, _, data = binary(http.BASE, path, client)
                checks[key + '_PDF_protege_octets_HTTP'] = code == 200 and data.startswith(b'%PDF-')
    own, other = f['subscriptions']['A-CARTE'], f['subscriptions']['A-SUSP']
    client = clients['A-CARTE']
    for name, path in [
        ('query_ids', base + '?subscription=' + str(other) + '&user_id=' + str(f['users']['A-SUSP']) + '&customer_id=' + str(f['users']['A-SUSP'])),
        ('view_subscription', base + 'view-subscription/' + str(other) + '/'),
        ('edit_address', base + 'edit-address/shipping/?subscription=' + str(other)),
        ('view_order', base + 'view-order/' + str(f['orders']['A-SUSP']) + '/')]:
        status, _, body = http.fetch(path, client)
        checks['isolation_' + name + '_sans_donnees_autre'] = status in (200, 403, 404) and 'data-imagine-abonnement="' + str(other) + '"' not in body and 'A-SUSP' not in body
        if name == 'edit_address':
            checks['isolation_adresse_pas_formulaire_autre'] = 'value="' + str(other) + '" id="update_subscription_address"' not in body
    code, _, body = http.fetch(base)
    checks['anonyme_pas_compte_HTTP'] = code == 200 and 'data-imagine-mon-compte' not in body and 'A-CARTE' not in body
    checks['profil_reception_A_SEPA4_natif'] = bool(wp('echo wp_json_encode((bool)get_user_by("login","a-sepa4"));'))
    _, _, home = http.fetch('/')
    nav = re.search(r'data-imagine-nav="compte".*?</li>', home, re.S)
    checks['navigation_compte_natif'] = bool(nav) and base in nav.group(0)
    sid = own
    guard = '$s=wcs_get_subscription(' + str(sid) + ');if(!$s||(int)$s->get_customer_id()!==' + str(f['users']['A-CARTE']) + '){throw new RuntimeException("Cible B02 refusée");}'
    before = wp(guard + 'echo wp_json_encode(["shipping"=>$s->get_address("shipping"),"modified"=>$s->get_date_modified()?->getTimestamp(),"customer"=>(new WC_Customer($s->get_customer_id()))->get_shipping(),"observations"=>count(Imagine\\Site\\EnvoiNatif::releves((string)$s->get_id()))]);')
    foreign_before = wp('$s=wcs_get_subscription(' + str(other) + ');echo wp_json_encode([$s->get_address("shipping"),$s->get_date_modified()?->getTimestamp()]);')
    def edit(address, target=sid, bad_nonce=False):
        path = base + 'edit-address/shipping/?subscription=' + str(sid)
        status, _, body = http.fetch(path, client)
        fields = {'shipping_' + k: v for k, v in address.items()}
        for name in ['woocommerce-edit-address-nonce', '_wcsnonce']:
            match = re.search(r'name="' + name + r'" value="([^"]+)"', body)
            if not match:
                raise RuntimeError('Nonce adresse native absent : ' + name)
            fields[name] = 'invalide' if bad_nonce else unescape(match.group(1))
        fields.update({'action': 'edit_address', 'save_address': '1', 'update_subscription_address': str(target)})
        return http.fetch(base + 'edit-address/shipping/?subscription=' + str(target), client, urlencode(fields).encode())
    if not allow_address_edit:
        # Corrections B02 : conserver les POST d'isolation, aucune édition positive ni restauration SQL.
        edit(before['shipping'], bad_nonce=True)
        checks['POST_nonce_invalide_sans_ecriture'] = wp(guard + 'echo wp_json_encode($s->get_shipping_address_1());') == before['shipping']['address_1']
        edit(before['shipping'], target=other)
        checks['POST_ID_autre_sans_mutation_autre'] = wp('$s=wcs_get_subscription(' + str(other) + ');echo wp_json_encode([$s->get_address("shipping"),$s->get_date_modified()?->getTimestamp()]);') == foreign_before
        after = wp(guard + 'echo wp_json_encode(["shipping"=>$s->get_address("shipping"),"modified"=>$s->get_date_modified()?->getTimestamp(),"customer"=>(new WC_Customer($s->get_customer_id()))->get_shipping(),"observations"=>count(Imagine\\Site\\EnvoiNatif::releves((string)$s->get_id()))]);')
        checks['adresse_client_et_journal_sans_mutation'] = before == after
        failures = [k for k, value in checks.items() if value is not True]
        (b02.PROOF / 'http.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
        print('B02 HTTP sans édition positive :', len(checks) - len(failures), '/', len(checks), '; échecs :', failures, flush=True)
        return checks
    changed = dict(before['shipping'], address_1='2 rue Imaginaire B02')
    try:
        edit(changed, bad_nonce=True)
        checks['POST_nonce_invalide_sans_ecriture'] = wp(guard + 'echo wp_json_encode($s->get_shipping_address_1());') == before['shipping']['address_1']
        edit(before['shipping'], target=other)
        checks['POST_ID_autre_sans_mutation_autre'] = wp('$s=wcs_get_subscription(' + str(other) + ');echo wp_json_encode([$s->get_address("shipping"),$s->get_date_modified()?->getTimestamp()]);') == foreign_before
        status, _, _ = edit(changed)
        after = wp(guard + '$r=Imagine\\Site\\EnvoiNatif::releves((string)$s->get_id());echo wp_json_encode(["shipping"=>$s->get_shipping_address_1(),"postal"=>$r[array_key_last($r)]["donnees"]["rue"],"customer"=>(new WC_Customer($s->get_customer_id()))->get_shipping_address_1()]);')
        checks['POST_natif_adresse_modifiee_et_relue'] = status == 200 and after['shipping'] == changed['address_1']
        checks['POST_adresse_source_postale_et_client_coherente'] = after['postal'] == after['customer'] == changed['address_1']
        code, _, body = http.fetch(base, client)
        checks['POST_adresse_affichee_HTTP'] = code == 200 and changed['address_1'] in body
    finally:
        edit(before['shipping'])
        # Le natif a modifié date_modified, pas le contrat. Restaurer seulement ce témoin.
        wp(guard + '$s->set_date_modified(' + str(before['modified']) + ');$s->save();echo wp_json_encode($s->get_date_modified()->getTimestamp());')
        after = wp(guard + 'echo wp_json_encode(["shipping"=>$s->get_address("shipping"),"modified"=>$s->get_date_modified()?->getTimestamp(),"customer"=>(new WC_Customer($s->get_customer_id()))->get_shipping(),"observations"=>count(Imagine\\Site\\EnvoiNatif::releves((string)$s->get_id()))]);')
        checks['adresse_native_et_client_restaurees_exactement'] = all(after[k] == before[k] for k in ['shipping', 'modified', 'customer'])
        checks['deux_observations_postales_append_only'] = after['observations'] == before['observations'] + 2
    failures = [k for k, value in checks.items() if value is not True]
    (b02.PROOF / 'http.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
    print('B02 HTTP :', len(checks) - len(failures), '/', len(checks), '; échecs :', failures, flush=True)
    return checks


if __name__ == '__main__':
    checks = verify()
    raise SystemExit(0 if all(checks.values()) else 1)
