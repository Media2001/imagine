"""C32 relevé réel HTTP + JavaScript ; aucune valeur de cookie publiée."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,re,secrets,hashlib
import c32_browser_policy as policy
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import c32 as o
import b13
if len(sys.argv) not in [2,3] or (len(sys.argv)==3 and sys.argv[2]!='--strict'):
    raise SystemExit('Usage : python -B wp/outils/demo/c32-browser.py LABEL [--strict]')
strict_mode=len(sys.argv)==3
sp=importlib.util.spec_from_file_location('c32_common',o.ROOT/'wp/outils/demo/b13-browser.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
identity=o.guard();f,markers=b.inventory()
pages=o.wp('$o=[];foreach(get_option("imagine_b09_pages") as $k=>$id){$o[$k]=["id"=>$id,"path"=>wp_make_link_relative(get_permalink($id)),"content"=>get_post($id)->post_content];}echo wp_json_encode($o);')
patterns=o.wp('echo wp_json_encode(Imagine\\Site\\Cookies::liste());')
def unknown(names):return sorted({n for n in names if not any(re.fullmatch(x['motif'],n) for x in patterns)})
def require_listed(names):
    bad=unknown(names)
    if bad:raise ValueError('Cookie hors liste: '+','.join(bad))
    return True
extension_path=o.ROOT/'production/C-26/mutations-livraison-extension.json'
extension=json.loads(extension_path.read_text(encoding='utf-8'))
paths=policy.public_paths(f,pages,extension)
before=b13.c29.state();sessions=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
native_options=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name=\'user_count\'",ARRAY_A));')
private=b13.b11.private(sys.argv[1],{'sessions':sessions,'native_options':native_options})
probe='mu-plugins/c32-observer.php';checks={};rows=[];external=[];error=None;uid=None;knownkeys=set();userlogin='fictif-c32-'+secrets.token_hex(6)
def check(n,ok):checks[n]=bool(ok);assert ok,n
session_query='global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));'
def replace_session(key,expected,previous):
    # Comparer et verrouiller avant écriture : ne jamais écraser une arrivée concurrente.
    return o.wp('global $wpdb;$key='+o.php(key)+';$expected='+o.php(expected)+';$previous='+o.php(previous)+';'
        '$wpdb->query("START TRANSACTION");try{'
        '$actual=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}woocommerce_sessions WHERE session_key=%s FOR UPDATE",$key),ARRAY_A);'
        'if($wpdb->last_error){throw new RuntimeException("Lecture session échouée");}'
        'if($actual!==$expected){$wpdb->query("ROLLBACK");echo wp_json_encode(false);return;}'
        'if($actual!==null && $wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>$key])!==1){throw new RuntimeException("Suppression session échouée");}'
        'if($previous!==null && $wpdb->insert($wpdb->prefix."woocommerce_sessions",$previous)!==1){throw new RuntimeException("Restauration session échouée");}'
        'if($wpdb->query("COMMIT")===false){throw new RuntimeException("Commit session échoué");}echo wp_json_encode(true);'
        '}catch(Throwable $e){$wpdb->query("ROLLBACK");throw $e;}')
try:
    assert o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    b13.b11.upload(probe,(o.ROOT/'wp/tests/demo/c32-observer.php').read_bytes())
    password=secrets.token_urlsafe(40)
    uid=o.wp('$u=wp_insert_user(["user_login"=>'+o.php(userlogin)+',"user_email"=>'+o.php(userlogin+'@example.org')+',"user_pass"=>'+o.php(password)+',"role"=>"subscriber"]);if(is_wp_error($u)){throw new RuntimeException("fixture refusée");}echo wp_json_encode($u);')
    product=o.wp('$p=get_posts(["post_type"=>"product","post_status"=>"publish","numberposts"=>1,"meta_key"=>"imagine_achat_numero_id"]);if(!$p){throw new RuntimeException("Produit fictif absent");}echo wp_json_encode($p[0]->ID);')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,channel='msedge')
        def context():
            ctx=browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE')
            def route(r):
                if urlsplit(r.request.url).netloc!=urlsplit(identity['url']).netloc:external.append(urlsplit(r.request.url).netloc);r.abort()
                else:r.continue_()
            ctx.route('**/*',route);return ctx
        def visit(ctx,path,kind,mutant=False):
            page=ctx.new_page();headers=[]
            def response(r):
                for h in r.headers_array():
                    if h['name'].lower()=='set-cookie':headers.append(h['value'].split('=',1)[0])
            page.on('response',response);res=page.goto(identity['url']+path,wait_until='networkidle');body=res.text();cookies=ctx.cookies()
            for c in cookies:
                if c['name'].startswith('wp_woocommerce_session_'):knownkeys.add(c['value'].split('%7C')[0].split('|')[0])
            names=sorted(set(headers+[c['name'] for c in cookies]));bad=unknown(names)
            item={'kind':kind,'path':path,'status':res.status,'header_names':sorted(set(headers)),'browser':[{k:c[k] for k in ['name','expires','httpOnly','secure','sameSite','path']} for c in cookies],'unknown':bad,'zero_cookie_expected':kind=='lecture','zero_cookie_pass':not names if kind=='lecture' else None}
            rows.append(item)
            if mutant:
                refused=False
                try:require_listed(names)
                except ValueError:refused=True
                check(kind+'_mutation_detectee',refused and bad==['c32_sonde_hors_liste'])
            else:
                check(kind+'_'+str(len(rows))+'_200',res.status==200)
                check(kind+'_'+str(len(rows))+'_liste_fermee',require_listed(names))
                check(kind+'_'+str(len(rows))+'_etanche',b.c26.c23.assess(200,body,markers)['ok'])
                if kind=='lecture':check(kind+'_'+str(len(rows))+'_ecart_natif_borne',set(names)<=policy.READING_NATIVE)
            if kind=='lecture' and path==pages['cookies']['path']:
                table=page.locator('[data-imagine-cookies]');check('page_liste_unique',table.count()==1 and table.locator('tbody tr').count()==14)
                check('page_texte_vide',pages['cookies']['content']=='')
                page.screenshot(path=str(o.OUT/(sys.argv[1]+'.png')),full_page=True)
            page.close();return names
        for path in paths:
            ctx=context();visit(ctx,path,'lecture');ctx.close()
        for path,kind,expected in [('/bienvenue/?code=fictif-affiche','code',['wp_woocommerce_session_']),('/?add-to-cart='+str(product),'panier',['wp_woocommerce_session_','woocommerce_items_in_cart','woocommerce_cart_hash']),('/wp-login.php?wp_lang=fr_FR','langue',['wp_lang','wordpress_test_cookie'])]:
            ctx=context();names=visit(ctx,path,kind);check(kind+'_cookies_natifs_observes',all(any(n.startswith(e) for n in names) for e in expected));ctx.close()
        ctx=context();page=ctx.new_page();heads=[]
        page.on('response',lambda r:heads.extend(h['value'].split('=',1)[0] for h in r.headers_array() if h['name'].lower()=='set-cookie'))
        page.goto(identity['url']+'/wp-login.php',wait_until='networkidle');page.locator('#user_login').fill(userlogin);page.locator('#user_pass').fill(password)
        with page.expect_navigation(wait_until='networkidle'):page.locator('#wp-submit').click()
        cookies=ctx.cookies();names=sorted(set(heads+[c['name'] for c in cookies]));bad=unknown(names)
        check('connexion_liste_fermee',bad==[]);check('connexion_native_reussie',any(c['name'].startswith('wordpress_logged_in_') for c in cookies) and any(re.fullmatch('wordpress_[a-f0-9]{32}',c['name']) for c in cookies))
        rows.append({'kind':'connexion','status':200,'header_names':sorted(set(heads)),'browser':[{k:c[k] for k in ['name','expires','httpOnly','secure','sameSite','path']} for c in cookies],'unknown':bad})
        for c in cookies:
            if c['name'].startswith('wp_woocommerce_session_'):knownkeys.add(c['value'].split('%7C')[0].split('|')[0])
        ctx.close()
        for typ in ['header','script']:
            ctx=context();visit(ctx,'/?c32_cookie='+typ,'mutation_'+typ,True);ctx.close()
        browser.close()
    check('aucun_tiers',not external)
except Exception as exc:error=repr(exc)
finally:
    if uid:
        o.wp('global $wpdb;$id='+str(uid)+';if(get_userdata($id)->user_login!=='+o.php(userlogin)+'){throw new RuntimeException("Compte étranger");}$wpdb->delete($wpdb->usermeta,["user_id"=>$id]);$wpdb->delete($wpdb->users,["ID"=>$id]);clean_user_cache($id);echo wp_json_encode(true);')
    o.wp('global $wpdb;$wpdb->delete($wpdb->options,["option_name"=>"user_count"]);foreach('+o.php(native_options)+' as $r){$wpdb->insert($wpdb->options,$r);}wp_cache_flush();echo wp_json_encode(true);')
    if uid:knownkeys.add(str(uid))
    try:
        session_result=policy.restore_sessions(sessions,o.wp(session_query),knownkeys,replace_session,lambda:o.wp(session_query))
    except Exception:
        error=error or 'Échec restauration sessions ; préimage privée conservée'
        session_result={'restored':False,'foreign_changes':None,'write_conflicts':None,'owned_remaining':None}
    session_ok=session_result['restored']
    b13.b11.b10.b09.remove_remote([probe]);removed=o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    after=b13.c29.state();allowed={'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero','_transient_wp_styles_for_blocks','_site_transient_timeout_wp_theme_files_patterns-55884c82b8cc78f0affc1677838a8dc8'}
    delta={k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k)!=after['option_fingerprints'].get(k)}
    restored=all(before[k]==after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta<=allowed
    reading=policy.reading_verdict(rows)
    public_coverage=policy.coverage([r['path'] for r in rows if r['kind']=='lecture'],paths)
    checks[policy.STRICT_CHECK]=reading['strict_pass']
    checks['lecture_ecart_natif_borne']=reading['inventory_pass']
    checks['couverture_publique_identique']=public_coverage['pass']
    inventory_checks=[k for k in checks if k!=policy.STRICT_CHECK]
    inventory_pass=not error and restored and session_ok and removed and all(checks[k] for k in inventory_checks)
    verdicts={'inventory':'PASS' if inventory_pass else 'FAIL','strict_zero_cookie':'PASS' if checks[policy.STRICT_CHECK] else 'FAIL'}
    public_inventory={'fixture':{k:f[k] for k in ['article_path','issue_path','term_path']}|{'posts':[{'path':x['path']} for x in f['posts']],'issues':[{'slug':x['slug']} for x in f['issues']]},'pages':{k:{'path':v['path']} for k,v in pages.items()}}
    b13.save(o,sys.argv[1],{'checks':checks,'inventory_checks':inventory_checks,'total':len(checks),'rows':rows,'error':error,'restored':restored,'sessions_restored':session_ok,'sessions_cleanup':session_result,'probe_removed':removed,'private':private,'external':external,'before':before,'after':after,'option_delta':sorted(delta),'sources':o.sources(o),'zero_cookie_reading':checks[policy.STRICT_CHECK],'reading':reading,'verdicts':verdicts,'public_coverage':public_coverage,'public_inventory':public_inventory,'c26_extension_sha256':hashlib.sha256(extension_path.read_bytes()).hexdigest()})
print({'total':len(checks),'rows':len(rows),'error':error,'restored':restored,'sessions':session_ok,'probe_removed':removed,'verdicts':verdicts})
# Inventaire autorisé et contrôle strict ont des verdicts et des sorties distincts.
assert inventory_pass and checks[policy.STRICT_CHECK]==policy.reading_verdict(rows)['strict_pass']
if strict_mode:assert checks[policy.STRICT_CHECK], 'Aucun cookie en lecture : FAIL (inventaire séparé)'
