"""C22 navigateur réel : sauvegarde C10, cases, refus et restauration exacte."""
from pathlib import Path
import importlib.util, json, hashlib, sys
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c22
BASE = 'http://192.168.129.32:8085'
CAT, AUTO, META = 'imagine_newsletters_catalogue','imagine_newsletters_creation','imagine_newsletters_preferences'

def rows(names):
    return c22.wp('global $wpdb;$out=[];foreach('+c22.php_json(names)+' as $n){$out[$n]=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->options} WHERE option_name=%s",$n),ARRAY_A);}echo wp_json_encode($out);')

def run(label):
    c22.profils.guard('imagine-test-demo')
    assert not (c22.PROOF/(label+'.json')).exists()
    spec = importlib.util.spec_from_file_location('c22_transport',Path(__file__).with_name('c18-http.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    h=module.transport()
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients={k:h.login(accounts[k]) for k in ['E-ADMIN','A-PAPIER','A-SEPA4','A-SANSMAIL']}
    account_path=c22.wp('echo wp_json_encode(parse_url(wc_get_page_permalink("myaccount"),PHP_URL_PATH));')
    baseline=c22.state()
    ids=c22.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]);')
    uid=ids['A-PAPIER']; other=ids['A-SEPA4']
    meta_sql='global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key=\''+META+'\' OR (meta_key=\'_woocommerce_tracks_anon_id\' AND user_id='+str(uid)+') ORDER BY umeta_id",ARRAY_A));'
    old_meta=c22.wp(meta_sql)
    checks,blocked,old,observations={},[],None,[]
    observer='mu-plugins/imagine-c22-observer.php'
    assert c22.hashes([observer])[observer] is None, 'Observer preexists'
    c22.profils.b00.upload(observer,(c22.ROOT/'wp/tests/demo/c22-observer.php').read_bytes())
    def prefs(id):
        return c22.wp('echo wp_json_encode(get_user_meta('+str(id)+',"'+META+'",true));')
    def context(browser, key=None):
        ctx=browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE',extra_http_headers={'X-Imagine-C22':'recette-fictive'})
        def route(r):
            if r.request.url.startswith(BASE+'/'):r.continue_()
            else:blocked.append(r.request.url.split('?')[0]);r.abort()
        ctx.route('**/*',route)
        if key:
            jar=next(x.cookiejar for x in clients[key].handlers if hasattr(x,'cookiejar'))
            ctx.add_cookies([{'name':c.name,'value':c.value,'domain':c.domain,'path':c.path,'secure':c.secure} for c in jar])
        return ctx
    def visit(page,path):
        r=page.goto(BASE+path,wait_until='networkidle');assert r.status==200,(path,r.status)
        return r
    def save_form(page):
        with page.expect_navigation(wait_until='networkidle'):
            page.locator('#mes-newsletters button[type=submit]').click()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            try:
                anon=context(browser); ap=anon.new_page();visit(ap,'/nos-newsletters/')
                checks['public_trois_presentations']=ap.locator('[data-newsletter]').count()==3
                checks['anonyme_emplacement_sans_formulaire']=ap.locator('#imagine-newsletters-inscription-brevo').count()==1 and ap.locator('main form').count()==0
                ap.screenshot(path=str(c22.PROOF/(label+'-nos-newsletters.png')),full_page=True)
                user=context(browser,'A-PAPIER');page=user.new_page();r=visit(page,account_path)
                checks['compte_prive_no_store']='no-store' in r.headers.get('cache-control','')
                checks['trois_cases_initiales_fermees']=page.locator('#mes-newsletters input[type=checkbox]').count()==3 and page.locator('#mes-newsletters input:checked').count()==0
                checks['pas_de_date_inventee']=page.locator('#mes-newsletters time').count()==0
                first=page.locator('#mes-newsletters input[value=lettre-fictive]');first.check();save_form(page)
                on=prefs(uid)
                checks['cocher_persistant_date']=on['lettre-fictive']['choix'] is True and on['lettre-fictive']['origine']=='lecteur' and len(on['lettre-fictive']['date_utc'])==20
                page.reload(wait_until='networkidle')
                checks['rechargement_case_et_date']=page.locator('#mes-newsletters input[value=lettre-fictive]').is_checked() and page.locator('#mes-newsletters time').count()==3
                # Genuine HTTP tampering with a valid nonce belonging to this session.
                fields=page.locator('#mes-newsletters form').evaluate('(f)=>Object.fromEntries(new FormData(f))')
                old_other=prefs(other)
                fields['compte']=str(other)
                resp=user.request.post(BASE+'/wp-admin/admin-post.php',form=fields)
                checks['autre_utilisateur_HTTP403']=resp.status==403 and prefs(other)==old_other and prefs(uid)==on
                fields['compte']=str(uid);fields['_wpnonce']='invalide'
                checks['nonce_invalide_HTTP403']=user.request.post(BASE+'/wp-admin/admin-post.php',form=fields).status==403 and prefs(uid)==on
                page.locator('#mes-newsletters input[value=lettre-fictive]').uncheck();save_form(page)
                page.reload(wait_until='networkidle')
                checks['decocher_recharger_date']=not page.locator('#mes-newsletters input[value=lettre-fictive]').is_checked() and prefs(uid)['lettre-fictive']['choix'] is False and page.locator('#mes-newsletters time').count()==3
                page.screenshot(path=str(c22.PROOF/(label+'-mes-newsletters.png')),full_page=True)
                visit(page,'/nos-newsletters/')
                link=page.get_by_role('link',name='Gérer mes newsletters')
                checks['lien_connecte_preferences']=link.count()==1 and link.get_attribute('href')==BASE+account_path+'#mes-newsletters'
                with page.expect_navigation(wait_until='networkidle'):link.click()
                checks['lien_arrive_preferences']=page.locator('#mes-newsletters').is_visible()
                sans=context(browser,'A-SANSMAIL');sp=sans.new_page();visit(sp,account_path)
                checks['sansmail_phrase_sans_rubrique']=sp.locator('#mes-newsletters').count()==0 and sp.locator('[data-imagine-newsletters-sans-email]').count()==1
                sp.screenshot(path=str(c22.PROOF/(label+'-sans-email.png')),full_page=True)
                visit(sp,'/nos-newsletters/')
                checks['sansmail_page_sans_choix']=sp.get_by_role('link',name='Gérer mes newsletters').count()==0 and sp.locator('[data-newsletter]').count()==3
                admin=context(browser,'E-ADMIN');adm=admin.new_page();visit(adm,'/wp-admin/admin.php?page=imagine-reglages')
                form=adm.locator('form[action="options.php"]')
                checks['C10_champs_meme_formulaire']=form.locator('#imagine-newsletters-reglages').count()==1 and form.locator('input[name=_wpnonce]').count()==1
                names=form.locator('[name]').evaluate_all('(xs)=>[...new Set(xs.map(x=>x.name.split("[")[0]).filter(x=>x.startsWith("imagine_")))]')
                old=rows(names)
                checks['defaut_creation_ferme']=adm.locator('#imagine-newsletters-creation').input_value()=='non'
                for key,val in {'id':'quatrieme-fictive','titre':'Quatrième newsletter fictive','presentation':'Cette quatrième lettre est temporaire.'}.items():
                    adm.locator('#imagine-newsletter-3-'+key).fill(val)
                with adm.expect_navigation(wait_until='networkidle'):form.evaluate('(f)=>f.requestSubmit()')
                checks['quatrieme_enregistree_C10']=len(c22.wp('echo wp_json_encode(get_option("'+CAT+'"));'))==4
                page.reload(wait_until='networkidle');visit(page,account_path)
                checks['quatrieme_compte_case']=page.locator('#mes-newsletters input[value=quatrieme-fictive]').count()==1
                visit(ap,'/nos-newsletters/')
                checks['quatrieme_page_publique']=ap.locator('[data-newsletter=quatrieme-fictive]').count()==1
                adm.locator('#imagine-newsletter-3-id').fill('')
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                visit(page,account_path);visit(ap,'/nos-newsletters/')
                checks['retrait_quatrieme_partout']=page.locator('#mes-newsletters input[type=checkbox]').count()==3 and ap.locator('[data-newsletter]').count()==3
                adm.locator('#imagine-newsletters-creation').select_option('oui')
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                checks['C10_creation_oui_persiste']=c22.wp('echo wp_json_encode(get_option("'+AUTO+'"));')=='oui'
                adm.locator('#imagine-newsletters-creation').select_option('non')
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                checks['C10_creation_non_persiste']=c22.wp('echo wp_json_encode(get_option("'+AUTO+'"));')=='non'
                checks['C10_ne_reinscrit_pas_existant']=prefs(uid)['lettre-fictive']['choix'] is False
                adm.locator('#imagine-newsletters-reglages').scroll_into_view_if_needed()
                adm.screenshot(path=str(c22.PROOF/(label+'-reglages-newsletters.png')),full_page=True)
                bad={'option_page':'imagine_reglages','action':'update','_wpnonce':'invalide',AUTO:'oui'}
                checks['C10_nonce_invalide_refuse']=admin.request.post(BASE+'/wp-admin/options.php',form=bad).status==403
                for ctx in [anon,user,sans,admin]:ctx.close()
            finally:browser.close()
    finally:
        # Restore exact raw rows/absences; retain native append-only C10 audit events.
        c22.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["meta_key"=>"'+META+'"]);$wpdb->delete($wpdb->usermeta,["meta_key"=>"_woocommerce_tracks_anon_id","user_id"=>'+str(uid)+']);foreach('+c22.php_json(old_meta)+' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_flush();echo "true";')
        if old is not None:
            c22.wp('global $wpdb;foreach('+c22.php_json(old)+' as $n=>$r){$wpdb->delete($wpdb->options,["option_name"=>$n]);if($r!==null)$wpdb->insert($wpdb->options,$r);}wp_cache_flush();echo "true";')
            checks['C10_restauration_lignes_et_absences']=rows(list(old))==old
        observations=c22.wp('global $wpdb;$out=[];foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE \'imagine_c22_observation_%\'",ARRAY_A) as $r){$out[$r["option_name"]]=maybe_unserialize($r["option_value"]);}echo wp_json_encode($out);')
        c22.wp('global $wpdb;foreach('+c22.php_json(list(observations))+' as $n)$wpdb->delete($wpdb->options,["option_name"=>$n]);echo "true";')
        c22.remove_observer()
    checks['preferences_restaurees_octets_exacts']=c22.wp(meta_sql)==old_meta
    after=c22.state()
    checks['profils_et_action_metier_exacts']=baseline==after
    checks['requete_navigateur_hors_demo_non_transmise']=all(u.startswith('https://secure.gravatar.com/avatar/') for u in blocked)
    checks['observation_serveur_presente']=len(observations)>10
    checks['aucun_mail_tente_HTTP']=all(v['mail']==0 for v in observations.values())
    checks['aucun_transport_HTTP_sortant']=all(v['http']==v['http_blocked'] for v in observations.values())
    checks['aucun_HTTP_newsletter_tente']=all(v['newsletter_http']==0 for v in observations.values())
    checks['instrumentation_retiree']=c22.hashes([observer])[observer] is None
    failures=[k for k,v in checks.items() if v is not True]
    c22.save(label,{'checks':checks,'total':len(checks),'failures':failures,'before':baseline,'after':after,'observed_requests':len(observations),'mail_attempts':sum(v['mail'] for v in observations.values()),'http_attempts':sum(v['http'] for v in observations.values()),'http_blocked':sum(v['http_blocked'] for v in observations.values()),'outside_demo_blocked':blocked,'captures':[label+'-'+n for n in ['nos-newsletters.png','mes-newsletters.png','sans-email.png','reglages-newsletters.png']],'visual_approval':False})
    print(json.dumps({'total':len(checks),'failures':failures,'requests':len(observations)},ensure_ascii=False))
    assert not failures

if __name__=='__main__':run(sys.argv[1])
