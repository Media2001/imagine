"""Recette C28 native/HTTP, sans passerelle ; rétablit les profils C09 et le pack."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
from urllib.parse import urlsplit, urlencode
from playwright.sync_api import sync_playwright
import c28
import c26


def run(label):
    assert not (c28.OUT/(label+'.json')).exists()
    identity = c28.guard()
    fixture = c28.wp('echo wp_json_encode(get_option("imagine_c28_fixture"));')
    business = c28.state()
    old = c28.wp('''global $wpdb;$f=get_option('imagine_c28_fixture');$users=get_option('imagine_c09_fixture')['users'];$ids=[1,$users['V-INSCRIT'],$users['V-DEC-FIN']];$p=$f['product'];echo wp_json_encode(['users'=>$ids,'meta'=>$wpdb->get_results('SELECT * FROM '.$wpdb->usermeta.' WHERE user_id IN ('.implode(',',$ids).') ORDER BY umeta_id',ARRAY_A),'posts'=>$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID=$p OR (post_type='revision' AND post_parent=$p) ORDER BY ID",ARRAY_A),'postmeta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id=$p ORDER BY meta_id",ARRAY_A),'refund_policy'=>get_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT,null),'actions'=>$wpdb->get_col('SELECT action_id FROM '.$wpdb->prefix.'actionscheduler_actions'),'woo_sessions'=>$wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions WHERE session_key='".(int)$users['V-INSCRIT']."'",ARRAY_A)]);''')
    snap = c28.private('C28-'+label, {'old':old, 'business':business})
    c26path = c28.ROOT/'production/C-26/correction-livraison-V2-inventaire.json'
    witnesses = c26.denied_markers(json.loads(c26path.read_text(encoding='utf-8')), 'anonyme')
    assert witnesses and len(witnesses) > 10
    details = c28.wp('''$f=get_option('imagine_c28_fixture');$o=[];foreach($f['articles'] as $issue=>$id){preg_match('/CONTENU_FICTIF_RESERVE_[A-Z0-9_-]+/',get_post($id)->post_content,$m);$o[$issue]=['article'=>$id,'url'=>get_permalink($id),'marker'=>$m[0]??null,'pdf_sha256'=>hash_file('sha256',Imagine\\Site\\PdfNumero::path((int)$issue))];}echo wp_json_encode($o);''')
    assert len(details) == 4 and all(v['marker'] for v in details.values())
    observer = 'mu-plugins/c28-observer.php'
    assert c28.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+observer+'"));') is False
    checks = {}; surfaces = []; cleanup = {}; mutations = {}; network = []; observations = {}; order_id = None; refund_ids = []; error = None
    def check(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)
    try:
        c28.upload(observer, (c28.ROOT/'wp/tests/demo/c28-observer.php').read_bytes())
        check('observateur_relu', c28.hashes([observer])[observer] == hashlib.sha256((c28.ROOT/'wp/tests/demo/c28-observer.php').read_bytes()).hexdigest())
        positive = c28.wp("wp_mail('fictif@example.org','C28 fictif','Fictif');wp_remote_get('https://example.invalid/');$r=get_option('imagine_c28_observations');delete_option('imagine_c28_observations');echo wp_json_encode($r);")
        check('observateur_positif_mail_HTTP_bloques', positive == {'mail':1,'mail_blocked':1,'http':1,'http_blocked':1})
        roles = {'admin':old['users'][0], 'buyer':old['users'][1], 'third':old['users'][2]}
        auth = c28.wp('$o=[];foreach('+c28.php(roles)+''' as $key=>$id){if(!str_ends_with(get_userdata($id)->user_email,'@example.org')){throw new RuntimeException('Fictif requis');}$t=WP_Session_Tokens::get_instance($id)->create(time()+3600);$o[$key]=[LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'logged_in',$t),AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'auth',$t),SECURE_AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'secure_auth',$t)];}echo wp_json_encode($o);''')
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True, channel='msedge')
            contexts = {}
            for role in ['admin','buyer','third','anon']:
                ctx = browser.new_context()
                def route(r):
                    if urlsplit(r.request.url).netloc != urlsplit(identity['url']).netloc:
                        network.append(r.request.url)
                        r.abort()
                    else:
                        r.continue_()
                ctx.route('**/*', route)
                if role != 'anon':
                    ctx.add_cookies([{'name':k, 'value':v, 'url':identity['url']} for k,v in auth[role].items()])
                contexts[role] = ctx
            def get(role, path):
                url = path if path.startswith(identity['url']) else identity['url']+path
                r = contexts[role].request.get(url, max_redirects=0)
                return r.status, dict(r.headers), r.body()
            admin = contexts['admin'].new_page()
            def edit(ids):
                admin.goto(identity['url']+'/wp-admin/post.php?post='+str(fixture['product'])+'&action=edit')
                admin.wait_for_load_state('networkidle')
                check('champ_admin_natif_present', admin.locator('#imagine-pack-numeros').count() == 1)
                admin.locator('#imagine-pack-numeros').select_option([str(i) for i in ids])
                admin.locator('#publish').click()
                admin.wait_for_load_state('networkidle')
                actual = c28.wp('echo wp_json_encode(Imagine\\Site\\PacksThematiques::numeros(wc_get_product('+str(fixture['product'])+')));')
                check('liste_admin_relue_'+'-'.join(map(str,ids)), actual == ids)
            edit(fixture['issues'])
            page = contexts['anon'].new_page()
            response = page.goto(identity['url']+'/product/c28-pack-thematique-fictif/')
            page.wait_for_load_state('networkidle')
            check('page_pack_titre_liste_couvertures_dates_prix_bouton', response.status == 200 and page.locator('[data-imagine-pack]').count() == 1 and page.locator('[data-imagine-numero]').count() == 3 and page.locator('[data-imagine-numero] img').count() == 3 and page.locator('[data-imagine-numero] time').count() == 3 and 'fictif' in page.locator('[data-imagine-pack-prix]').inner_text() and page.locator('button[name="add-to-cart"]').count() == 1)
            check('prix_fictif_3_28', bool(re.search(r'3[.,]28', page.locator('[data-imagine-pack-prix]').inner_text())))
            check('bouton_achat_francais', page.locator('button[name="add-to-cart"]').inner_text() == 'Acheter ce pack')
            page.screenshot(path=str(c28.OUT/(label+'-pack.png')), full_page=True)
            # Le bouton suit réellement le panier natif ; aucun POST de paiement ni passerelle.
            cart_page = contexts['buyer'].new_page()
            cart_page.goto(identity['url']+'/product/c28-pack-thematique-fictif/')
            cart_page.locator('button[name="add-to-cart"]').click()
            cart_page.wait_for_load_state('networkidle')
            check('bouton_panier_natif', cart_page.locator('.woocommerce-message').count() >= 1)
            def stage(name, allowed, roles_to_test=('buyer','third','anon')):
                for role in roles_to_test:
                    for issue in [*fixture['issues'], fixture['fourth']]:
                        detail = details[str(issue)]
                        permit = role == 'buyer' and issue in allowed
                        r = get(role, detail['url'])
                        verdict = c26.c23.assess_response(r, [detail['marker']], positive=permit, expected=(200,))
                        check(name+'_article_'+role+'_'+str(issue), verdict['ok'] and bool(r[2]) and b'<main' in r[2])
                        pdf = get(role, '/?imagine_pdf='+str(issue))
                        valid = pdf[0] == 200 and hashlib.sha256(pdf[2]).hexdigest() == detail['pdf_sha256'] if permit else pdf[0] == 302 and not pdf[2].startswith(b'%PDF-')
                        check(name+'_PDF_'+role+'_'+str(issue), valid and 'no-store' in pdf[1].get('cache-control',''))
                account = get('buyer','/mon-compte/')
                check(name+'_compte_charge', account[0] == 200 and b'imagine-account' in account[2])
                native = c28.wp('wp_set_current_user('+str(roles['buyer'])+');echo wp_json_encode(array_column(Imagine\\Site\\MonCompte::donnees()["numeros"],"id"));')
                check(name+'_compte_memes_numeros', sorted(native) == sorted(allowed))
            stage('avant', [])
            made = c28.wp('''$f=get_option('imagine_c28_fixture');$o=wc_create_order(['customer_id'=>'''+str(roles['buyer'])+''','status'=>'pending','created_via'=>'admin']);$o->update_meta_data('_imagine_c28_fictif','''+c28.php(label)+''');$o->set_payment_method('');$o->set_transaction_id('');$line=$o->add_product(wc_get_product($f['product']),1);$o->calculate_totals(false);$o->save();echo wp_json_encode(['order'=>$o->get_id(),'line'=>$line,'total'=>$o->get_total(),'pending'=>!$o->is_paid()]);''')
            order_id = made['order']; line_id = made['line']
            check('commande_native_fictive_3_28_en_attente', made['total'] == '3.28' and made['pending'])
            paid = c28.wp('$o=wc_get_order('+str(order_id)+');$o->payment_complete();$o=wc_get_order($o->get_id());echo wp_json_encode(["paid"=>$o->is_paid(),"method"=>$o->get_payment_method(),"transaction"=>$o->get_transaction_id(),"snapshot"=>$o->get_item('+str(line_id)+')->get_meta(Imagine\\Site\\PacksThematiques::LIGNE)]);')
            check('paiement_fictif_sans_transport_instantane3', paid['paid'] and paid['method'] == '' and paid['transaction'] == '' and paid['snapshot']['numeros'] == fixture['issues'])
            stage('paye', fixture['issues'])
            edit([*fixture['issues'], fixture['fourth']])
            stage('ajout4', fixture['issues'])
            edit([fixture['issues'][1], fixture['issues'][2], fixture['fourth']])
            stage('retrait1', fixture['issues'])
            reread = c28.wp('echo wp_json_encode(wc_get_order('+str(order_id)+')->get_item('+str(line_id)+')->get_meta(Imagine\\Site\\PacksThematiques::LIGNE));')
            check('instantane3_relu_immuable', reread == paid['snapshot'])
            # Réglage C14 par commande puis par ligne, sans aucun mécanisme de remboursement C28.
            c28.wp('update_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT,"commande");echo wp_json_encode(true);')
            refund = c28.wp('$r=wc_create_refund(["order_id"=>'+str(order_id)+',"amount"=>"1","refund_payment"=>false,"restock_items"=>false,"reason"=>"C28 FICTIF sans transfert"]);if(is_wp_error($r)){throw new RuntimeException($r->get_error_message());}echo wp_json_encode(["id"=>$r->get_id(),"gateway"=>$r->get_refunded_payment()]);')
            refund_ids.append(refund['id'])
            check('remboursement_fictif_sans_passerelle', refund['gateway'] is False)
            stage('refund_commande', [])
            c28.wp('update_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT,"ligne");echo wp_json_encode(true);')
            stage('refund_ligne_non_ventile', fixture['issues'], ('buyer',))
            refund = c28.wp('$r=wc_create_refund(["order_id"=>'+str(order_id)+',"amount"=>"1","line_items"=>['+str(line_id)+'=>["qty"=>0,"refund_total"=>1,"refund_tax"=>[]]],"refund_payment"=>false,"restock_items"=>false]);if(is_wp_error($r)){throw new RuntimeException($r->get_error_message());}echo wp_json_encode(["id"=>$r->get_id(),"gateway"=>$r->get_refunded_payment()]);')
            refund_ids.append(refund['id'])
            stage('refund_ligne_pack', [])
            packurl = '/product/c28-pack-thematique-fictif/'
            paths = [(packurl, 'html'),('/wp-json/wc/store/v1/products/'+str(fixture['product']), 'store'),('/?rest_route=/wc/store/v1/products/'+str(fixture['product']), 'store-query'),('/?post_type=product&feed=rss2', 'feed'),('/?s=C28&post_type=product', 'search'),(packurl+'embed/', 'embed'),('/wp-json/oembed/1.0/embed?'+urlencode({'url':identity['url']+packurl}), 'oembed')]
            for path, kind in paths:
                r = get('anon', path)
                surface = bool(r[2]) and ((b'<main' in r[2] or b'wp-embed' in r[2]) if kind in ['html','search','embed'] else (b'<rss' in r[2] if kind == 'feed' else isinstance(json.loads(r[2]), (dict,list))))
                verdict = c26.c23.assess_response(r, witnesses, expected=(200,))
                check('C26_pack_'+kind, surface and verdict['ok'])
                surfaces.append({'kind':kind,'path':path,'bytes':len(r[2]),'status':r[0],'surface_present':surface,'sha256':hashlib.sha256(r[2]).hexdigest(),**verdict})
            actual = get('anon',packurl)
            control = [c26.c23.assess_response((actual[0],actual[1],actual[2]+('<!-- '+w+' -->').encode()), [w]) for w in witnesses]
            mutations['response_only'] = {'count':len(control),'detected':sum(x['leak'] and not x['ok'] for x in control)}
            check('detecteur_tous_temoins_C26', mutations['response_only']['count'] == mutations['response_only']['detected'])
            # Mutation du seul raccord C28 : liste vivante à la place de l'instantané.
            filename = 'plugins/imagine-site/PacksThematiques.php'
            original = (c28.ROOT/'wp'/filename).read_bytes()
            token = b"return PacksRegles::instantane($item->get_meta(self::LIGNE, true, 'edit'));"
            assert original.count(token) == 1
            try:
                c28.upload(filename, original.replace(token, b'return self::numeros(wc_get_product($item->get_product_id()));'))
                observed = c28.wp('echo wp_json_encode(Imagine\\Site\\PacksThematiques::instantanes([],wc_get_order('+str(order_id)+')->get_item('+str(line_id)+')));')
                mutations['live_list'] = {'observed':observed,'expected':fixture['issues']}
                check('mutation_liste_vivante_detectee', observed != fixture['issues'] and fixture['fourth'] in observed and fixture['issues'][0] not in observed)
            finally:
                c28.upload(filename, original)
                check('source_pack_restauree_relue', c28.hashes([filename])[filename] == hashlib.sha256(original).hexdigest())
            browser.close()
        observations = c28.wp('echo wp_json_encode(get_option("imagine_c28_observations",[]));')
        check('HTTP_mail_tous_bloques', observations.get('http',0) == observations.get('http_blocked',0) and observations.get('mail',0) == observations.get('mail_blocked',0) and not any(k.endswith('NOT_BLOCKED') for k in observations))
        check('aucun_tiers_public_seuls_gravatars_admin_bloques', all(urlsplit(u).netloc == 'secure.gravatar.com' for u in network))
    except Exception as exc:
        error = type(exc).__name__+': '+str(exc)
    finally:
        c28.b11.b10.b09.remove_remote([observer])
        cleanup['observer_absent'] = c28.wp('delete_option("imagine_c28_observations");echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'") && get_option("imagine_c28_observations",null)===null);')
        if order_id:
            cleanup['commandes_ephemeres_supprimees'] = c28.wp('''$ids='''+c28.php([*refund_ids,order_id])+''';foreach($ids as $id){$o=wc_get_order($id);if($o){$o->delete(true);}}echo wp_json_encode(!array_filter($ids,static fn($id)=>wc_get_order($id)));''')
        else:
            cleanup['commandes_ephemeres_supprimees'] = True
        restored = c28.wp('''global $wpdb;$old='''+c28.php(old)+''';$p='''+str(fixture['product'])+''';$all=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE ID=$p OR (post_type='revision' AND post_parent=$p)");$where=implode(',',array_map('intval',$all));$wpdb->query('START TRANSACTION');try{$wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id IN ($where)");foreach($all as $id){if(!in_array($id,array_column($old['posts'],'ID'),true)){$wpdb->delete($wpdb->posts,['ID'=>$id]);}}foreach($old['posts'] as $r){$id=$r['ID'];unset($r['ID']);$wpdb->update($wpdb->posts,$r,['ID'=>$id]);}foreach($old['postmeta'] as $r){$wpdb->insert($wpdb->postmeta,$r);}$uids=implode(',',array_map('intval',$old['users']));$wpdb->query("DELETE FROM {$wpdb->usermeta} WHERE user_id IN ($uids)");foreach($old['meta'] as $r){$wpdb->insert($wpdb->usermeta,$r);}if($old['refund_policy']===null){delete_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT);}else{update_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT,$old['refund_policy'],false);}$wpdb->query('COMMIT');}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}foreach($all as $id){clean_post_cache((int)$id);}foreach($old['users'] as $id){clean_user_cache((int)$id);}wc_delete_product_transients($p);echo wp_json_encode(['meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id IN ($uids) ORDER BY umeta_id",ARRAY_A)===$old['meta'],'posts'=>$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID=$p OR (post_type='revision' AND post_parent=$p) ORDER BY ID",ARRAY_A)===$old['posts'],'postmeta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id=$p ORDER BY meta_id",ARRAY_A)===$old['postmeta'],'policy'=>get_option(Imagine\\Site\\AchatsNumeros::REMBOURSEMENT,null)===$old['refund_policy']]);''')
        cleanup.update(restored)
        schedule_cleanup = c28.wp('''global $wpdb;$old='''+c28.php(old)+''';$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';$removed=[];foreach($wpdb->get_results("SELECT * FROM $a",ARRAY_A) as $row){if(in_array($row['action_id'],$old['actions'],true)){continue;}$owned=($row['hook']==='woocommerce_run_product_attribute_lookup_update_callback'&&in_array($row['args'],['[3592,1]','[3592,2]'],true))||($row['hook']==='woocommerce_admin/stored_state_setup_for_products/async/run_remote_notifications'&&$row['args']==='[]');if($owned&&$row['status']==='pending'&&$row['attempts']==='0'){$removed[]=(int)$row['action_id'];$wpdb->delete($l,['action_id'=>$row['action_id']]);$wpdb->delete($a,['action_id'=>$row['action_id']]);}}$s=$wpdb->prefix.'woocommerce_sessions';$key=(string)$old['users'][1];$wpdb->delete($s,['session_key'=>$key]);foreach($old['woo_sessions'] as $r){$wpdb->insert($s,$r);}echo wp_json_encode(['removed_exact_test_actions'=>$removed,'woo_sessions_restored'=>$wpdb->get_results($wpdb->prepare("SELECT * FROM $s WHERE session_key=%s",$key),ARRAY_A)===$old['woo_sessions']]);''')
        cleanup['woo_sessions_restored'] = schedule_cleanup['woo_sessions_restored']
        after = c28.state()
        cleanup['business_preserved'] = after == business
        c28.save(label+'-nettoyage', {'checks':cleanup,'before':business,'after':after})
        c28.save(label, {'identity':identity,'checks':checks,'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'cleanup':cleanup,'surfaces':surfaces,'mutations':mutations,'network_blocked':network,'server_observations':observations,'C26':{'file':str(c26path.relative_to(c28.ROOT)),'sha256':hashlib.sha256(c26path.read_bytes()).hexdigest(),'witnesses':len(witnesses)},'private_snapshot':snap,'sources':c28.sources()})
    print(json.dumps({'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'cleanup':cleanup}, ensure_ascii=False))
    assert error is None and all(checks.values()) and all(cleanup.values()), error


if __name__ == '__main__':
    run(sys.argv[1])
