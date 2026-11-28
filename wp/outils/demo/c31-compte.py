"""Vrais POST natifs Mon compte, utilisateur fictif jetable, secrets en mémoire seulement."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import base64
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import c31 as o
import b13
spec = importlib.util.spec_from_file_location('c31_browser_common', o.ROOT / 'wp/outils/demo/b13-browser.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
label = sys.argv[1]
identity = o.guard()
f, markers = b.inventory()
uid = None
probe = 'mu-plugins/c31-observer.php'
checks, rows, external = {}, [], []
error = None
before = b13.c29.state()
raw = o.wp('global $wpdb;echo wp_json_encode(["options"=>$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name=\'imagine_domaines_refuses\' OR option_name LIKE \'imagine_reglages_journal_%\'",ARRAY_A),"sessions"=>$wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A)]);')
private = b13.b11.private(label, raw)
def check(name, ok):
    checks[name] = bool(ok)
    assert ok, name
def read():
    return o.wp('$u=get_userdata(' + str(uid) + ');echo wp_json_encode(["email"=>$u->user_email,"first"=>$u->first_name,"billing"=>get_user_meta($u->ID,"billing_email",true)]);')
try:
    check('sonde_initialement_absente', o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/' + probe + '"));'))
    check('compte_fictif_initialement_absent', not o.wp('echo wp_json_encode(username_exists("fictif-c31-compte-http"));'))
    b13.b11.upload(probe, (o.ROOT / 'wp/tests/demo/c31-observer.php').read_bytes())
    uid = o.wp('update_option(Imagine\\Site\\DomainesRefuses::OPTION,[],false);$id=wp_insert_user(["user_login"=>"fictif-c31-compte-http","user_email"=>"c31-existant-http@jetable-fictif.example.org","user_pass"=>wp_generate_password(48),"role"=>"customer","first_name"=>"Fictif","last_name"=>"C31"]);if(is_wp_error($id)){throw new RuntimeException("Création fictive impossible");}echo wp_json_encode($id);')
    o.wp('update_option(Imagine\\Site\\DomainesRefuses::OPTION,["jetable-fictif.example.org","temporaire-fictif.example.org","usage-unique-fictif.example.org"],false);echo wp_json_encode(true);')
    auth = o.wp('$id=' + str(uid) + ';$t=WP_Session_Tokens::get_instance($id)->create(time()+1800);echo wp_json_encode([LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+1800,"logged_in",$t)]);')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel='msedge')
        ctx = browser.new_context(java_script_enabled=False, viewport={'width':1280, 'height':1000})
        ctx.add_cookies([{'name':k, 'value':v, 'url':identity['url']} for k,v in auth.items()])
        def route(r):
            if urlsplit(r.request.url).netloc != urlsplit(identity['url']).netloc:
                external.append(r.request.url.split('?')[0])
                r.abort()
            else:
                r.continue_()
        ctx.route('**/*', route)
        page = ctx.new_page()
        for kind, email, first in [
            ('inchange', 'c31-existant-http@jetable-fictif.example.org', 'Fictif témoin inchangé'),
            ('refuse', 'c31-changement-http@jetable-fictif.example.org', 'C31 écriture interdite'),
            ('autorise', 'c31-changement-http@example.org', 'Fictif changement autorisé'),
        ]:
            r = page.goto(identity['url'] + f['account_path'].rstrip('/') + '/edit-account/', wait_until='networkidle')
            check(kind + '_formulaire_200', r.status == 200)
            form = page.locator('form.woocommerce-EditAccountForm')
            check(kind + '_formulaire_natif_nonce', form.count() == 1 and form.locator('[name="save-account-details-nonce"]').count() == 1)
            form.locator('[name="account_first_name"]').fill(first)
            form.locator('[name="account_last_name"]').fill('C31 fictif')
            form.locator('[name="account_display_name"]').fill('Lecteur fictif C31')
            form.locator('[name="account_email"]').fill(email)
            with page.expect_response(lambda response: response.request.method == 'POST') as posted:
                with page.expect_navigation(wait_until='networkidle'):
                    form.locator('[name="save_account_details"]').click()
            response = posted.value
            body = page.content()
            obs = json.loads(base64.b64decode(response.headers['x-c31-observation'])) if response.status == 302 else b.observation(response.text())
            actual = read()
            if kind == 'refuse':
                check(kind + '_message_alternative', 'Merci d’utiliser une autre adresse email.' in page.locator('body').inner_text())
                check(kind + '_email_non_ecrit', actual['email'] == 'c31-existant-http@jetable-fictif.example.org')
                check(kind + '_temoin_sauvegarde_bloquee', actual['first'] == 'Fictif témoin inchangé')
                check(kind + '_zero_sortant', obs == {'http':[], 'mail':[]})
            else:
                check(kind + '_vraie_redirection_succes', response.status == 302)
                check(kind + '_email_relu', actual['email'] == email)
                check(kind + '_temoin_sauvegarde_effective', actual['first'] == first)
                check(kind + '_aucun_http', obs['http'] == [])
                if kind == 'autorise':
                    check(kind + '_billing_email_relu', actual['billing'] == email)
            check(kind + '_etanche', b.c26.c23.assess(200, body, markers)['ok'])
            check(kind + '_mutation_etanche_detectee', not b.c26.c23.assess(200, body + '<!--' + markers[0] + '-->', markers)['ok'])
            rows.append({'kind':kind, 'post_status':response.status, 'native_readback':actual, 'observation':obs})
            page.screenshot(path=str(o.OUT / (label + '-' + kind + '.png')), full_page=True)
        ctx.close()
        browser.close()
    absent = o.wp('global $wpdb;$email="c31-changement-http@jetable-fictif.example.org";$hits=[];$tables=$wpdb->get_col($wpdb->prepare("SHOW TABLES LIKE %s",$wpdb->esc_like($wpdb->prefix)."%"));foreach($tables as $table){foreach($wpdb->get_results("SHOW COLUMNS FROM `{$table}`",ARRAY_A) as $c){if(preg_match("/char|text|blob|binary|json|enum|set/i",$c["Type"])){ $count=$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM `{$table}` WHERE `".$c["Field"]."` LIKE %s","%".$wpdb->esc_like($email)."%"));if($wpdb->last_error!==""){throw new RuntimeException("SQL");}if((int)$count>0){$hits[]=$table.".".$c["Field"];}}}}echo wp_json_encode($hits);')
    check('refuse_absent_toutes_tables', absent == [])
    check('aucun_tiers', external == [])
except Exception as exc:
    error = repr(exc)
finally:
    # Ne supprimer que le compte créé ici ; C21 n'est pas exercé par cette recette.
    if uid:
        o.wp('global $wpdb;$id=' + str(uid) + ';$wpdb->delete($wpdb->usermeta,["user_id"=>$id]);$wpdb->delete($wpdb->users,["ID"=>$id]);$wpdb->delete($wpdb->prefix."wc_customer_lookup",["user_id"=>$id]);clean_user_cache($id);echo wp_json_encode(get_userdata($id)===false);')
    # Ne réécrire que la liste C31 et retirer ses nouveaux journaux ; ancien historique intact.
    maximum = max(int(r['option_id']) for r in raw['options'])
    old_list = [r for r in raw['options'] if r['option_name'] == 'imagine_domaines_refuses']
    (o.OUT / (label + '-progress.json')).write_text(json.dumps({'checks':checks, 'rows':rows, 'error':error}, ensure_ascii=False, indent=2), encoding='utf-8')
    restore_code = """global $wpdb;$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%' AND option_id>MAXIMUM");$wpdb->delete($wpdb->options,["option_name"=>"imagine_domaines_refuses"]);foreach(OLDLIST as $r){$wpdb->insert($wpdb->options,$r);} $keys=OLDKEYS;foreach($wpdb->get_col("SELECT session_key FROM {$wpdb->prefix}woocommerce_sessions") as $key){if(!in_array($key,$keys,true)){$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>$key]);}}wp_cache_flush();echo wp_json_encode(true);"""
    o.wp(restore_code.replace('MAXIMUM', str(maximum)).replace('OLDLIST', o.php(old_list)).replace('OLDKEYS', o.php([r['session_key'] for r in raw['sessions']])))
    b13.b11.b10.b09.remove_remote([probe])
    removed = o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/' + probe + '"));')
    sessions_ok = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));') == raw['sessions']
    after = b13.c29.state()
    allowed = {'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero','_transient_wp_styles_for_blocks'}
    delta = {k for k in before['option_fingerprints'].keys() | after['option_fingerprints'].keys() if before['option_fingerprints'].get(k) != after['option_fingerprints'].get(k)}
    restored = all(before[k] == after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta <= allowed
    b13.save(o, label, {'checks':checks, 'total':len(checks), 'rows':rows, 'error':error, 'restored':restored, 'sessions_restored':sessions_ok, 'probe_removed':removed, 'external':external, 'option_delta':sorted(delta), 'before':before, 'after':after, 'private':private, 'sources':o.sources(o)})
print(json.dumps({'total':len(checks), 'error':error, 'restored':restored, 'sessions':sessions_ok, 'probe_removed':removed, 'delta':sorted(delta)}, ensure_ascii=False))
assert error is None and checks and all(checks.values()) and restored and sessions_ok and removed
