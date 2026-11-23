"""C10 : options.php natif, sessions WP éphémères, aucun secret dans les preuves."""
from pathlib import Path
import hashlib
import html
import http.cookiejar
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPCookieProcessor
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10
import construire as b00

PAGE = '/wp-admin/admin.php?page=imagine-reglages'
A, P, E = 'imagine_acces_reglages', 'imagine_c05_reglages', 'imagine_envoi_colonnes_export'


class Form(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('type') == 'hidden' and a.get('name'):
            self.hidden[a['name']] = a.get('value', '')


def state():
    code = '''$s=new Imagine\\Pilotage\\Administration\\Reglages();$out=[];foreach($s->defauts() as $k=>$d){$out['values'][$k]=get_option($k,$d);}global $wpdb;$like=$wpdb->esc_like($s::JOURNAL).'%';$out['audit_count']=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE %s",$like));$out['journal']=$s->journal();echo wp_json_encode($out);'''
    return json.loads(b00.wp('eval', code)['stdout'])


def session(login, base):
    # Aucun mot de passe : session WP native réservée au runner local fictif, détruite en finally.
    code = '$u=get_user_by("login",' + json.dumps(login) + ''');$exp=time()+1800;$m=WP_Session_Tokens::get_instance($u->ID);$t=$m->create($exp);wp_set_current_user($u->ID);$auth=wp_generate_auth_cookie($u->ID,$exp,'auth',$t);$logged=wp_generate_auth_cookie($u->ID,$exp,'logged_in',$t);$_COOKIE[LOGGED_IN_COOKIE]=$logged;echo wp_json_encode(['id'=>$u->ID,'token'=>$t,'cookies'=>[AUTH_COOKIE=>$auth,LOGGED_IN_COOKIE=>$logged],'nonce'=>wp_create_nonce('imagine_reglages-options')]);'''
    secret = json.loads(b00.wp('eval', code)['stdout'])
    jar = http.cookiejar.CookieJar()
    from urllib.parse import urlsplit
    host = urlsplit(base).hostname
    for name, value in secret['cookies'].items():
        jar.set_cookie(http.cookiejar.Cookie(0, name, value, None, False, host, False, False,
            '/', True, False, None, True, None, None, {}, False))
    return build_opener(HTTPCookieProcessor(jar)), secret


def destroy(secret):
    code = '$m=WP_Session_Tokens::get_instance(' + str(secret['id']) + ');$t=' + json.dumps(secret['token']) + ';$m->destroy($t);echo wp_json_encode(!$m->get($t));'
    return json.loads(b00.wp('eval', code)['stdout']) is True


def fetch(base, path, client=None, data=None):
    if base != 'http://192.168.129.32:8085' or path not in (PAGE, '/wp-admin/options.php'):
        raise ValueError('Cible C10 non autorisée')
    client = client or build_opener()
    request = Request(base + path, data=data, headers={'User-Agent': 'Imagine-C10-tests/1.0'})
    try:
        response = client.open(request, timeout=60)
    except HTTPError as error:
        response = error
    body = response.read().decode('utf-8', errors='replace')
    if any(word in body for word in ['Fatal error', 'Warning:', 'Uncaught Error', 'critical error']):
        raise RuntimeError('Erreur PHP dans réponse C10')
    return response.code, body


def fields(values):
    result = {}
    for option, value in values.items():
        if option == E and isinstance(value, list):
            result[option] = '\n'.join(value)
        elif isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, list):
                    result[option + '[' + key + '][]'] = val
                else:
                    result[option + '[' + key + ']'] = '' if val is None else str(val)
        else:
            result[option] = value
    return result


