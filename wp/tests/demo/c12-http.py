"""C12 : vrai HTTP, secrets uniquement en mémoire ; résultats sans corps ni cookies."""
from pathlib import Path
import concurrent.futures
import http.cookiejar
import json
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPCookieProcessor
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c12

BASE = 'http://192.168.129.32:8085'


class DemoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != 'http' or urlsplit(newurl).netloc != '192.168.129.32:8085':
            raise ValueError('Redirection hors démonstration')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(path, client=None, data=None, headers=None, method=None):
    if not path.startswith('/') or path.startswith('//'):
        raise ValueError('Chemin C12 refusé')
    client = client or build_opener(DemoRedirect())
    try:
        r = client.open(Request(BASE + path, data=data, headers={'User-Agent': 'Imagine-C12/1.0', **(headers or {})}, method=method), timeout=45)
    except HTTPError as e:
        r = e
    return r.code, dict((k.lower(), v) for k, v in r.headers.items()), r.read().decode('utf-8', 'replace')


def login(account):
    jar = http.cookiejar.CookieJar()
    client = build_opener(DemoRedirect(), HTTPCookieProcessor(jar))
    fetch('/wp-login.php', client)
    fetch('/wp-login.php', client, urlencode({'log': account['login'], 'pwd': account['password'],
        'redirect_to': BASE + '/mon-compte/', 'testcookie': '1'}).encode())
    if not any(c.name.startswith('wordpress_logged_in_') for c in jar):
        raise RuntimeError('Connexion native C12 échouée')
    return client


def wp(code):
    r = c12.c10.b00.wp('eval', code)
    if r['stderr']:
        raise RuntimeError('Avertissement PHP dans la recette C12')
    return json.loads(r['stdout'])


def settings_post(admin, desired, nonce_override=None, relecture='fermee'):
    from html import unescape
    _, _, page = fetch('/wp-admin/admin.php?page=imagine-reglages', admin)
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"', page)
    if not nonce:
        raise RuntimeError('Nonce Settings API absent')
    fields = {'option_page': 'imagine_reglages', 'action': 'update',
              '_wpnonce': nonce_override or unescape(nonce.group(1)),
              '_wp_http_referer': '/wp-admin/admin.php?page=imagine-reglages'}
    values = wp(r'$s=new Imagine\Pilotage\Administration\Reglages();$v=[];foreach($s->defauts() as $k=>$d){$v[$k]=get_option($k,$d);}echo wp_json_encode($v);')
    for option, value in values.items():
        if isinstance(value, dict):
            fields.update({option + '[' + k + ']': v for k, v in value.items()})
        else:
            fields[option] = '\n'.join(value)
    fields.update({'imagine_decouverte_reglages[' + k + ']': (','.join(v) if isinstance(v, list) else v) for k, v in desired.items()})
    fields['imagine_decouverte_relecture'] = relecture
    return fetch('/wp-admin/options.php', admin, urlencode(fields).encode())


