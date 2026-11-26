"""Recette C25 HTTP/native avec inverse bornée et readback métier exact."""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path
from html import unescape
import c25


def remove_remote(names):
    assert all(n.startswith(('mu-plugins/c25-', 'imagine-demo-build/c25-')) for n in names)
    code = 'import pathlib,json; base=pathlib.Path("/app/sites/imagine-test-demo/wp-content"); names=' + repr(names) + ';[(base/n).unlink(missing_ok=True) for n in names];print(json.dumps({n:not(base/n).exists() for n in names}))'
    result = subprocess.run(['wsl.exe', 'docker', 'exec', 'staging-wp-dashboard', 'python', '-c', code], capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert all(data.values())
    return data


def nonce(html):
    found = re.findall(r'name="_c25" value="([^"]+)"', html)
    assert len(found) == 1
    return unescape(found[0])


def run(label):
    assert not (c25.PROOF / (label + '.json')).exists()
    identity = c25.b06.guard()
    before = c25.b06.state()
    database = c25.snapshot()
    assert not any(row['option_name'] in [c25key for c25key in ['imagine_retractation_reglages', 'imagine_c25_observations', 'imagine_reglages_journal_retractation_126', 'imagine_reglages_journal_retractation_88']] for row in database['options']), 'Une recette précédente doit être restaurée avant de rejouer'
    durable = c25.private(label, {'database': database, 'business': before})
    # Le même snapshot durable sera relu depuis ses octets avant toute inverse.
    private_path = Path(__import__('os').environ['TMPDIR']) / durable['file']
    observer = 'mu-plugins/c25-observer.php'
    runtime = 'imagine-demo-build/c25-runtime.php'
    assert c25.wp('$out=[];foreach(' + c25.php([observer, runtime]) + ' as $n){$out[$n]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);') == {observer: False, runtime: False}
    checks = {}
    statuses = []
    outcome = {}
    try:
        c25.b06.profils.b00.upload(observer, (c25.ROOT / 'wp/tests/demo/c25-observer.php').read_bytes())
        c25.b06.profils.b00.upload(runtime, (c25.ROOT / 'wp/tests/demo/c25-runtime.php').read_bytes())
        # Témoins positifs : les observateurs voient les appels, toujours bloqués par B00.
        witness = c25.wp('''wp_mail('fictif@example.org','Test fictif','Fictif');wp_remote_get('https://example.org/');global $wp_filter;foreach(['woocommerce_order_status_changed','woocommerce_subscription_status_updated','woocommerce_order_refunded'] as $hook){foreach($wp_filter[$hook]->callbacks[-1000] as $item){($item['function'])(null);}}$v=get_option('imagine_c25_observations');update_option('imagine_c25_observations',[],false);echo wp_json_encode($v);''')
        checks['observateurs_positifs_non_vacuite'] = witness == {'mail': 1, 'http': 1, 'statut': 1, 'abonnement': 1, 'remboursement': 1}
        auth = c25.wp('''$admin=get_users(['role'=>'administrator','number'=>1])[0]->ID;$out=['admin'=>$admin,'cookies'=>[]];foreach([28,$admin] as $id){$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);$out['cookies'][$id]=LOGGED_IN_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'logged_in',$token).'; '.AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'auth',$token).'; '.SECURE_AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'secure_auth',$token);}echo wp_json_encode($out);''')
        c25.private(label + '-auth', auth)
        base = identity['url']
        def http(path, user=28, data=None):
            import urllib.parse
            assert path.startswith('/') and not path.startswith('//')
            payload = urllib.parse.urlencode(data).encode() if data is not None else None
            request = urllib.request.Request(base + path, data=payload, headers={'Cookie': auth['cookies'][str(user)], 'User-Agent': 'Imagine-C25-fixture'})
            with urllib.request.urlopen(request, timeout=40) as response:
                assert response.geturl().startswith(base + '/')
                text = response.read().decode('utf-8')
                statuses.append(response.status)
                return text
        import urllib.parse
        account = urllib.parse.urlsplit(c25.wp('echo wp_json_encode(wc_get_page_permalink("myaccount"));')).path
        path = account + '?imagine_retractation=126'
        first = http(path)
        checks['HTTP_etape1_positive'] = 'id="imagine-retractation"' in first and 'Me rétracter' in first and 'facultatif' in first
        review = http(path, data={'etape': 'preparer', '_c25': nonce(first), 'raison': 'Motif HTTP fictif'})
        checks['HTTP_etape2_explicite'] = 'Confirmer ma demande de rétractation' in review and 'Commande n°126' in review
        checks['HTTP_abandon_ne_persiste_rien'] = c25.wp('echo wp_json_encode(Imagine\\Site\\Retractation::lire(126));') is None
        bad = http(path, data={'etape': 'confirmer', '_c25': nonce(first), 'raison': 'Motif HTTP fictif', 'confirmation': 'confirmer'})
        checks['HTTP_nonce_etape1_pas_confirmation'] = 'Demande refusée' in bad and c25.wp('echo wp_json_encode(Imagine\\Site\\Retractation::lire(126));') is None
        post = {'etape': 'confirmer', '_c25': nonce(review), 'raison': 'Motif HTTP fictif', 'confirmation': 'confirmer'}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: http(path, data=post), range(2)))
        checks['HTTP_concurrence_deux_accuses'] = all('Accusé de réception' in text for text in replies)
        reread = http(path)
        checks['HTTP_accuse_retrouve_GET'] = 'Accusé de réception' in reread and 'imagine-retractation-accuse' in reread
        checks['HTTP_compte_tiers_refuse'] = 'Demande refusée' in http(path, user=auth['admin'])
        old = http(account + '?imagine_retractation=88', user=auth['admin'], data=post)
        checks['HTTP_POST_autrui_refuse'] = 'Demande refusée' in old
        admin = http('/wp-admin/admin.php?page=imagine-retractations', user=auth['admin'])
        checks['HTTP_admin_liste_native'] = 'Motif HTTP fictif' in admin and '#126' in admin
        settings = http('/wp-admin/admin.php?page=imagine-reglages', user=auth['admin'])
        checks['HTTP_C10_deux_champs_dans_formulaire'] = 'name="imagine_retractation_reglages[jours]"' in settings and 'name="imagine_retractation_reglages[origine]"' in settings
        result = c25.b06.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/' + runtime + '";', check=False)
        native = json.loads(result['stdout'])
        outcome = {'checks': checks, 'native': native, 'native_exit': result['code'], 'native_stderr': result['stderr'], 'http_statuses': statuses, 'observer_counts': c25.wp('echo wp_json_encode(get_option("imagine_c25_observations"));')}
        assert result['code'] == 0 and not result['stderr'] and not native['failures'], native
        assert all(checks.values()), checks
    finally:
        raw = private_path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == durable['sha256']
        saved = json.loads(raw)['payload']['database']
        admin_ids = {int(x['ID']) for x in saved['users'] if x['ID'] == str(auth['admin'])} if 'auth' in locals() else set()
        users = {28, *admin_ids}
        rows = [row for row in saved['usermeta'] if int(row['user_id']) in users]
        dates = [row for row in saved['postmeta'] if int(row['post_id']) in [88, 94] and row['meta_key'] == '_imagine_retractation_debut']
        restored = c25.wp('''global $wpdb;$out=[];$notes=$wpdb->get_col($wpdb->prepare("SELECT comment_id FROM {$wpdb->commentmeta} WHERE meta_key=%s",Imagine\\Site\\Retractation::META));foreach($notes as $note){wp_delete_comment((int)$note,true);}foreach([126,88] as $id){delete_option(Imagine\\Site\\Retractation::JOURNAL.$id);}delete_option(Imagine\\Site\\Retractation::OPTION);delete_option('imagine_c25_observations');foreach([88,94] as $id){$wpdb->delete($wpdb->postmeta,['post_id'=>$id,'meta_key'=>'_imagine_retractation_debut']);wp_cache_delete($id,'post_meta');}foreach(''' + c25.php(dates) + ''' as $row){$wpdb->insert($wpdb->postmeta,$row);}foreach(''' + c25.php(list(users)) + ''' as $id){$wpdb->delete($wpdb->usermeta,['user_id'=>$id]);wp_cache_delete($id,'user_meta');}foreach(''' + c25.php(rows) + ''' as $row){$wpdb->insert($wpdb->usermeta,$row);}echo wp_json_encode(['notes_absentes'=>Imagine\\Site\\RetractationConfidentialite::lignes()===[],'demandes_absentes'=>get_option(Imagine\\Site\\Retractation::JOURNAL.'126',null)===null&&get_option(Imagine\\Site\\Retractation::JOURNAL.'88',null)===null,'reglage_absent'=>get_option(Imagine\\Site\\Retractation::OPTION,null)===null]);''')
        removed = remove_remote([observer, runtime])
        after = c25.b06.state()
        current = c25.snapshot()
        # Comparaison exacte métier ; sessions visées et dates temporaires sont restaurées depuis les lignes brutes.
        exact = {key: current[key] == saved[key] for key in ['users', 'usermeta', 'posts', 'postmeta', 'comments', 'commentmeta']}
        outcome.update(identity=identity, private_snapshot=durable, restoration=restored, tests_removed=removed, business_preserved=after == before, exact_rows_preserved=exact)
        c25.save(label, outcome)
        print(json.dumps({'checks': checks, 'native': outcome.get('native'), 'restoration': restored, 'business_preserved': after == before, 'exact_rows_preserved': exact}, ensure_ascii=False))
        assert all(restored.values()) and after == before and all(exact.values()), 'Restauration non prouvée'


if __name__ == '__main__':
    run(sys.argv[1])
