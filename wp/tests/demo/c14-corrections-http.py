"""Corrections C14 : vrais POST Settings API et GET articles/PDF, objets jetables zéro."""
import json
import re
from html import unescape
from urllib.parse import urlencode
import c14

PREFIX = r'require_once WP_CONTENT_DIR . "/imagine-demo-build/c14-corrections-fixture.php";'
NS = r'Imagine\Demo\C14\Corrections'
OPTION = 'imagine_achat_remboursement'
PAGE = '/wp-admin/options-general.php?page=imagine-achats'


def verify(http, fetch_pdf, client, admin, expected_pdf):
    wp = c14.wp
    checks = {}
    before = wp('echo wp_json_encode(get_option("' + OPTION + '",null));')

    def settings(value, visitor=admin, bad_nonce=False):
        code, _, page = http.fetch(PAGE, visitor)
        nonce = re.search(r'name="_wpnonce" value="([^"]+)"', page)
        fields = {'option_page': 'imagine_achats', 'action': 'update', '_wp_http_referer': PAGE,
                  '_wpnonce': 'incorrect' if bad_nonce or not nonce else unescape(nonce[1]), OPTION: value}
        return http.fetch('/wp-admin/options.php', visitor, urlencode(fields).encode())[0]

    def state():
        return wp('global $wpdb;echo wp_json_encode($wpdb->get_var($wpdb->prepare("SELECT option_value FROM {$wpdb->options} WHERE option_name=%s","' + OPTION + '")));')

    def php(f, code):
        return wp(PREFIX + '$f=json_decode(' + json.dumps(json.dumps(f)) + ',true);' + code)

    def access(f, label, expected):
        for key, allowed in expected.items():
            a = f['articles'][key]
            status, _, body = http.fetch(a['path'], client)
            checks[label + '_' + key + '_article'] = status == 200 and (a['witness'] in body) == allowed
            status, _, data = fetch_pdf(http.BASE, '/?imagine_pdf=' + str(f['issues'][key]), client)
            checks[label + '_' + key + '_PDF'] = (status == 200 and data == expected_pdf) if allowed else (status in (200, 403, 404) and b'%PDF-' not in data)

    try:
        wp('delete_option("' + OPTION + '");echo "true";')
        status, _, page = http.fetch(PAGE, admin)
        checks['reglage_admin_visible_defaut_prudent'] = status == 200 and 'name="' + OPTION + '"' in page and 'À confirmer par Imagine' in page and re.search(r'value="commande"\s+selected=', page) is not None
        checks['POST_defaut_persiste_ligne_native_absente'] = settings('commande') == 200 and state() == 'commande'
        checks['POST_nonce_invalide_refuse'] = settings('ligne', bad_nonce=True) == 403 and state() == 'commande'
        denied = settings('ligne', visitor=client)
        checks['POST_client_sans_capacite_refuse'] = denied in (200, 401, 403) and state() == 'commande'
        checks['POST_valeur_invalide_defaut_ferme'] = settings('invalide') == 200 and state() == 'commande'
        for mode in ['commande', 'ligne']:
            checks['POST_' + mode + '_persiste_relu'] = settings(mode) == 200 and state() == mode
            for kind in ['ventile', 'non_ventile', 'total']:
                f = wp(PREFIX + 'echo wp_json_encode(' + NS + r'\seed());')
                try:
                    access(f, mode + '_' + kind + '_avant', {'a': True, 'b': True})
                    r = php(f, '$r=' + NS + r'\refund($f,' + json.dumps(kind) + ');echo wp_json_encode($r);')
                    f['orders'].append(r['id'])
                    checks[mode + '_' + kind + '_natif_zero'] = r['zero_sans_passerelle'] and r['statut'] == ('refunded' if kind == 'total' else 'processing')
                    expected = {'a': False, 'b': False} if mode == 'commande' or kind == 'total' else {'a': kind != 'ventile', 'b': True}
                    access(f, mode + '_' + kind + '_apres', expected)
                finally:
                    cleaned = php(f, 'echo wp_json_encode(' + NS + r'\cleanup($f));')
                    checks[mode + '_' + kind + '_nettoye_relu'] = all(cleaned.values())
        f = wp(PREFIX + 'echo wp_json_encode(' + NS + r'\seed());')
        try:
            guard_order = NS + r'\owned($f,$f["order"],true);$o=wc_get_order($f["order"]);'
            guard_product = NS + r'\owned($f,$f["products"]["a"]);$p=wc_get_product($f["products"]["a"]);'
            php(f, guard_order + '$o->remove_item($f["items"]["b"]);$o->save();echo "true";')
            access(f, 'instantane_initial', {'a': True, 'b': False})
            php(f, guard_product + '$p->update_meta_data(Imagine\\Site\\AchatsNumeros::PRODUIT,$f["issues"]["b"]);$p->save();echo "true";')
            access(f, 'reaffectation_conserve_sans_retrooctroi', {'a': True, 'b': False})
            php(f, guard_product + '$p->delete_meta_data(Imagine\\Site\\AchatsNumeros::PRODUIT);$p->save();echo "true";')
            access(f, 'mapping_vide_conserve', {'a': True, 'b': False})
            php(f, guard_product + '$p->delete(true);echo wp_json_encode(!get_post($f["products"]["a"]));')
            access(f, 'produit_supprime_conserve', {'a': True, 'b': False})
            guard_issue = NS + r'\owned($f,$f["issues"]["a"]);'
            php(f, guard_issue + 'wp_update_post(["ID"=>$f["issues"]["a"],"post_status"=>"draft"]);echo "true";')
            access(f, 'numero_depublie_ferme', {'a': False, 'b': False})
            php(f, guard_issue + 'wp_update_post(["ID"=>$f["issues"]["a"],"post_status"=>"publish"]);echo "true";')
            access(f, 'numero_republie_retabli', {'a': True, 'b': False})
            php(f, guard_order + '$i=$o->get_item($f["items"]["a"]);$i->delete_meta_data(Imagine\\Site\\AchatsNumeros::LIGNE);$i->save();echo "true";')
            access(f, 'instantane_retire_ferme_pas_de_retrooctroi', {'a': False, 'b': False})
            php(f, guard_order + '$i=$o->get_item($f["items"]["a"]);$i->update_meta_data(Imagine\\Site\\AchatsNumeros::LIGNE,$f["issues"]["a"]);$i->save();echo "true";')
            access(f, 'instantane_retabli_produit_absent', {'a': True, 'b': False})
        finally:
            checks['catalogue_nettoye_relu'] = all(php(f, 'echo wp_json_encode(' + NS + r'\cleanup($f));').values())
    finally:
        wp(('delete_option("' + OPTION + '");' if before is None else 'update_option("' + OPTION + '",' + json.dumps(before) + ');') + 'echo "true";')
        checks['reglage_restaure_exactement'] = wp('echo wp_json_encode(get_option("' + OPTION + '",null));') == before
    return checks
