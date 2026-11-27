"""Preuve native B07 antislash : POST HTTP, boîte admin, export, inverses ciblées."""
import sys
sys.dont_write_bytecode = True
import hashlib
import html.parser
import json
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request
import c27

ROOT = c27.ROOT
PROOF = ROOT / 'production/B-07'
AGENDA = 'plugins/imagine-site/Agenda.php'
OBSERVER = 'mu-plugins/imagine-b07-antislash-observer.php'
TRACE = 'imagine-demo-build/b07-antislash-observations.jsonl'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Inputs(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'input' and attrs.get('name'):
            self.inputs[attrs['name']] = attrs.get('value', '')


def http(url, values=None):
    request = Request(url, data=urlencode(values).encode() if values else None)
    try:
        response = build_opener(NoRedirect).open(request, timeout=30)
    except HTTPError as error:
        response = error
    return response.code, dict(response.headers), response.read().decode('utf-8')


def run():
    receipt = PROOF / 'antislash-native.json'
    assert not receipt.exists()
    identity = c27.guard()
    before = c27.snapshot()
    business = c27.state()
    source = (ROOT/'wp'/AGENDA).read_bytes()
    red_hash = json.loads((PROOF/'antislash-red.json').read_text(encoding='utf-8'))['sources']['wp/'+AGENDA]
    remote = c27.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+AGENDA+'"));')
    assert hashlib.sha256(remote.encode()).hexdigest() == red_hash, 'Préimage distante inattendue'
    assert c27.wp('$v=[];foreach('+c27.php([OBSERVER, TRACE])+' as $n){$v[]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);') == [False, False]
    fixture = c27.wp('$id=(int)get_option("imagine_b07_fixture")["rencontre"];echo wp_json_encode(["id"=>$id,"url"=>get_permalink($id),"open"=>Imagine\\Site\\Agenda::ouvert($id)]);')
    assert fixture['open'] and urlsplit(fixture['url']).netloc == urlsplit(identity['url']).netloc
    emails = ['b07-antislash-'+str(i)+'@example.org' for i in range(4)]
    assert c27.wp('$v=[];foreach('+c27.php(emails)+' as $e){$v[]=Imagine\\Site\\Agenda::inscriptions($e);}echo wp_json_encode($v);') == [[], [], [], []]
    durable = c27.private('b07-antislash', {'database': before, 'business': business, 'agenda': remote})
    result = {'identity': identity, 'private_snapshot': durable, 'fixture': fixture,
              'before_agenda_sha256': red_hash, 'agenda_sha256': hashlib.sha256(source).hexdigest(),
              'sources': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
                  'wp/outils/demo/b07-antislash-native.py', 'wp/tests/demo/b07-antislash-observer.php']}}
    deployed = False
    try:
        # Seul notre fichier de trace neuf devient inscriptible (aucun dossier partagé).
        c27.upload(TRACE, b'')
        code = 'from pathlib import Path;p=Path("/app/sites/imagine-test-demo/wp-content/'+TRACE+'");assert p.is_file() and p.stat().st_size==0;p.chmod(0o666)'
        subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'exec', 'staging-wp-dashboard', 'python', '-c', code], check=True, capture_output=True)
        assert c27.wp('echo wp_json_encode(is_writable(WP_CONTENT_DIR."/'+TRACE+'"));') is True
        c27.upload(OBSERVER, (ROOT/'wp/tests/demo/b07-antislash-observer.php').read_bytes())
        assert c27.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR."/'+OBSERVER+'"));') == result['sources']['wp/tests/demo/b07-antislash-observer.php']
        witness = c27.wp('$m=apply_filters("pre_wp_mail",null,[]);$h=apply_filters("pre_http_request",false,[],"https://example.org");echo wp_json_encode([$m===false,is_wp_error($h)]);')
        witness_rows = c27.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+TRACE+'"));')
        parsed_witness = [json.loads(line) for line in witness_rows.splitlines()]
        assert witness == [True, True] and any(row['mail'] > 0 and row['http'] > 0 for row in parsed_witness)
        result['observer_witness'] = {'blocked_by_existing_guard': True, 'mail_and_http_detected': True}
        clear = 'from pathlib import Path;p=Path("/app/sites/imagine-test-demo/wp-content/'+TRACE+'");assert p.is_file();p.write_bytes(b"")'
        subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'exec', 'staging-wp-dashboard', 'python', '-c', clear], check=True, capture_output=True)
        status, headers, body = http(fixture['url'])
        assert status == 200 and 'imagine-agenda-inscription' in body
        parser = Inputs()
        parser.feed(body)
        values = {'action': 'imagine_agenda', 'evenement': str(fixture['id']),
                  'imagine_agenda_nonce': parser.inputs['imagine_agenda_nonce'], 'consentement': '1'}
        endpoint = identity['url'] + '/wp-admin/admin-post.php'
        noms = ['Fictif \\ Atelier', 'Fictif \\\\ double', "Fictif O'Exemple \\ & Atelier", 'Fictif sans antislash']
        red, _, red_body = http(endpoint, {**values, 'nom': noms[0], 'email': emails[0]})
        assert red == 400 and 'Inscription indisponible' in red_body
        assert c27.wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+c27.php(emails[0])+'));') == []
        result['native_red'] = {'http': red, 'no_registration': True}
        c27.upload(AGENDA, source)
        deployed = True
        assert c27.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR."/'+AGENDA+'"));') == result['agenda_sha256']
        result['cases'] = []
        for nom, email in zip(noms, emails):
            attempts = []
            for _ in range(2):
                code, headers, body = http(endpoint, {**values, 'nom': nom, 'email': email})
                location = headers.get('Location')
                assert code == 303 and location == fixture['url'] + '?inscription=enregistree'
                attempts.append({'http': code, 'location': location})
            data = c27.wp('''$email=EMAIL;$ids=Imagine\\Site\\Agenda::inscriptions($email);$id=$ids[0]??0;
$admins=get_users(['role'=>'administrator','fields'=>'ID']);wp_set_current_user((int)$admins[0]);
do_action('add_meta_boxes',Imagine\\Site\\Agenda::INSCRIPTION,get_post($id));
global $wp_meta_boxes;$box=$wp_meta_boxes[Imagine\\Site\\Agenda::INSCRIPTION]['advanced']['default']['imagine-agenda-personne'];
ob_start();$box['callback'](get_post($id));$html=ob_get_clean();
$exporters=apply_filters('wp_privacy_personal_data_exporters',[]);
$export=$exporters['imagine-agenda']['callback']($email,1);
echo wp_json_encode(['ids'=>$ids,'name'=>get_post_meta($id,'imagine_agenda_nom',true),'html'=>$html,'export'=>$export,'admin'=>current_user_can('manage_options')]);'''.replace('EMAIL', c27.php(email)))
            assert len(data['ids']) == 1 and data['name'] == nom and data['admin']
            expected = c27.wp('echo wp_json_encode(esc_html('+c27.php(nom)+'));')
            assert 'id="imagine-agenda-admin"' in data['html'] and '<dd>'+expected+'</dd>' in data['html']
            export = data['export']
            assert export['done'] and len(export['data']) == 1
            fields = {x['name']: x['value'] for x in export['data'][0]['data']}
            assert fields['Nom'] == nom
            result['cases'].append({'name': nom, 'email': email, 'post': attempts,
                                    'unique_registration': True, 'stored_exact': True,
                                    'admin_display_exact': True, 'native_export_exact': True})
        observations = c27.wp('$p=WP_CONTENT_DIR."/'+TRACE+'";echo wp_json_encode(file_get_contents($p));')
        rows = [json.loads(line) for line in observations.splitlines()]
        assert rows and len(rows) >= 10 and all(all(v == 0 for v in row.values()) for row in rows)
        result['observations'] = {'requests': len(rows), 'mail': sum(x['mail'] for x in rows),
                                  'http': sum(x['http'] for x in rows),
                                  'transport_mail': sum(x['transport_mail'] for x in rows),
                                  'transport_http': sum(x['transport_http'] for x in rows)}
        result['checks_passed'] = True
    finally:
        cleanup = {}
        try:
            c27.wp('$emails='+c27.php(emails)+';foreach($emails as $email){$ids=Imagine\\Site\\Agenda::inscriptions($email);if($ids===null){throw new RuntimeException("Nettoyage illisible");}foreach($ids as $id){wp_delete_post($id,true);}}echo wp_json_encode(true);')
            cleanup['registrations_removed'] = c27.wp('$v=[];foreach('+c27.php(emails)+' as $e){$v[]=Imagine\\Site\\Agenda::inscriptions($e);}echo wp_json_encode($v);') == [[], [], [], []]
        except Exception as error:
            cleanup['registration_error'] = str(error)
        # Retirer l'observateur avant la trace : les lectures suivantes n'en recréent pas.
        for name in [OBSERVER, TRACE]:
            try:
                c27.b09.remove_remote([name])
                cleanup[name] = c27.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+name+'"));')
            except Exception as error:
                cleanup[name] = str(error)
        after = c27.snapshot()
        exact = {k: before[k] == after[k] for k in before if k != 'options'}
        opts = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] == 'cron']
        exact['options_metier'] = opts(before) == opts(after)
        preserved = business == c27.state()
        result.update(cleanup=cleanup, restoration=exact, business_preserved=preserved,
                      corrected_agenda_deployed=deployed,
                      final_remote_sha256=c27.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR."/'+AGENDA+'"));'))
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False))
        assert cleanup and all(v is True for v in cleanup.values()) and all(exact.values()) and preserved
    assert result.get('checks_passed') and result['final_remote_sha256'] == result['agenda_sha256']


if __name__ == '__main__':
    run()
