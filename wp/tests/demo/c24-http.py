"""C24 : vrais formulaires C10/Mon compte, navigation Chromium et inverses ciblés."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, subprocess, os, uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c24
wp, php = c24.wp, c24.php_json
CAT='imagine_personnalisation_questions'
META='imagine_personnalisation_reponses'
CONS='imagine_personnalisation_consentement'
BASE='http://192.168.129.32:8085'

def snapshot(ids):
    return wp('''global $wpdb;$ids='''+php(ids)+''';$list=implode(',',array_map('intval',$ids));$out=[
'users'=>$wpdb->get_results("SELECT * FROM {$wpdb->users} WHERE ID IN ($list) ORDER BY ID",ARRAY_A),
'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id IN ($list) ORDER BY umeta_id",ARRAY_A),
'other_meta'=>hash('sha256',serialize($wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id NOT IN ($list) ORDER BY umeta_id",ARRAY_A))),
'options'=>$wpdb->get_results("SELECT * FROM {$wpdb->options} ORDER BY option_id",ARRAY_A),
'actions'=>[]];foreach(['actionscheduler_actions','actionscheduler_groups','actionscheduler_claims','actionscheduler_logs'] as $t){$out['actions'][$t]=hash('sha256',serialize($wpdb->get_results("SELECT * FROM {$wpdb->prefix}$t ORDER BY 1",ARRAY_A)));}
echo wp_json_encode($out);''')

def restore(before, ids, allowed_options):
    current=snapshot(ids)
    old={r['option_name']:r for r in before['options']}
    new={r['option_name']:r for r in current['options']}
    changed=[n for n in old.keys()|new.keys() if old.get(n)!=new.get(n)]
    # C10 fait aussi réserver ses anciens identifiants C22 ; le lanceur AS peut
    # rafraîchir son option-verrou sans traiter de tâche. Restaurer leurs octets observés.
    allowed=lambda n:n in allowed_options or n=='action_scheduler_lock_async-request-runner' or n.startswith(('imagine_personnalisation_reserve_','imagine_newsletters_reserve_','imagine_c24_observation_','imagine_reglages_journal_','_transient_','_site_transient_'))
    # No reset: inverses only for the exact changed keys of this owned run.
    forbidden=[n for n in changed if not allowed(n)]
    assert not forbidden,'Options non attribuables : '+','.join(forbidden)
    payload={n:old.get(n) for n in changed}
    wp('''global $wpdb;$rows='''+php(payload)+''';foreach($rows as $n=>$row){$wpdb->delete($wpdb->options,['option_name'=>$n]);if($row!==null&&$wpdb->insert($wpdb->options,$row)===false)throw new RuntimeException('Inverse option refusé');wp_cache_delete($n,'options');}wp_cache_delete('alloptions','options');wp_cache_delete('notoptions','options');
$old='''+php(before['meta'])+''';$ids='''+php(ids)+''';$list=implode(',',array_map('intval',$ids));$keep=array_column($old,'umeta_id');$extra=$keep?' AND umeta_id NOT IN ('.implode(',',array_map('intval',$keep)).')':'';
if($wpdb->query("DELETE FROM {$wpdb->usermeta} WHERE user_id IN ($list)".$extra)===false)throw new RuntimeException('Inverse méta refusé');
foreach($old as $r){$exists=$wpdb->get_var($wpdb->prepare("SELECT umeta_id FROM {$wpdb->usermeta} WHERE umeta_id=%d",$r['umeta_id']));if(($exists?$wpdb->update($wpdb->usermeta,$r,['umeta_id'=>$r['umeta_id']]):$wpdb->insert($wpdb->usermeta,$r))===false)throw new RuntimeException('Inverse ligne refusé');}
foreach($ids as $id){clean_user_cache($id);wp_cache_delete($id,'user_meta');}echo 'true';''')
    after=snapshot(ids)
    assert after==before,'Readback intégral comptes/options/actions divergent'
    return changed

def run(label):
    assert not (c24.PROOF/(label+'.json')).exists()
    identity=c24.guard()
    cache=wp('echo wp_json_encode(["external"=>(bool)wp_using_ext_object_cache(),"dropin"=>is_file(WP_CONTENT_DIR."/object-cache.php"),"cron_disabled"=>defined("DISABLE_WP_CRON")&&DISABLE_WP_CRON]);')
    assert cache=={'external':False,'dropin':False,'cron_disabled':True},cache
    fixture=wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]);')
    accounts={'reader':fixture['A-PAPIER'],'other':fixture['A-SEPA4'],'sans':fixture['A-SANSMAIL'],'admin':fixture['E-ADMIN']}
    ids=list(accounts.values())
    before=snapshot(ids);native=c24.state()
    # Snapshot durable AVANT la première session ; jamais dans le dépôt.
    scratch=Path(os.environ['TMPDIR'])/('c24-http-'+uuid.uuid4().hex)
    scratch.mkdir(mode=0o700);snapshot_path=scratch/'before.json'
    raw=json.dumps({'scope':'imagine-test-demo','baseline':'Etat recupere pris explicitement comme nouvelle reference ; snapshot historique initial perdu, jamais reconstitue.','snapshot':before,'ids':ids,'native':native},ensure_ascii=False).encode('utf-8')
    with snapshot_path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.chmod(snapshot_path,0o600)
    snapshot_sha256=hashlib.sha256(raw).hexdigest()
    assert hashlib.sha256(snapshot_path.read_bytes()).hexdigest()==snapshot_sha256
    assert json.loads(snapshot_path.read_bytes())['snapshot']==before
    account_path=wp('echo wp_json_encode(wp_parse_url(wc_get_page_permalink("myaccount"),PHP_URL_PATH));')
    old_catalogue=wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());')
    assert len(old_catalogue)==4
    observer='mu-plugins/imagine-c24-observer.php';assert c24.hashes([observer])[observer] is None
    observer_source=c24.ROOT/'wp/tests/demo/c24-observer.php'
    expected=hashlib.sha256(observer_source.read_bytes()).hexdigest()
    c24.profils.b00.upload(observer,observer_source.read_bytes());assert c24.hashes([observer])[observer]==expected
    checks={};blocked=[];observations=[];allowed_options=[CAT];error=None;restored=False
    fifth='cinquieme-c24-'+hashlib.sha256(label.encode()).hexdigest()[:10]
    choice='choix-'+fifth
    def responses(uid): return wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::reponses('+str(uid)+'));')
    def consent(uid): return wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::consentement('+str(uid)+'));')
    def outgoing(uid): return wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::attributsConnecteur('+str(uid)+'));')
    def visit(page,path):
        r=page.goto(BASE+path,wait_until='networkidle');assert r.status==200,(path,r.status)
        return r
    def submit(page,mode):
        with page.expect_navigation(wait_until='networkidle'):
            page.locator('#ma-personnalisation form[data-personnalisation-mode='+mode+'] button').click()
    try:
        sessions=wp('''$out=[];foreach('''+php(accounts)+''' as $key=>$id){$expiration=time()+3600;$token=WP_Session_Tokens::get_instance($id)->create($expiration);$logged=wp_generate_auth_cookie($id,$expiration,'logged_in',$token);$auth=wp_generate_auth_cookie($id,$expiration,'auth',$token);$out[$key]=LOGGED_IN_COOKIE.'='.$logged.'; '.AUTH_COOKIE.'='.$auth.'; tk_ai='.bin2hex(random_bytes(16));}echo wp_json_encode($out);''')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            def context(key=None):
                ctx=browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE',extra_http_headers={'X-Imagine-C24':'recette-fictive'})
                def route(r):
                    if r.request.url.startswith(BASE+'/'):r.continue_()
                    else:blocked.append(r.request.url.split('?')[0]);r.abort()
                ctx.route('**/*',route)
                if key:
                    ctx.add_cookies([{'name':v.split('=',1)[0],'value':v.split('=',1)[1],'url':BASE} for v in sessions[key].split('; ')])
                return ctx
            try:
                reader=context('reader');page=reader.new_page();r=visit(page,account_path)
                checks['compte_no_store']='no-store' in r.headers.get('cache-control','')
                checks['quatre_questions_fictives']=page.locator('#ma-personnalisation fieldset[data-question]').count()==4
                checks['pas_de_champ_libre_ni_obligation']=page.locator('#ma-personnalisation input[type=text], #ma-personnalisation textarea, #ma-personnalisation [required]').count()==0
                checks['consentement_separe_initial_non_coche']=page.locator('#ma-personnalisation form').count()==3 and not page.locator('#ma-personnalisation input[name=consentement]').is_checked()
                page.locator('#ma-personnalisation input[value=reveur-fictif]').check()
                page.locator('#ma-personnalisation input[value=jardins-lunaires-fictifs]').check()
                page.locator('#ma-personnalisation input[value=cerfs-volants-fictifs]').check()
                submit(page,'reponses');on=responses(accounts['reader'])
                checks['reponses_persistantes_datees']=on['situation-fictive']['choix']==['reveur-fictif'] and len(on['situation-fictive']['date_utc'])==20 and len(on['interets-fictifs']['choix'])==2
                checks['sans_consentement_etiquettes_locales']=consent(accounts['reader'])==[] and outgoing(accounts['reader'])==[]
                page.reload(wait_until='networkidle')
                checks['rechargement_reponses_dates']=page.locator('#ma-personnalisation input[value=reveur-fictif]').is_checked() and page.locator('#ma-personnalisation time').count()==2
                fields=page.locator('#ma-personnalisation form[data-personnalisation-mode=reponses]').evaluate('(f)=>Object.fromEntries(new FormData(f))')
                other=responses(accounts['other']);fields['compte']=str(accounts['other'])
                checks['tiers_HTTP403_sans_effet']=reader.request.post(BASE+'/wp-admin/admin-post.php',form=fields).status==403 and responses(accounts['other'])==other and responses(accounts['reader'])==on
                fields['compte']=str(accounts['reader']);fields['_wpnonce']='faux'
                checks['nonce_HTTP403_sans_effet']=reader.request.post(BASE+'/wp-admin/admin-post.php',form=fields).status==403 and responses(accounts['reader'])==on
                page.locator('#ma-personnalisation input[name=consentement]').check();submit(page,'consentement')
                given=consent(accounts['reader'])
                checks['consentement_donne_date_separe']=given['accord'] is True and len(given['date_utc'])==20 and responses(accounts['reader'])==on
                checks['consentement_seul_newsletter_absente_ferme']=outgoing(accounts['reader'])==[]
                page.locator('#mes-newsletters input[value=lettre-fictive]').check()
                with page.expect_navigation(wait_until='networkidle'):page.locator('#mes-newsletters button').click()
                checks['conjonction_newsletter_et_consentement']=outgoing(accounts['reader'])==on
                page.locator('#ma-personnalisation input[name=consentement]').uncheck();submit(page,'consentement')
                checks['retrait_consentement_garde_etiquettes']=consent(accounts['reader'])['accord'] is False and responses(accounts['reader'])==on and outgoing(accounts['reader'])==[]
                page.locator('#ma-personnalisation input[value=explorateur-fictif]').check();submit(page,'reponses')
                checks['modifier_recharger']=responses(accounts['reader'])['situation-fictive']['choix']==['explorateur-fictif'] and page.locator('#ma-personnalisation input[value=explorateur-fictif]').is_checked()
                page.screenshot(path=str(c24.PROOF/(label+'-compte.png')),full_page=True)
                submit(page,'effacer');page.reload(wait_until='networkidle')
                checks['effacer_recharger_sans_consentement_perdu']=responses(accounts['reader'])==[] and consent(accounts['reader'])['accord'] is False and page.locator('#ma-personnalisation time').count()==1
                sans=context('sans');sp=sans.new_page();visit(sp,account_path)
                checks['sansmail_questions_sans_case']=sp.locator('#ma-personnalisation fieldset').count()==4 and sp.locator('#ma-personnalisation input[name=consentement]').count()==0 and sp.locator('[data-personnalisation-sans-email]').count()==1
                sp.locator('#ma-personnalisation input[value=reveur-fictif]').check();submit(sp,'reponses')
                checks['sansmail_peut_repondre_sans_envoi']=responses(accounts['sans'])['situation-fictive']['choix']==['reveur-fictif'] and outgoing(accounts['sans'])==[]
                sp.screenshot(path=str(c24.PROOF/(label+'-sans-email.png')),full_page=True)
                anonymous=context();ap=anonymous.new_page();visit(ap,account_path)
                checks['anonyme_pas_de_reponses']=ap.locator('#ma-personnalisation').count()==0 and ap.locator('form.woocommerce-form-login').count()==1
                checks['anonyme_POST403']=anonymous.request.post(BASE+'/wp-admin/admin-post.php',form=fields).status==403
                admin=context('admin');adm=admin.new_page();visit(adm,'/wp-admin/admin.php?page=imagine-reglages')
                form=adm.locator('form[action="options.php"]')
                checks['C10_meme_formulaire_nonce_unique']=form.locator('#imagine-personnalisation-reglages').count()==1 and form.locator('input[name=_wpnonce]').count()==1
                checks['C10_insertion_sous_bouton_existante']=form.evaluate('(f)=>{let b=f.querySelector("[type=submit]"),s=f.querySelector("#imagine-personnalisation-reglages");return !!(b&&s&&(b.compareDocumentPosition(s)&Node.DOCUMENT_POSITION_FOLLOWING));}')
                allowed_options=form.locator('[name]').evaluate_all('(xs)=>[...new Set(xs.map(x=>x.name.split("[")[0]).filter(n=>n.startsWith("imagine_")))]')
                for key,value in {'id':fifth,'titre':'Cinquième question entièrement fictive','choix':json.dumps([{'id':choice,'titre':'Cinquième choix entièrement fictif'}],ensure_ascii=False)}.items():
                    adm.locator('#imagine-personnalisation-4-'+key).fill(value)
                with adm.expect_navigation(wait_until='networkidle'):form.evaluate('(f)=>f.requestSubmit()')
                checks['C10_ajout_cinquieme_persistant']=len(wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());'))==5
                visit(page,account_path)
                checks['cinquieme_rendue_par_reglage']=page.locator('#ma-personnalisation [data-question='+fifth+']').count()==1
                page.locator('#ma-personnalisation input[value='+choice+']').check();submit(page,'reponses')
                fifth_history=responses(accounts['reader'])[fifth]
                checks['cinquieme_reponse_datee']=fifth_history['choix']==[choice] and len(fifth_history['date_utc'])==20
                adm.locator('#imagine-personnalisation-4-id').fill('')
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                visit(page,account_path)
                checks['retiree_absente_historique_non_reattribue']=page.locator('#ma-personnalisation fieldset').count()==4 and page.locator('#ma-personnalisation [data-question='+fifth+']').count()==0 and responses(accounts['reader'])[fifth]==fifth_history
                for key,value in {'id':fifth,'titre':'Recyclage interdit','choix':json.dumps([{'id':choice,'titre':'Réaffectation interdite'}])}.items():adm.locator('#imagine-personnalisation-4-'+key).fill(value)
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                checks['C10_question_recyclee_refusee']=adm.locator('#setting-error-imagine_personnalisation_invalide').count()==1 and len(wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());'))==4
                # Reuse only a choice ID under an active question: equally forbidden.
                choices=json.loads(adm.locator('#imagine-personnalisation-0-choix').input_value());choices.append({'id':choice,'titre':'Choix recyclé interdit'})
                adm.locator('#imagine-personnalisation-0-choix').fill(json.dumps(choices))
                with adm.expect_navigation(wait_until='networkidle'):adm.locator('form[action="options.php"]').evaluate('(f)=>f.requestSubmit()')
                checks['C10_choix_recycle_refuse']=adm.locator('#setting-error-imagine_personnalisation_invalide').count()==1 and wp('echo wp_json_encode(Imagine\\Site\\Personnalisation::catalogue());')==old_catalogue
                visit(page,account_path);submit(page,'effacer')
                checks['effacer_inclut_historique_retire']=responses(accounts['reader'])==[]
                adm.locator('#imagine-personnalisation-reglages').scroll_into_view_if_needed();adm.screenshot(path=str(c24.PROOF/(label+'-reglages.png')),full_page=True)
                checks['C10_nonce_faux_403']=admin.request.post(BASE+'/wp-admin/options.php',form={'option_page':'imagine_reglages','action':'update','_wpnonce':'faux'}).status==403
                r=reader.request.get(BASE+'/wp-admin/admin.php?page=imagine-reglages')
                checks['C10_lecteur_interdit']=r.status==403
                for ctx in [reader,sans,anonymous,admin]:ctx.close()
            finally:browser.close()
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)
    finally:
        observations=wp('''global $wpdb;$out=[];foreach($wpdb->get_results("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_c24_observation_%'",ARRAY_A) as $r){$out[]=maybe_unserialize($r['option_value']);}echo wp_json_encode($out);''')
        try:
            assert c24.hashes([observer])[observer]==expected
            p=subprocess.run(['wsl.exe','-d','Ubuntu','--','docker','exec','-i','--user','root','wp-imagine-test-demo','php'],input='<?php $p="/var/www/html/wp-content/'+observer+'";if(hash_file("sha256",$p)!=="'+expected+'")exit(3);if(!unlink($p))exit(4);echo "removed";',capture_output=True,text=True,encoding='utf-8')
            assert p.returncode==0 and p.stdout=='removed',p.stderr
            checks['instrumentation_retiree']=c24.hashes([observer])[observer] is None
        except Exception as exc:
            checks['instrumentation_retiree']=False
            error=(error or '')+'; retrait observateur : '+type(exc).__name__+': '+str(exc)
        changed=[]
        try:
            assert hashlib.sha256(snapshot_path.read_bytes()).hexdigest()==snapshot_sha256
            durable=json.loads(snapshot_path.read_bytes())
            changed=restore(durable['snapshot'],durable['ids'],allowed_options);restored=True
        except Exception as exc:
            error=(error or '')+'; restauration : '+type(exc).__name__+': '+str(exc)
        checks['comptes_sessions_options_cache_actions_exacts']=restored and snapshot(ids)==before and c24.state()==native
        # Conserver la préimage privée et son empreinte, même après succès.
        checks['snapshot_durable_relu']=hashlib.sha256(snapshot_path.read_bytes()).hexdigest()==snapshot_sha256
        checks['observation_non_vide']=len(observations)>20
        checks['aucun_mail_HTTP_tente']=bool(observations) and all(o['mail']==0 for o in observations)
        checks['HTTP_sortant_bloque']=bool(observations) and all(o['http']==o['http_blocked'] for o in observations)
        checks['aucun_HTTP_personnalisation_tente']=bool(observations) and all(o['personalisation_http']==0 for o in observations)
        checks['requete_navigateur_hors_site_bloquee']=all(u.startswith('https://secure.gravatar.com/avatar/') for u in blocked)
        failures=[k for k,v in checks.items() if v is not True]
        c24.save(label,{'private_snapshot':{'file':scratch.name+'/before.json','sha256':snapshot_sha256,'retained':True},'baseline':'recovered-new-explicit','historical_initial_snapshot_restored':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'identity':identity,'checks':checks,'total':len(checks),'failures':failures,'error':error,'restored':restored,'restored_option_names':changed,'observed_requests':len(observations),'mail_attempts':sum(o['mail'] for o in observations),'http_attempts':sum(o['http'] for o in observations),'http_blocked':sum(o['http_blocked'] for o in observations),'cache':cache,'before_digest':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'after_digest':hashlib.sha256(json.dumps(snapshot(ids),sort_keys=True).encode()).hexdigest(),'visual_approval':False})
        print(json.dumps({'total':len(checks),'failures':failures,'error':error,'restored':restored},ensure_ascii=False))
    assert not failures and error is None

if __name__=='__main__':run(sys.argv[1])
