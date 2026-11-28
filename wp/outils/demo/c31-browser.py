import sys
sys.dont_write_bytecode=True
import importlib.util
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import c31 as o
import b13
sp=importlib.util.spec_from_file_location('c31_common',o.ROOT/'wp/outils/demo/b13-browser.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
identity=o.guard();f,markers=b.inventory();before=b13.c29.state()
settings=['users_can_register','woocommerce_enable_myaccount_registration']
old=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN (\'users_can_register\',\'woocommerce_enable_myaccount_registration\')",ARRAY_A));')
sessions=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
private=b13.b11.private(sys.argv[1],{'options':old,'sessions':sessions})
probe='mu-plugins/c31-observer.php';checks={};rows=[];error=None;external=[]
def check(n,ok):checks[n]=bool(ok);assert ok,n
try:
    assert o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    b13.b11.upload(probe,(o.ROOT/'wp/tests/demo/c31-observer.php').read_bytes())
    o.wp('update_option("users_can_register",1);update_option("woocommerce_enable_myaccount_registration","yes");echo wp_json_encode(true);')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,channel='msedge');ctx=browser.new_context(java_script_enabled=False,viewport={'width':1280,'height':1000})
        def route(r):
            if urlsplit(r.request.url).netloc!=urlsplit(identity['url']).netloc:external.append(r.request.url);r.abort()
            else:r.continue_()
        ctx.route('**/*',route)
        for kind,path in [('wp','/wp-login.php?action=register'),('woo',f['account_path'])]:
            page=ctx.new_page();r=page.goto(identity['url']+path,wait_until='networkidle');check(kind+'_formulaire_200',r.status==200)
            email='fictif-c31-http-'+kind+'@JETABLE-FICTIF.example.org'
            if kind=='wp':
                form=page.locator('#registerform');check(kind+'_vrai_formulaire',form.count()==1)
                form.locator('[name="user_login"]').fill('fictif-c31-http-'+kind);form.locator('[name="user_email"]').fill(email)
                with page.expect_navigation(wait_until='networkidle') as submitted:
                    form.locator('[type="submit"]').click()
            else:
                form=page.locator('form.register');check(kind+'_vrai_formulaire',form.count()==1 and form.locator('[name="woocommerce-register-nonce"]').count()==1)
                form.locator('[name="email"]').fill(email)
                if form.locator('[name="username"]').count():form.locator('[name="username"]').fill('fictif-c31-http-'+kind)
                if form.locator('[name="password"]').count():form.locator('[name="password"]').fill('FICTIF-c31-Only-Refused-Path-9821')
                with page.expect_navigation(wait_until='networkidle') as submitted:
                    form.locator('[name="register"]').click()
            page.wait_for_load_state('networkidle');body=submitted.value.text()
            check(kind+'_message_clair','Merci d’utiliser une autre adresse email.' in page.locator('body').inner_text())
            obs=b.observation(body);rows.append({'path':path,'kind':kind,'refused':True,'observation':obs})
            if kind=='wp':
                check(kind+'_seules_traductions_natives_bloquees',obs['mail']==[] and len(obs['http'])==2 and all('translations_api' in x.get('trace',[]) for x in obs['http']))
            else:
                check(kind+'_zero_sortant',obs=={'http':[],'mail':[]})
            absent=o.wp('global $wpdb;$email='+o.php(email)+';$opt=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_value LIKE %s","%".$wpdb->esc_like($email)."%"));$meta=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE meta_value LIKE %s","%".$wpdb->esc_like($email)."%"));echo wp_json_encode(get_user_by("email",$email)===false && username_exists('+o.php('fictif-c31-http-'+kind)+')===false && $opt===0 && $meta===0 && $wpdb->last_error==="");')
            check(kind+'_aucun_compte',absent)
            check(kind+'_etanche',b.c26.c23.assess(200,body,markers)['ok'])
            check(kind+'_mutation_etanche',not b.c26.c23.assess(200,body+'<!--'+markers[0]+'-->',markers)['ok'])
            if kind=='woo':page.screenshot(path=str(o.OUT/(sys.argv[1]+'.png')),full_page=True)
            page.close()
        r=ctx.request.get(identity['url']+'/?imagine_c31_witness=1');w=b.observation(r.text());check('temoins_transport',len(w['http'])==1 and w['mail']==['blocked'] and 'wp_remote_get' in w['http'][0]['trace'])
        ctx.close();browser.close()
    check('aucun_tiers',external==[])
except Exception as exc:error=repr(exc)
finally:
    o.wp('global $wpdb;foreach('+o.php(settings)+' as $key){$wpdb->delete($wpdb->options,["option_name"=>$key]);}foreach('+o.php(old)+' as $row){$wpdb->insert($wpdb->options,$row);}wp_cache_flush();echo wp_json_encode(true);')
    current=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
    oldkeys={r['session_key'] for r in sessions};added=[r['session_key'] for r in current if r['session_key'] not in oldkeys]
    for key in added:
        assert not key.isdigit()
        o.wp('global $wpdb;$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>'+o.php(key)+']);echo wp_json_encode(true);')
    session_ok=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')==sessions
    b13.b11.b10.b09.remove_remote([probe]);removed=o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    after=b13.c29.state();allowed={'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero'}
    delta={k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k)!=after['option_fingerprints'].get(k)}
    restored=all(before[k]==after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta<=allowed
    b13.save(o,sys.argv[1],{'checks':checks,'total':len(checks),'rows':rows,'error':error,'restored':restored,'sessions_restored':session_ok,'probe_removed':removed,'private':private,'external':external,'before':before,'after':after,'sources':o.sources(o)})
print({'total':len(checks),'error':error,'restored':restored,'sessions':session_ok,'probe_removed':removed})
assert not error and restored and session_ok and removed and all(checks.values())
