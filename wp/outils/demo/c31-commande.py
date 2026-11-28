"""Checkout Blocks réel par HTTP : panier natif, création demandée, refus avant persistance."""
import sys
sys.dont_write_bytecode = True
import importlib.util
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
before = b13.c29.state()
sessions = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
setting = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN (\'woocommerce_enable_signup_and_login_from_checkout\',\'woocommerce_coming_soon\')",ARRAY_A));')
private = b13.b11.private(label, {'sessions':sessions, 'setting':setting})
checks, external, rows = {}, [], []
error = None
probe = 'mu-plugins/c31-observer.php'
def check(name, ok):
    checks[name] = bool(ok)
    assert ok, name
def parsed(response):
    return json.loads(response.text().split('<!-- B13_OBSERVATION ')[0])
try:
    check('sonde_absente', o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/' + probe + '"));'))
    b13.b11.upload(probe, (o.ROOT / 'wp/tests/demo/c31-observer.php').read_bytes())
    o.wp('update_option("woocommerce_enable_signup_and_login_from_checkout","yes");update_option("woocommerce_coming_soon","no");echo wp_json_encode(true);')
    product = o.wp('$ids=[];foreach(wc_get_products(["limit"=>-1,"type"=>"simple","status"=>"publish"]) as $p){if(str_starts_with($p->get_name(),"FICTIF B04") && $p->is_purchasable()){$ids[]=$p->get_id();}}echo wp_json_encode($ids);')
    check('produit_fictif_existant', len(product) == 1)
    counts = o.wp('global $wpdb;echo wp_json_encode(["users"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users}"),"orders"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_orders")]);')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel='msedge')
        ctx = browser.new_context(java_script_enabled=False, viewport={'width':1280,'height':1000})
        def route(r):
            if urlsplit(r.request.url).netloc != urlsplit(identity['url']).netloc:
                external.append(r.request.url.split('?')[0])
                r.abort()
            else:
                r.continue_()
        ctx.route('**/*', route)
        page = ctx.new_page()
        added = page.goto(identity['url'] + '/?add-to-cart=' + str(product[0]), wait_until='networkidle')
        check('vrai_ajout_panier_navigateur', added.status == 200)
        cart = ctx.request.get(identity['url'] + '/wp-json/wc/store/v1/cart')
        check('panier_store_natif_non_vide', cart.status == 200 and parsed(cart)['items_count'] == 1)
        headers = {'Nonce': cart.headers['nonce']}
        shown = page.goto(identity['url'] + '/checkout/', wait_until='networkidle')
        rows.append({'checkout_page_status':shown.status, 'checkout_page_url':page.url, 'block_count':page.locator('.wp-block-woocommerce-checkout').count(), 'body_excerpt':page.locator('main').inner_text()[:1800]})
        page.screenshot(path=str(o.OUT / (label + '.png')), full_page=True)
        check('page_checkout_reelle_200', shown.status == 200 and page.locator('.wp-block-woocommerce-checkout').count() == 1)
        check('page_etanche', b.c26.c23.assess(200, shown.text(), markers)['ok'])
        check('mutation_etanche_detectee', not b.c26.c23.assess(200, shown.text() + '<!--' + markers[0] + '-->', markers)['ok'])
        email = 'c31-refus-store-http@JETABLE-FICTIF.example.org'
        response = ctx.request.post(identity['url'] + '/wp-json/wc/store/v1/checkout', headers=headers, data={'create_account':True, 'billing_address':{'first_name':'Fictif', 'last_name':'C31', 'address_1':'1 rue fictive', 'city':'Fictif', 'postcode':'1000', 'country':'BE', 'email':email, 'phone':'020000000'}, 'payment_method':''})
        result = parsed(response)
        check('vrai_checkout_refuse_400', response.status == 400 and result['code'] == 'imagine_adresse_alternative')
        check('message_alternative', 'autre adresse email' in result['message'])
        obs = b.observation(response.text())
        check('zero_sortant', obs == {'http':[], 'mail':[]})
        rows.append({'path':'/wp-json/wc/store/v1/checkout', 'status':response.status, 'code':result['code'], 'observation':obs})
        page.screenshot(path=str(o.OUT / (label + '.png')), full_page=True)
        ctx.close()
        browser.close()
    current = o.wp('global $wpdb;echo wp_json_encode(["users"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users}"),"orders"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_orders")]);')
    check('aucun_compte_aucune_commande', current == counts)
    hits = o.wp('global $wpdb;$email=' + o.php(email) + ';$hits=[];$tables=$wpdb->get_col($wpdb->prepare("SHOW TABLES LIKE %s",$wpdb->esc_like($wpdb->prefix)."%"));foreach($tables as $table){foreach($wpdb->get_results("SHOW COLUMNS FROM `{$table}`",ARRAY_A) as $c){if(preg_match("/char|text|blob|binary|json|enum|set/i",$c["Type"])){ $count=$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM `{$table}` WHERE `".$c["Field"]."` LIKE %s","%".$wpdb->esc_like($email)."%"));if($wpdb->last_error!==""){throw new RuntimeException("SQL");}if((int)$count>0){$hits[]=$table.".".$c["Field"];}}}}echo wp_json_encode($hits);')
    check('adresse_absente_toutes_tables_apres_requete', hits == [])
    check('aucun_tiers', external == [])
except Exception as exc:
    error = repr(exc)
finally:
    o.wp('global $wpdb;foreach(["woocommerce_enable_signup_and_login_from_checkout","woocommerce_coming_soon"] as $key){$wpdb->delete($wpdb->options,["option_name"=>$key]);}foreach(' + o.php(setting) + ' as $r){$wpdb->insert($wpdb->options,$r);}$keys=' + o.php([r['session_key'] for r in sessions]) + ';foreach($wpdb->get_col("SELECT session_key FROM {$wpdb->prefix}woocommerce_sessions") as $key){if(!in_array($key,$keys,true)){$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>$key]);}}wp_cache_flush();echo wp_json_encode(true);')
    session_ok = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));') == sessions
    b13.b11.b10.b09.remove_remote([probe])
    removed = o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/' + probe + '"));')
    after = b13.c29.state()
    allowed = {'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero'}
    delta = {k for k in before['option_fingerprints'].keys() | after['option_fingerprints'].keys() if before['option_fingerprints'].get(k) != after['option_fingerprints'].get(k)}
    restored = all(before[k] == after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta <= allowed
    b13.save(o, label, {'checks':checks, 'total':len(checks), 'rows':rows, 'error':error, 'restored':restored, 'sessions_restored':session_ok, 'probe_removed':removed, 'external':external, 'before':before, 'after':after, 'private':private, 'option_delta':sorted(delta), 'sources':o.sources(o)})
print(json.dumps({'total':len(checks), 'error':error, 'restored':restored, 'sessions':session_ok, 'probe_removed':removed, 'delta':sorted(delta)}, ensure_ascii=False))
assert error is None and checks and all(checks.values()) and restored and session_ok and removed