def verify():
    site, _ = c10.c08.guard()
    base = site['url'].rstrip('/')
    protected = c10.snapshot()
    before = state()
    original = before['values']
    checks, responses = {}, {}
    sessions = []
    record = {'scope': b00.SLUG, 'at': datetime.now(timezone.utc).isoformat(), 'url': base}

    def check(name, condition):
        checks[name] = bool(condition)

    def post(client, values, nonce=True, extra=None):
        _, page = fetch(base, PAGE, client)
        parser = Form()
        parser.feed(page)
        data = {**parser.hidden, **fields(values), 'option_page': 'imagine_reglages', 'action': 'update', '_wp_http_referer': PAGE}
        if nonce is False:
            data.pop('_wpnonce', None)
        elif isinstance(nonce, str):
            data['_wpnonce'] = nonce
        data.update(extra or {})
        return fetch(base, '/wp-admin/options.php', client, urlencode(data, doseq=True).encode())

    try:
        admin, admin_secret = session('e-admin', base)
        sessions.append(admin_secret)
        editor, editor_secret = session('e-redac', base)
        sessions.append(editor_secret)
        subscriber, sub_secret = session('imagine-c08-sans-droit', base)
        sessions.append(sub_secret)
        code, page = fetch(base, PAGE, admin)
        check('admin_page_200', code == 200 and 'Réglages Imagine' in page)
        check('menu_imagine_reglages', 'toplevel_page_imagine' in page and '>Réglages</a>' in page)
        check('huit_champs_documentes', page.count('class="imagine-reglage"') == 8 and page.count('À confirmer par Imagine') == 8 and page.count('Défaut :') == 8)
        check('aucun_menu_legacy', not any('page=' + slug + '"' in page for slug in ['imagine-acces', 'imagine-c05', 'imagine-envoi-export']))
        for label, client, nonce in [('redacteur', editor, editor_secret['nonce']), ('abonne', subscriber, sub_secret['nonce'])]:
            code, _ = fetch(base, PAGE, client)
            check(label + '_page_403', code == 403)
            prior = state()
            code, denied = post(client, original, nonce=nonce)
            # WooCommerce redirige les abonnés hors de l’administration avant options.php.
            refused = code == 403 if label == 'redacteur' else (code == 200 and 'My account' in denied and 'imagine-reglage' not in denied)
            check(label + '_post_nonce_valide_refuse', refused)
            responses[label] = {'status': code, 'refus': 'WordPress 403' if code == 403 else 'Redirection WooCommerce vers Mon compte'}
            check(label + '_sans_mutation', prior == state())
        prior = state()
        code, _ = fetch(base, '/wp-admin/options.php', data=urlencode({'option_page':'imagine_reglages','action':'update','_wpnonce':admin_secret['nonce']}).encode())
        check('anonyme_post_refuse', code in (200, 403) and prior == state())
        for label, nonce in [('absent', False), ('invalide', 'nonce-invalide-c10'), ('autre_session', editor_secret['nonce'])]:
            prior = state()
            code, _ = post(admin, original, nonce=nonce)
            check('nonce_' + label + '_403', code == 403)
            check('nonce_' + label + '_aucune_ecriture', prior == state())

        # Premier enregistrement des défauts : pas de faux changement dans le journal.
        code, page = post(admin, original)
        check('post_valide_200', code == 200)
        check('readback_defauts', state()['values'] == original)
        check('noop_aucun_journal', state()['audit_count'] == before['audit_count'])
        baseline = state()
        bad = []
        for key in original[A]:
            v = json.loads(json.dumps(original)); v[A][key] = 'inconnu-c10'
            bad.append(('acces_' + key, v))
        for key, value in [('marge_jours','-1'),('marge_jours','1.5'),('marge_jours','0'),
                           ('marge_jours','999999999999999999999999999999999999'),
                           ('apres_rejet','inconnu'),('tarif','inconnu'),('confirmation_premier_sepa','inconnu')]:
            v = json.loads(json.dumps(original)); v[P][key] = value
            bad.append(('paiement_' + key + '_' + str(value), v))
        for value in ['inconnue', 'ville\nville', '', '<script>alerte</script>']:
            v = json.loads(json.dumps(original)); v[E] = value
            bad.append(('export_' + str(len(bad)), v))
        for option in [A,P]:
            for value in ['texte-invalide', {}, {'extra':'invalide'}]:
                v = json.loads(json.dumps(original)); v[option] = value
                bad.append(('forme_' + str(len(bad)), v))
        for label, values in bad:
            code, page = post(admin, values)
            after = state()
            check(label + '_refuse', code == 200 and any(word in html.unescape(page) for word in ['refusé','refusés','invalide']))
            check(label + '_ancien_conserve', after == baseline)

        # Toutes les positions admises des trois adaptateurs, par vrais POST.
        alternate = {A:{'contenu_futur':'equipe','pdf_robot':'complet','pdf_anterieur_abonnement':'ouvert'},
            P:{'marge_jours':3,'apres_rejet':'annuler_restantes','tarif':'courant_impayes','confirmation_premier_sepa':'sans_marge'},
            E:['ville','destinataire','pays']}
        prior = state()
        code, page = post(admin, alternate)
        after = state()
        check('valeurs_alternatives_lues_exactes', code == 200 and after['values'] == alternate)
        check('trois_changements_trois_journaux', after['audit_count'] == prior['audit_count'] + 3)
        recent = after['journal'][:3]
        check('audit_qui_quand', all(row['qui_id'] == admin_secret['id'] and row['qui_login'] == 'e-admin'
            and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', row['quand_utc']) for row in recent))
        check('audit_avant_apres_exacts', {row['option']:(row['avant'],row['apres']) for row in recent}
            == {key:(original[key],alternate[key]) for key in [A,P,E]})
        csv = html.unescape(re.search(r'<pre id="imagine-csv-apercu">(.*?)</pre>', page, re.S).group(1))
        check('effet_export_C07_reel', csv.splitlines() == ['ville,destinataire,pays','"Ville Fictive","Lectrice Fictive C10",BE'])
        record['effect'] = {'setting':E, 'changed_columns':alternate[E], 'csv_after':csv,
            'source':'ExportCsv::lignes avec AdministrationFormatExport::lire, rendu dans la vraie page admin'}
        code, _ = post(admin, alternate)
        check('second_enregistrement_sans_faux_audit', state() == after)
        record['audit_evidence'] = recent
        # Restauration par le même parcours : événements de retour conservés.
        code, _ = post(admin, original)
        check('retour_defauts_exact', code == 200 and state()['values'] == original)
        check('retour_journalise', state()['audit_count'] == after['audit_count'] + 3)
        record['audit_count_before'] = before['audit_count']
        record['audit_count_after'] = state()['audit_count']
        record['invalid_cases'] = len(bad)
    finally:
        # Si un test s'interrompt, tenter la restauration sans effacer la piste d'audit.
        if sessions and state()['values'] != original:
            post(admin, original)
        for secret in sessions:
            check('session_detruite_' + str(secret['id']), destroy(secret))
        check('C08_C09_contenus_comptes_bibliotheques_preserves', protected == c10.snapshot())
        record.update(checks=checks, total=len(checks), responses=responses, failures=[k for k,v in checks.items() if not v])
        record['status'] = 'VERIFIED' if not record['failures'] else 'FAILED'
        (c10.PROOF / 'http-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(record, ensure_ascii=False, indent=2))
    if record['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    verify()
