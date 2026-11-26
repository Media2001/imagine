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
        checks['observateurs_positifs_non_vacuite'] = witness == {'ambiance_mail': 1, 'ambiance_http': 1, 'ambiance_statut': 1, 'ambiance_abonnement': 1, 'ambiance_remboursement': 1}
        auth = c25.wp('''$admin=get_users(['role'=>'administrator','number'=>1])[0]->ID;$out=['admin'=>$admin,'cookies'=>[]];foreach([28,9,$admin] as $id){$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);$out['cookies'][$id]=LOGGED_IN_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'logged_in',$token).'; '.AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'auth',$token).'; '.SECURE_AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'secure_auth',$token);}echo wp_json_encode($out);''')
        c25.private(label + '-auth', auth)
        base = identity['url']
        def http(path, user=28, data=None, headers=None):
            import urllib.parse
            assert path.startswith('/') and not path.startswith('//')
            payload = urllib.parse.urlencode(data).encode() if data is not None else None
            request = urllib.request.Request(base + path, data=payload, headers={'Cookie': auth['cookies'][str(user)], 'User-Agent': 'Imagine-C25-fixture', **(headers or {})})
            with urllib.request.urlopen(request, timeout=40) as response:
                assert response.geturl().startswith(base + '/')
                text = response.read().decode('utf-8')
                statuses.append(response.status)
                return text
        import urllib.parse
        account = urllib.parse.urlsplit(c25.wp('echo wp_json_encode(wc_get_page_permalink("myaccount"));')).path
        path = account + '?imagine_retractation=126'
        access_code = '''$out=[];foreach([28,9] as $uid){wp_set_current_user($uid);foreach(get_posts(['post_type'=>'imagine_numero','post_status'=>'publish','numberposts'=>-1]) as $issue){$out[$uid][$issue->ID]=Imagine\\Site\\Paywall::decisionPdf($issue);}}echo wp_json_encode($out);'''
        access_before = c25.wp(access_code)
        checks['acces_temoin_positif'] = any(d['complet'] for per_user in access_before.values() for d in per_user.values())
        first = http(path)
        checks['HTTP_etape1_positive'] = 'id="imagine-retractation"' in first and 'Me rétracter' in first and 'facultatif' in first
        review = http(path, data={'etape': 'preparer', '_c25': nonce(first), 'raison': r'Motif HTTP fictif C:\dossier\fichier et \\double'})
        checks['HTTP_etape2_explicite'] = 'Confirmer ma demande de rétractation' in review and 'Commande n°126' in review
        checks['HTTP_abandon_ne_persiste_rien'] = c25.wp('echo wp_json_encode(Imagine\\Site\\Retractation::lire(126));') is None
        bad = http(path, data={'etape': 'confirmer', '_c25': nonce(first), 'raison': r'Motif HTTP fictif C:\dossier\fichier et \\double', 'confirmation': 'confirmer'})
        checks['HTTP_nonce_etape1_pas_confirmation'] = 'Demande refusée' in bad and c25.wp('echo wp_json_encode(Imagine\\Site\\Retractation::lire(126));') is None
        post = {'etape': 'confirmer', '_c25': nonce(review), 'raison': r'Motif HTTP fictif C:\dossier\fichier et \\double', 'confirmation': 'confirmer'}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda _: http(path, data=post), range(2)))
        checks['HTTP_concurrence_deux_accuses'] = all('Accusé de réception' in text for text in replies)
        reread = http(path)
        checks['HTTP_accuse_retrouve_GET'] = 'Accusé de réception' in reread and 'imagine-retractation-accuse' in reread
        checks['HTTP_compte_tiers_refuse'] = 'Demande refusée' in http(path, user=auth['admin'])
        old = http(account + '?imagine_retractation=88', user=auth['admin'], data=post)
        checks['HTTP_POST_autrui_refuse'] = 'Demande refusée' in old
        checks['acces_moteur_C06_inchanges'] = c25.wp(access_code) == access_before
        during = c25.b06.state()
        c25.private(label + '-demande-persistee', {'business': during})
        def diffpaths(a, b, path=''):
            if isinstance(a, dict) and isinstance(b, dict):
                return [p for key in a.keys() | b.keys() for p in (diffpaths(a.get(key), b.get(key), path + '/' + str(key)))]
            return [path] if a != b else []
        outcome['during_difference_paths'] = diffpaths(before, during)
        posts_during = c25.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->posts}",ARRAY_A));')
        for row in posts_during:
            if int(row['ID']) == 126:
                old_row = next(r for r in database['posts'] if int(r['ID']) == 126)
                assert int(row['comment_count']) in [int(old_row['comment_count']), int(old_row['comment_count']) + 1]
                row['comment_count'] = old_row['comment_count']
        only_note_counter = posts_during == database['posts']
        if only_note_counter:
            during['native']['native_fingerprints']['posts'] = before['native']['native_fingerprints']['posts']
        meta_during = c25.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->usermeta}",ARRAY_A));')
        previous_meta = {row['umeta_id']: row for row in database['usermeta']}
        current_meta = {row['umeta_id']: row for row in meta_during}
        changed_meta = [current_meta.get(key, previous_meta.get(key))['meta_key'] for key in previous_meta.keys() | current_meta.keys() if previous_meta.get(key) != current_meta.get(key)]
        outcome['during_meta_changed_keys'] = sorted(set(changed_meta))
        transient_user_keys = {'session_tokens', '_woocommerce_persistent_cart_1', '_last_update', 'wc_last_active', '_wcs_subscription_ids_cache'}
        if set(changed_meta) <= transient_user_keys:
            during['native']['native_fingerprints']['usermeta'] = before['native']['native_fingerprints']['usermeta']
        checks['HTTP_commande_abonnements_acces_actions_inchanges'] = during == before and only_note_counter
        expired = http(account + '?imagine_retractation=88', user=9)
        checks['HTTP_hors_delai_sans_formulaire'] = 'id="imagine-retractation"' not in expired
        signed = c25.wp('wp_set_current_user(9);$pairs=explode("; ",' + c25.php(auth['cookies']['9']) + ');foreach($pairs as $pair){[$k,$v]=explode("=",$pair,2);$_COOKIE[$k]=$v;}echo wp_json_encode(wp_create_nonce("imagine_c25_88_confirmer_".hash("sha256","")));')
        refused = http(account + '?imagine_retractation=88', user=9, data={'etape': 'confirmer', '_c25': signed, 'raison': '', 'confirmation': 'confirmer'})
        checks['HTTP_hors_delai_POST_signe_refuse'] = 'Demande refusée' in refused and c25.wp('echo wp_json_encode(Imagine\\Site\\Retractation::lire(88));') is None
        admin = http('/wp-admin/admin.php?page=imagine-retractations', user=auth['admin'])
        checks['HTTP_admin_liste_native'] = r'Motif HTTP fictif C:\dossier\fichier et \\double' in admin and '#126' in admin
        settings = http('/wp-admin/admin.php?page=imagine-reglages', user=auth['admin'])
        checks['HTTP_C10_deux_champs_dans_formulaire'] = 'name="imagine_retractation_reglages[jours]"' in settings and 'name="imagine_retractation_reglages[origine]"' in settings
        import runpy
        outcome['settings_HTTP'] = runpy.run_path(str(c25.ROOT / 'wp/outils/demo/c25-settings.py'))['run'](c25, http, base, auth['admin'], checks)
        result = c25.b06.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/' + runtime + '";', check=False)
        native = json.loads(result['stdout'])
        outcome.update({'checks': checks, 'native': native, 'native_exit': result['code'], 'native_stderr': result['stderr'], 'http_statuses': statuses, 'observer_counts': c25.wp('echo wp_json_encode(get_option("imagine_c25_observations"));')})
        assert result['code'] == 0 and not result['stderr'] and not native['failures'], native
        assert all(checks.values()), checks
    finally:
        raw = private_path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == durable['sha256']
        saved = json.loads(raw)['payload']['database']
        admin_ids = {int(x['ID']) for x in saved['users'] if x['ID'] == str(auth['admin'])} if 'auth' in locals() else set()
        users = {28, 9, *admin_ids}
        rows = [row for row in saved['usermeta'] if int(row['user_id']) in users]
        dates = [row for row in saved['postmeta'] if int(row['post_id']) in [88, 94] and row['meta_key'] == '_imagine_retractation_debut']
        hpos_orders = [row for row in saved['wc_orders'] if int(row['id']) in [88, 94]]
        hpos_meta = [row for row in saved['wc_orders_meta'] if int(row['order_id']) in [88, 94]]
        original_max_id = max(int(r['option_id']) for r in saved['options'])
        outcome['settings_journals_removed'] = c25.wp('''global $wpdb;$removed=[];foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_id>''' + str(original_max_id) + ''' AND option_name LIKE 'imagine_reglages_journal_%'",ARRAY_A) as $row){$event=maybe_unserialize($row['option_value']);if(is_array($event)&&($event['option']??'')==='imagine_retractation_reglages'){if(!delete_option($row['option_name']))throw new RuntimeException('Inverse journal refusée');$removed[]=$row['option_name'];}}echo wp_json_encode($removed);''')
        restored = c25.wp('''global $wpdb;foreach(''' + c25.php(hpos_orders) + ''' as $row){$wpdb->update($wpdb->prefix.'wc_orders',$row,['id'=>$row['id']]);}foreach([88,94] as $id){$wpdb->delete($wpdb->prefix.'wc_orders_meta',['order_id'=>$id]);}foreach(''' + c25.php(hpos_meta) + ''' as $row){$wpdb->insert($wpdb->prefix.'wc_orders_meta',$row);}wp_cache_flush();$out=[];$notes=$wpdb->get_col($wpdb->prepare("SELECT comment_id FROM {$wpdb->commentmeta} WHERE meta_key=%s",Imagine\\Site\\Retractation::META));foreach($notes as $note){wp_delete_comment((int)$note,true);}foreach([126,88] as $id){delete_option(Imagine\\Site\\Retractation::JOURNAL.$id);}delete_option(Imagine\\Site\\Retractation::OPTION);delete_option('imagine_c25_observations');foreach([88,94] as $id){$wpdb->delete($wpdb->postmeta,['post_id'=>$id,'meta_key'=>'_imagine_retractation_debut']);wp_cache_delete($id,'post_meta');}foreach(''' + c25.php(dates) + ''' as $row){$wpdb->insert($wpdb->postmeta,$row);}foreach(''' + c25.php(list(users)) + ''' as $id){$wpdb->delete($wpdb->usermeta,['user_id'=>$id]);wp_cache_delete($id,'user_meta');}foreach(''' + c25.php(rows) + ''' as $row){$wpdb->insert($wpdb->usermeta,$row);}echo wp_json_encode(['notes_absentes'=>Imagine\\Site\\RetractationConfidentialite::lignes()===[],'demandes_absentes'=>get_option(Imagine\\Site\\Retractation::JOURNAL.'126',null)===null&&get_option(Imagine\\Site\\Retractation::JOURNAL.'88',null)===null,'reglage_absent'=>get_option(Imagine\\Site\\Retractation::OPTION,null)===null]);''')
        removed = remove_remote([observer, runtime])
        after = c25.b06.state()
        current = c25.snapshot()
        # Comparaison exacte métier ; sessions visées et dates temporaires sont restaurées depuis les lignes brutes.
        exact = {key: current[key] == saved[key] for key in ['users', 'usermeta', 'posts', 'postmeta', 'comments', 'commentmeta', 'wc_orders', 'wc_orders_meta', 'wc_order_addresses', 'wc_order_operational_data', 'woocommerce_order_items', 'woocommerce_order_itemmeta']}
        business_options = lambda db: [row for row in db['options'] if row['option_name'].startswith('imagine_') or row['option_name'] == 'cron']
        exact['business_options'] = business_options(current) == business_options(saved)
        outcome.update(sources=c25.sources(), identity=identity, private_snapshot=durable, restoration=restored, tests_removed=removed, business_preserved=after == before, exact_rows_preserved=exact)
        c25.save(label, outcome)
        print(json.dumps({'checks': checks, 'native': outcome.get('native'), 'restoration': restored, 'business_preserved': after == before, 'exact_rows_preserved': exact}, ensure_ascii=False))
        assert all(restored.values()) and after == before and all(exact.values()), 'Restauration non prouvée'


if __name__ == '__main__':
    run(sys.argv[1])