def verify():
    c12.c10.guard()
    ids = wp('echo wp_json_encode(get_option("imagine_c12_fixture"));')
    user = wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["V-DEC"]);')
    key = 'imagine_decouverte_compte_' + str(user)
    before = wp('$id=' + str(user) + ';echo wp_json_encode(["etat"=>get_option("' + key + '",null),"policy"=>get_option("imagine_decouverte_reglages",null),"relecture"=>get_option("imagine_decouverte_relecture",null),"verifie"=>get_user_meta($id,"imagine_email_confirme",true)]);')
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    checks = {}
    c10_before = wp('$out=[];foreach(["imagine_acces_reglages","imagine_c05_reglages","imagine_envoi_colonnes_export"] as $k){$out[$k]=get_option($k,null);}echo wp_json_encode($out);')
    try:
        wp('delete_option("' + key + '");update_user_meta(' + str(user) + ',"imagine_email_confirme","1");update_option("imagine_decouverte_reglages",["ouverture"=>"fermee","forme"=>"articles","jours"=>7,"nombre"=>2,"numeros"=>[]]);echo "true";')
        client = login(accounts['V-DEC'])
        _, _, closed = fetch('/c12-decouverte-un/', client)
        checks['defaut_HTTP_ferme_sans_ouverture'] = 'Le texte réservé C12 un révèle' not in closed and wp('echo wp_json_encode(get_option("' + key + '",null));') is None
        admin = login(accounts['E-ADMIN'])
        issues = wp('$m=get_option("imagine_demo_manifest");echo wp_json_encode(array_map(static fn($s)=>(string)$m[$s],["demo-2026-t4","demo-2026-t3","demo-2026-t2"]));')
        desired = {'ouverture': 'premiere_lecture', 'forme': 'articles', 'jours': 7, 'nombre': 2, 'numeros': issues}
        status, _, settings_html = settings_post(admin, desired)
        checks['activation_POST_natif_C10'] = status == 200 and wp('echo wp_json_encode(get_option("imagine_decouverte_reglages"));') == desired
        checks['reglage_relecture_defaut_ferme_POST'] = wp('echo wp_json_encode(get_option("imagine_decouverte_relecture"));') == 'fermee'
        editorial = wp('$out=[];foreach(get_option("imagine_c12_fixture") as $label=>$id){$out[$label]=["numero"=>(string)get_post_meta($id,"imagine_numero_id",true),"designe"=>get_post_meta($id,"imagine_decouverte",true)==="1"];}echo wp_json_encode($out);')
        checks['un_designe_par_numero_existant'] = [editorial[k]['numero'] for k in ['un', 'deux', 'trois']] == issues and all(editorial[k]['designe'] for k in ['un', 'deux', 'trois']) and editorial['non-designe'] == {'numero': issues[0], 'designe': False}
        status, _, text = fetch('/c12-decouverte-non-designe/', client)
        checks['non_designe_meme_numero_sans_ouverture_HTTP'] = status == 200 and 'Le texte réservé C12 non-designe révèle' not in text and wp('echo wp_json_encode(get_option("' + key + '",null));') is None
        # Clé absente et faux natif sont deux états distincts ; ne muter que notre témoin.
        non_id = ids['non-designe']
        marker_before = wp('echo wp_json_encode(get_post_meta(' + str(non_id) + ',"imagine_decouverte",false));')
        try:
            wp('$id=' + str(non_id) + ';if(get_post_meta($id,"_imagine_c12_fixture",true)!=="non-designe"){throw new RuntimeException("Proprietaire C12 refuse");}delete_post_meta($id,"imagine_decouverte");echo "true";')
            status, _, text = fetch('/c12-decouverte-non-designe/', client)
            checks['designation_absente_HTTP_fermee_sans_etat'] = status == 200 and 'Le texte réservé C12 non-designe révèle' not in text and wp('echo wp_json_encode(get_option("' + key + '",null));') is None
        finally:
            wp('$id=' + str(non_id) + ';if(get_post_meta($id,"_imagine_c12_fixture",true)!=="non-designe"){throw new RuntimeException("Proprietaire C12 refuse");}delete_post_meta($id,"imagine_decouverte");foreach(json_decode(' + json.dumps(json.dumps(marker_before)) + ',true) as $v){add_post_meta($id,"imagine_decouverte",$v);}echo "true";')
            checks['designation_native_restauree_exactement'] = wp('echo wp_json_encode(get_post_meta(' + str(non_id) + ',"imagine_decouverte",false));') == marker_before
        audit = wp('global $wpdb;$rows=$wpdb->get_col("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE \'imagine_reglages_journal_%\'");$out=[];foreach($rows as $row){$event=maybe_unserialize($row);if($event["option"]==="imagine_decouverte_reglages"){$out[]=$event;}}echo wp_json_encode($out);')
        checks['journal_visible_compte_admin'] = any(e['qui_login'] == 'e-admin' and e['apres'] == desired for e in audit)
        bad = dict(desired, nombre=0)
        settings_post(admin, bad)
        checks['reglage_invalide_conserve'] = wp('echo wp_json_encode(get_option("imagine_decouverte_reglages"));') == desired
        status, _, _ = settings_post(admin, dict(desired, nombre=3), nonce_override='nonce-invalide')
        checks['nonce_invalide_refuse'] = status == 403 and wp('echo wp_json_encode(get_option("imagine_decouverte_reglages"));') == desired
        status, _, denied = fetch('/wp-admin/options.php', client, urlencode({'option_page': 'imagine_reglages', 'action': 'update', '_wpnonce': 'nonce-invalide'}).encode())
        # WooCommerce écarte le rôle customer vers Mon compte avant options.php.
        checks['client_ne_modifie_pas_C10'] = (status == 403 or (status == 200 and 'woocommerce-MyAccount' in denied and 'name="option_page"' not in denied)) and wp('echo wp_json_encode(get_option("imagine_decouverte_reglages"));') == desired
        fin_user = wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["V-DEC-FIN"]);')
        fin_before = wp('echo wp_json_encode(get_option("imagine_decouverte_compte_' + str(fin_user) + '"));')
        fin = login(accounts['V-DEC-FIN'])
        status, _, text = fetch('/c12-decouverte-trois/', fin)
        checks['profil_V_DEC_FIN_epuise_HTTP'] = status == 200 and 'data-imagine-bloc="decouverte_epuisee"' in text and 'Le texte réservé C12 trois révèle' not in text and wp('echo wp_json_encode(get_option("imagine_decouverte_compte_' + str(fin_user) + '"));') == fin_before
        nonce_status, _, nonce = fetch('/wp-admin/admin-ajax.php?action=rest-nonce', client)
        auth_status, _, me = fetch('/wp-json/wp/v2/users/me', client, headers={'X-WP-Nonce': nonce.strip()})
        checks['rest_vraiment_connecte'] = nonce_status == 200 and auth_status == 200 and json.loads(me)['id'] == user
        excluded = [
            ('rest', '/wp-json/wp/v2/posts/' + str(ids['un']), {'X-WP-Nonce': nonce.strip()}, 'GET'),
            ('rest_route', '/?rest_route=/wp/v2/posts/' + str(ids['un']), {'X-WP-Nonce': nonce.strip()}, 'GET'),
            ('flux', '/?feed=rss2&p=' + str(ids['un']), {}, 'GET'),
            ('apercu', '/?p=' + str(ids['un']) + '&preview=true', {}, 'GET'),
            ('embed', '/c12-decouverte-un/embed/', {}, 'GET'),
            ('oembed', '/wp-json/oembed/1.0/embed?' + urlencode({'url': BASE + '/c12-decouverte-un/'}), {}, 'GET'),
            ('recherche', '/?' + urlencode({'s': 'comètes turquoise'}), {}, 'GET'),
            ('google', '/c12-decouverte-un/', {'User-Agent': 'Googlebot/2.1'}, 'GET'),
            ('bing', '/c12-decouverte-un/', {'User-Agent': 'bingbot/2.0'}, 'GET'),
            ('head', '/c12-decouverte-un/', {}, 'HEAD'),
            ('prefetch', '/c12-decouverte-un/', {'Sec-Purpose': 'prefetch'}, 'GET'),
            ('post', '/c12-decouverte-un/', {}, 'POST'),
        ]
        witness = 'Le texte réservé C12 un révèle des comètes turquoise entièrement fictives.'
        for name, route, hs, method in excluded:
            for public, visitor in [('connecte', client), ('anonyme', None)]:
                status, headers, text = fetch(route, visitor, headers=hs, method=method)
                checks[name + '_' + public + '_sans_fuite'] = status in (200, 400, 401, 403, 404, 405) and witness not in text and 'Fatal error' not in text
            checks[name + '_sans_ouverture_ni_consommation'] = wp('echo wp_json_encode(get_option("' + key + '",null));') is None
        admin = login(accounts['E-ADMIN'])
        status, _, settings_html = fetch('/wp-admin/admin.php?page=imagine-reglages', admin)
        checks['champs_dans_section_acces_C10'] = status == 200 and all('name="imagine_decouverte_reglages[' + field + ']"' in settings_html for field in ['ouverture', 'forme', 'jours', 'nombre', 'numeros']) and 'À confirmer par Imagine' in settings_html
        checks['relecture_question_ouverte_visible_C10'] = 'name="imagine_decouverte_relecture"' in settings_html and 'Se refermer (défaut prudent)' in settings_html and 'Rester lisible' in settings_html and 'pas une contrainte du moteur C06' in settings_html
        path = '/c12-decouverte-un/'
        witness = 'Le texte réservé C12 un révèle des comètes turquoise entièrement fictives.'
        status, headers, body = fetch(path)
        checks['anonyme_extrait_connexion'] = status == 200 and witness not in body and 'data-imagine-bloc="connexion"' in body
        status, headers, body = fetch(path, client)
        checks['connecte_premiere_lecture_complete'] = status == 200 and witness in body
        checks['cache_prive'] = all(x in headers.get('cache-control', '') for x in ['private', 'no-store'])
        state = wp('echo wp_json_encode(get_option("' + key + '",null));')
        checks['decompte_compte_persistant'] = isinstance(state, dict) and state['articles'] == [ids['un']]
        checks['compteur_visible'] = 'data-imagine-decouverte="1/2"' in body
        status, _, text = fetch('/c12-decouverte-non-designe/', client)
        checks['non_designe_meme_numero_sans_credit_HTTP'] = status == 200 and 'Le texte réservé C12 non-designe révèle' not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == state
        again = login(accounts['V-DEC'])
        for _ in range(3):
            status, _, body = fetch(path, again)
        checks['sessions_cookies_boucle_sans_recredit'] = status == 200 and witness in body and wp('echo wp_json_encode(get_option("' + key + '"));') == state
        for name, route, hs, method in excluded:
            status, _, text = fetch(route, client, headers=hs, method=method)
            checks[name + '_apres_lecture_pas_de_credit'] = witness not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == state
        status, _, text = fetch('/c12-decouverte-deux/', again)
        checks['dernier_credit_HTTP_livre'] = status == 200 and 'Le texte réservé C12 deux révèle' in text and 'data-imagine-decouverte="2/2"' in text
        status, _, text = fetch('/c12-decouverte-trois/', again)
        exhausted_state = wp('echo wp_json_encode(get_option("' + key + '"));')
        checks['epuisement_HTTP_bloc'] = status == 200 and 'Le texte réservé C12 trois révèle' not in text and 'data-imagine-bloc="decouverte_epuisee"' in text and exhausted_state['articles'] == [ids['un'], ids['deux']]
        _, _, text = fetch(path, again)
        checks['relecture_apres_quota_defaut_fermee_HTTP'] = witness not in text and 'data-imagine-bloc="decouverte_epuisee"' in text and wp('echo wp_json_encode(get_option("' + key + '"));') == exhausted_state
        settings_post(admin, desired, relecture='rester_lisible')
        _, _, text = fetch(path, again)
        checks['relecture_apres_quota_rester_lisible_HTTP'] = witness in text and 'data-imagine-decouverte="2/2"' in text and wp('echo wp_json_encode(get_option("' + key + '"));') == exhausted_state
        _, _, text = fetch('/c12-decouverte-trois/', again)
        checks['relecture_lisible_aucun_nouveau_droit_HTTP'] = 'Le texte réservé C12 trois révèle' not in text and 'data-imagine-bloc="decouverte_epuisee"' in text and wp('echo wp_json_encode(get_option("' + key + '"));') == exhausted_state
        settings_post(admin, desired, relecture='fermee')
        fresh_session = login(accounts['V-DEC'])
        for _ in range(3):
            status, _, text = fetch('/c12-decouverte-trois/', fresh_session)
        checks['epuise_nouvelle_session_et_boucle'] = 'Le texte réservé C12 trois révèle' not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == exhausted_state
        status, _, text = fetch(path)
        checks['cookies_vides_restent_anonymes'] = witness not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == exhausted_state
        # Deux URL distinctes concurrentes disputent le dernier crédit (état de test seulement).
        wp('$s=get_option("' + key + '");$s["articles"]=[' + str(ids['un']) + '];update_option("' + key + '",$s);echo "true";')
        jobs = ['deux', 'trois'] * 3
        def concurrent_read(label):
            _, _, text = fetch('/c12-decouverte-' + label + '/', fresh_session)
            return label, ('Le texte réservé C12 ' + label + ' révèle') in text
        responses = list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(concurrent_read, jobs))
        after_race = wp('echo wp_json_encode(get_option("' + key + '"));')
        granted = {label for label, full in responses if full}
        checks['concurrence_quota_atomique'] = len(after_race['articles']) == 2 and len(granted) == 1
        settings_post(admin, dict(desired, nombre=3))
        new_label = 'trois' if ids['trois'] not in after_race['articles'] else 'deux'
        _, _, text = fetch('/c12-decouverte-' + new_label + '/', fresh_session)
        checks['changement_nombre_sans_recredit'] = 'data-imagine-bloc="decouverte_epuisee"' in text and wp('echo wp_json_encode(get_option("' + key + '"));') == after_race
        settings_post(admin, dict(desired, numeros=[]))
        _, _, text = fetch(path, fresh_session)
        checks['perimetre_vide_ferme_sans_consommation'] = witness not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == after_race
        settings_post(admin, dict(desired, forme='duree', jours=1, nombre=1))
        wp('delete_option("' + key + '");echo "true";')
        _, _, text = fetch(path, fresh_session)
        checks['duree_HTTP_positive'] = witness in text and 'UTC (fin exclue)' in text
        wp('$s=get_option("' + key + '");$s["debut"]=gmdate("Y-m-d H:i:s",time()-DAY_IN_SECONDS);update_option("' + key + '",$s);echo "true";')
        duration_state = wp('echo wp_json_encode(get_option("' + key + '"));')
        _, _, text = fetch('/c12-decouverte-deux/', fresh_session)
        checks['duree_HTTP_epuisee_sans_renouveler'] = 'Le texte réservé C12 deux révèle' not in text and 'data-imagine-bloc="decouverte_epuisee"' in text and wp('echo wp_json_encode(get_option("' + key + '"));') == duration_state
        settings_post(admin, dict(desired, ouverture='fermee'))
        _, _, text = fetch(path, fresh_session)
        checks['fermeture_generale_HTTP'] = witness not in text and wp('echo wp_json_encode(get_option("' + key + '"));') == duration_state
    finally:
        code = '$old=json_decode(' + json.dumps(json.dumps(before)) + ',true);$key=' + json.dumps(key) + ';foreach([$key=>"etat","imagine_decouverte_reglages"=>"policy","imagine_decouverte_relecture"=>"relecture"] as $option=>$field){if($old[$field]===null){delete_option($option);}else{update_option($option,$old[$field]);}}if($old["verifie"]===""){delete_user_meta(' + str(user) + ',"imagine_email_confirme");}else{update_user_meta(' + str(user) + ',"imagine_email_confirme",$old["verifie"]);}echo "true";'
        wp(code)
        restored = wp('$id=' + str(user) + ';echo wp_json_encode(["etat"=>get_option("' + key + '",null),"policy"=>get_option("imagine_decouverte_reglages",null),"relecture"=>get_option("imagine_decouverte_relecture",null),"verifie"=>get_user_meta($id,"imagine_email_confirme",true)]);')
        checks['restauration_exacte'] = restored == before
        wp('$old=json_decode(' + json.dumps(json.dumps(c10_before)) + ',true);foreach($old as $key=>$value){if($value===null){delete_option($key);}else{update_option($key,$value);}}echo "true";')
        c10_after = wp('$out=[];foreach(["imagine_acces_reglages","imagine_c05_reglages","imagine_envoi_colonnes_export"] as $k){$out[$k]=get_option($k,null);}echo wp_json_encode($out);')
        checks['C10_options_exactement_preservees'] = c10_after == c10_before
    failures = [k for k, v in checks.items() if v is not True]
    print('C12 HTTP :', len(checks) - len(failures), '/', len(checks), '; échecs :', failures)
    if failures:
        raise SystemExit(1)
    return checks


if __name__ == '__main__':
    verify()
