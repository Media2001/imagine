"""Recette HTTP B08, préimage privée avant sessions et inverse bornée."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path
import b08


def run(label):
    assert not (b08.PROOF / (label + '.json')).exists()
    identity = b08.c25.b06.guard()
    database = b08.snapshot()
    before = b08.c25.b06.state()
    durable = b08.c25.private('b08-' + label, {'database': database, 'business': before})
    private_path = Path(os.environ['TMPDIR']) / durable['file']
    observer = 'mu-plugins/b08-observer.php'
    assert not b08.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/' + observer + '"));')
    assert b08.wp('echo wp_json_encode(get_posts(["post_type"=>"imagine_sujet","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]));') == []
    checks = {}
    auth = None
    outcome = {}
    try:
        b08.c25.b06.profils.b00.upload(observer, (b08.ROOT / 'wp/tests/demo/b08-observer.php').read_bytes())
        positive = b08.wp('''wp_mail('fictif@example.org','Fictif','Fictif');wp_remote_get('https://example.org/');$v=get_option('imagine_b08_observations');update_option('imagine_b08_observations',[],false);echo wp_json_encode($v);''')
        checks['observateurs_positifs'] = positive == {'ambiance_mail': 1, 'ambiance_http': 1}
        auth = b08.wp('''$id=get_users(['role'=>'administrator','number'=>1])[0]->ID;$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);echo wp_json_encode(['id'=>$id,'cookie'=>LOGGED_IN_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'logged_in',$token).'; '.AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'auth',$token).'; '.SECURE_AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'secure_auth',$token)]);''')
        b08.c25.private('b08-' + label + '-auth', auth)
        def http(path, data=None, admin=False):
            assert path.startswith('/') and not path.startswith('//')
            headers = {'User-Agent': 'Imagine-B08-fictif'}
            if admin:
                headers['Cookie'] = auth['cookie']
            request = urllib.request.Request(identity['url'] + path, data=urllib.parse.urlencode(data).encode() if data is not None else None, headers=headers)
            with urllib.request.urlopen(request, timeout=35) as reply:
                assert reply.geturl().startswith(identity['url'] + '/')
                return reply.status, reply.read().decode('utf-8'), reply.geturl()
        _, home, _ = http('/')
        nav = re.search(r'<nav aria-label="Navigation principale">(.*?)</nav>', home, re.S).group(1)
        labels = [unescape(re.sub('<.*?>', '', a)).strip() for a in re.findall(r'<a\b[^>]*>(.*?)</a>', nav, re.S)]
        expected = ['Nos numéros', 'Thématiques', 'Nos newsletters', 'Nos événements', 'Notre coopérative', 'projet éditorial et manifeste', "charte d'indépendance", 'charte IA', 'baromètre égalité-diversité', 'équipe', 'gouvernance', 'Imagine COOP', 'Soutenir', "S'abonner", 'Connexion']
        checks['menu_natif_intitules_ordre'] = labels == [t.replace("'", '’') for t in expected]
        checks['sujet_hors_menu'] = 'Proposer un sujet' not in labels and len(labels) == 15
        checks['anciens_selecteurs_navigation'] = all('data-imagine-nav="' + key + '"' in nav for key in ['kiosque', 'agenda', 'compte'])
        pages = json.loads((b08.PROOF / 'pages-menu.json').read_text(encoding='utf-8'))['readback']
        for row in pages:
            code, html, url = http(urllib.parse.urlsplit(row['url']).path)
            checks['page_publique_' + str(row['id'])] = code == 200 and unescape(re.search(r'<h1>(.*?)</h1>', html, re.S).group(1)) == row['title'].replace("'", '’')
        _, coop, _ = http('/notre-cooperative/')
        article = coop.split('<article>', 1)[1].split('</article>', 1)[0]
        checks['liens_sujet_B06'] = '/proposer-un-sujet/' in article and '/espace-cooperateurs/' in article
        _, support, _ = http('/soutenir/')
        body = support.split('<article>', 1)[1].split('</article>', 1)[0]
        checks['don_OFF_parts_texte_positifs'] = 'id="imagine-soutenir"' in body and 'prise de parts' in body and 'don ponctuel' not in body and 'sponsored' not in body and '#imagine-abonnement' in body
        b08.wp('update_option(Imagine\\Site\\Soutenir::OPTION,["don"=>true,"parts_url"=>"https://example.org/parts-fictives"],false);echo wp_json_encode(Imagine\\Site\\Soutenir::configuration());')
        _, support, _ = http('/soutenir/')
        body = support.split('<article>', 1)[1].split('</article>', 1)[0]
        checks['don_ON_sans_paiement_parts_sponsored'] = all(t in body for t in ['don ponctuel ou récurrent', 'sans paiement', 'rel="sponsored"', 'https://example.org/parts-fictives']) and '<iframe' not in body and '<form' not in body
        _, form, _ = http('/proposer-un-sujet/')
        node = form.split('<form id="imagine-sujet"', 1)[1].split('</form>', 1)[0]
        checks['consentement_decocher_formulaire_public'] = 'type="checkbox"' in node and 'checked' not in node
        nonce = unescape(re.search(r'name="_b08" value="([^"]+)"', node).group(1))
        known = b08.wp('echo wp_json_encode(get_userdata(28)->user_email);')
        subject = 'B08_SUJET_PRIVE_TEMOIN_2026 C:\\dossier\\fichier\nDeuxième ligne \\ et apostrophe\'s'
        name = 'Personnage fictif B08 \\ rédaction'
        payload = {'action': 'imagine_sujet', '_b08': nonce, 'nom': name, 'email': known, 'sujet': subject}
        _, reply1, url1 = http('/wp-admin/admin-post.php', payload)
        payload2 = {**payload, 'email': 'b08-inconnu@example.org', 'sujet': 'B08_TIERS_PRIVE_TEMOIN_2026', 'consentement': '1'}
        _, reply2, url2 = http('/wp-admin/admin-post.php', payload2)
        checks['POST_reel_messages_uniformes'] = 'proposition=enregistree' in url1 and url1 == url2 and 'Votre proposition a été enregistrée localement.' in reply1 and 'Votre proposition a été enregistrée localement.' in reply2
        stored = b08.wp('$a=Imagine\\Site\\Sujet::ids(' + b08.php(known) + ');$b=Imagine\\Site\\Sujet::ids("b08-inconnu@example.org");echo wp_json_encode(["a"=>$a,"b"=>$b,"consentements"=>[get_post_meta($a[0],"imagine_sujet_consentement",true),get_post_meta($b[0],"imagine_sujet_consentement",true)],"statuts"=>[get_post($a[0])->post_status,get_post($b[0])->post_status]]);')
        checks['persistance_privee_positive'] = len(stored['a']) == len(stored['b']) == 1 and stored['consentements'] == ['0', '1'] and stored['statuts'] == ['private', 'private']
        _, invalid, invalid_url = http('/wp-admin/admin-post.php', {**payload, '_b08': 'faux'})
        checks['POST_nonce_refuse'] = 'proposition=refusee' in invalid_url
        _, admin, _ = http('/wp-admin/edit.php?post_type=imagine_sujet', admin=True)
        _, detail, _ = http('/wp-admin/post.php?post=' + str(stored['a'][0]) + '&action=edit', admin=True)
        checks['admin_liste_et_detail'] = 'Proposition de sujet' in admin and 'B08_SUJET_PRIVE_TEMOIN_2026' in detail
        subject_node = re.search(r'<strong>Sujet</strong><br>(.*?)</p>', detail, re.S)
        checks['antislash_detail_exact'] = subject_node is not None and unescape(re.sub(r'<[^>]+>', '', subject_node.group(1))) == subject
        checks['antislash_nom_detail_exact'] = name in unescape(detail)
        _, settings, _ = http('/wp-admin/options-general.php?page=imagine-soutenir', admin=True)
        checks['reglages_natifs_admin'] = 'name="imagine_soutenir[parts_url]"' in settings and 'options.php' in settings
        registry = b08.wp('''$a=apply_filters('wp_privacy_personal_data_exporters',[]);$b=apply_filters('wp_privacy_personal_data_erasers',[]);echo wp_json_encode(['export'=>isset($a['imagine-sujets']),'erase'=>isset($b['imagine-sujets'])]);''')
        checks['privacy_native_enregistre'] = all(registry.values())
        exported = b08.wp('$registry=apply_filters("wp_privacy_personal_data_exporters",[]);echo wp_json_encode(call_user_func($registry["imagine-sujets"]["callback"],' + b08.php(known) + ',1));')
        checks['antislash_export_exact'] = {field['name']: field['value'] for field in exported['data'][0]['data']}['Sujet'] == subject
        checks['antislash_nom_export_exact'] = {field['name']: field['value'] for field in exported['data'][0]['data']}['Nom'] == name
        checks['export_compte_par_adresse_sans_tiers'] = len(exported['data']) == 1 and 'B08_SUJET_PRIVE_TEMOIN_2026' in json.dumps(exported) and 'B08_TIERS_PRIVE' not in json.dumps(exported)
        # Témoin public recherché sur les mêmes collections avant toute absence privée.
        _, collection, _ = http('/wp-json/wp/v2/pages?per_page=100')
        checks['REST_temoin_public'] = 'notre-cooperative' in collection
        _, search, _ = http('/?s=Notre+coop%C3%A9rative')
        checks['recherche_temoin_public'] = 'notre-cooperative/' in search
        _, hidden, _ = http('/?s=B08_SUJET_PRIVE_TEMOIN_2026')
        checks['absence_recherche_privee'] = 'class="imagine-list"' in search and 'Aucun résultat pour votre recherche.' in hidden and 'class="imagine-list"' not in hidden.split('<main', 1)[1].split('</main>', 1)[0]
        checks['type_prive_hors_REST'] = b08.wp('echo wp_json_encode(get_post_type_object("imagine_sujet")->show_in_rest);') is False
        erased = b08.wp('echo wp_json_encode(Imagine\\Site\\SujetConfidentialite::effacer(' + b08.php(known) + '));')
        remaining = b08.wp('echo wp_json_encode([Imagine\\Site\\Sujet::ids(' + b08.php(known) + '),Imagine\\Site\\Sujet::ids("b08-inconnu@example.org")]);')
        checks['effacement_cible_sans_tiers'] = erased['items_removed'] and erased['done'] and remaining == [[], stored['b']]
        observations = b08.wp('echo wp_json_encode(get_option("imagine_b08_observations"));')
        checks['aucun_envoi_B08_observe'] = not any(k.startswith('b08_') and v for k, v in (observations.items() if isinstance(observations, dict) else []))
        outcome.update(observations=observations, labels=labels)
        assert all(checks.values()), checks
    finally:
        raw = private_path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == durable['sha256']
        saved = json.loads(raw)['payload']['database']
        # Retirer uniquement les nouvelles propositions du type neuf, vide au départ.
        b08.wp('''foreach(get_posts(['post_type'=>'imagine_sujet','post_status'=>'any','numberposts'=>-1]) as $p){wp_delete_post($p->ID,true);}delete_option('imagine_b08_observations');echo wp_json_encode(true);''')
        old_option = next((r for r in saved['options'] if r['option_name'] == 'imagine_soutenir'), None)
        if old_option:
            b08.wp('global $wpdb;$wpdb->replace($wpdb->options,' + b08.php(old_option) + ');wp_cache_delete("imagine_soutenir","options");echo wp_json_encode(true);')
        else:
            b08.wp('delete_option("imagine_soutenir");echo wp_json_encode(true);')
        if auth:
            uid = int(auth['id'])
            rows = [r for r in saved['usermeta'] if int(r['user_id']) == uid]
            b08.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["user_id"=>' + str(uid) + ']);foreach(' + b08.php(rows) + ' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete(' + str(uid) + ',"user_meta");echo wp_json_encode(true);')
        code = 'import pathlib,json;p=pathlib.Path("/app/sites/imagine-test-demo/wp-content/mu-plugins/b08-observer.php");p.unlink();print(json.dumps(not p.exists()))'
        result = subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',code], capture_output=True, encoding='utf-8')
        assert result.returncode == 0 and json.loads(result.stdout) is True
        current = b08.snapshot()
        exact = {k: current[k] == saved[k] for k in ['users','usermeta','posts','postmeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta','navigation']}
        business_options = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] == 'cron']
        exact['business_options'] = business_options(current) == business_options(saved)
        state_equal = before == b08.c25.b06.state()
        outcome.update(checks=checks, private_snapshot=durable, exact_restoration=exact, business_preserved=state_equal, observer_removed=True)
        b08.save(label, outcome)
        print(json.dumps({'checks': checks, 'restoration': exact, 'business_preserved': state_equal}, ensure_ascii=False))
        assert all(exact.values()) and state_equal, 'Restauration non prouvée'


if __name__ == '__main__':
    run(sys.argv[1])
