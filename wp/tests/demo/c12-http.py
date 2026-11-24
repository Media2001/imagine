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
        path = '/c12-decouverte-un/'
        witness = 'Le texte réservé C12 un révèle des comètes turquoise entièrement fictives.'
        status, headers, body = fetch(path)
        checks['anonyme_extrait_connexion'] = status == 200 and witness not in body and 'data-imagine-bloc="connexion"' in body
        status, headers, body = fetch(path, client)
        checks['connecte_premiere_lecture_complete'] = status == 200 and witness in body
        checks['cache_prive'] = all(x in headers.get('cache-control', '') for x in ['private', 'no-store'])
        state = wp('echo wp_json_encode(get_option("' + key + '",null));')
        checks['decompte_compte_persistant'] = isinstance(state, dict) and state['articles'] == [ids['un']]
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
