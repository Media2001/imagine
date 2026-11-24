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


def verify():
    c12.c10.guard()
    ids = wp('echo wp_json_encode(get_option("imagine_c12_fixture"));')
    user = wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["V-DEC"]);')
    key = 'imagine_decouverte_compte_' + str(user)
    before = wp('$id=' + str(user) + ';echo wp_json_encode(["etat"=>get_option("' + key + '",null),"policy"=>get_option("imagine_decouverte_reglages",null),"verifie"=>get_user_meta($id,"imagine_email_confirme",true)]);')
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    checks = {}
    try:
        wp('delete_option("' + key + '");update_user_meta(' + str(user) + ',"imagine_email_confirme","1");$p=["ouverture"=>"premiere_lecture","forme"=>"articles","jours"=>7,"nombre"=>2,"numeros"=>[(string)get_option("imagine_demo_manifest")["demo-2026-t4"]]];update_option("imagine_decouverte_reglages",$p);echo "true";')
        client = login(accounts['V-DEC'])
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
    finally:
        code = '$old=json_decode(' + json.dumps(json.dumps(before)) + ',true);$key=' + json.dumps(key) + ';foreach([$key=>"etat","imagine_decouverte_reglages"=>"policy"] as $option=>$field){if($old[$field]===null){delete_option($option);}else{update_option($option,$old[$field]);}}if($old["verifie"]===""){delete_user_meta(' + str(user) + ',"imagine_email_confirme");}else{update_user_meta(' + str(user) + ',"imagine_email_confirme",$old["verifie"]);}echo "true";'
        wp(code)
        restored = wp('$id=' + str(user) + ';echo wp_json_encode(["etat"=>get_option("' + key + '",null),"policy"=>get_option("imagine_decouverte_reglages",null),"verifie"=>get_user_meta($id,"imagine_email_confirme",true)]);')
        checks['restauration_exacte'] = restored == before
    failures = [k for k, v in checks.items() if v is not True]
    print('C12 HTTP :', len(checks) - len(failures), '/', len(checks), '; échecs :', failures)
    if failures:
        raise SystemExit(1)
    return checks


if __name__ == '__main__':
    verify()
