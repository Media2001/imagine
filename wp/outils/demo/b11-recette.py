"""B11 : formulaires natifs, HTTP/navigateur, témoins C26 sans changer sa matrice."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
import time
from urllib.parse import urlsplit, urlencode
from playwright.sync_api import sync_playwright
import b11
import c26

VIDEO='https://video-fictive.example.invalid/B11_VIDEO_FICTIVE?a=1&b=2'
PODCAST='https://podcast-fictif.example.invalid/B11_PODCAST_FICTIF'
BODY='CONTENU_FICTIF_RESERVE_B11_VIDEO_PODCAST'


def persisted(actual, expected):
    return set(actual)==set(expected) and all(actual[k]==v for k,v in expected.items())


def forbidden_external(event):
    origin=urlsplit(event['origin'])
    return not (event['context']=='admin' and origin.path.startswith('/wp-admin/')
                and urlsplit(event['url']).netloc=='secure.gravatar.com')


def remove_probes(names):
    assert set(names)<= {'mu-plugins/b11-observer.php','mu-plugins/b11-no-persist.php'}
    import subprocess
    code='import pathlib,json;root=pathlib.Path("/app/sites/imagine-test-demo/wp-content");names='+repr(names)+';[(root/n).unlink(missing_ok=True) for n in names];print(json.dumps(all(not (root/n).exists() for n in names)))'
    p=subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',code],capture_output=True,encoding='utf-8')
    assert p.returncode==0 and json.loads(p.stdout) is True
    assert b11.wp('$ok=true;foreach('+b11.php(names)+' as $n){$ok=$ok&&!file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($ok);')


def restore_options(rows):
    def fingerprint():
        return b11.wp('''global $wpdb;$o=[];foreach($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name LIKE 'imagine_%' ORDER BY option_id",ARRAY_A) as $r){$r['option_value']=hash('sha256',$r['option_value']);$o[$r['option_name']]=$r;}echo wp_json_encode($o);''')
    expected={r['option_name']:{**r,'option_value':hashlib.sha256(r['option_value'].encode()).hexdigest()} for r in rows}
    actual=fingerprint()
    for name in set(actual)-set(expected):
        b11.wp('delete_option('+b11.php(name)+');echo wp_json_encode(true);')
    for r in rows:
        if actual.get(r['option_name'])!=expected[r['option_name']]:
            b11.wp('global $wpdb;$r='+b11.php(r)+';$wpdb->replace($wpdb->options,$r);wp_cache_flush();echo wp_json_encode(true);')
    return fingerprint()==expected


def run(label):
    assert not (b11.OUT/(label+'.json')).exists()
    identity=b11.guard();business=b11.state();fixture=b11.wp('echo wp_json_encode(get_option("imagine_b11_fixture"));')
    settings0=b11.wp('echo wp_json_encode(get_option("imagine_medias",null));')
    observer='mu-plugins/b11-observer.php'
    mutant='mu-plugins/b11-no-persist.php'
    assert b11.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+observer+'"));') is False
    assert b11.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+mutant+'"));') is False
    saved=b11.wp('''global $wpdb;$users=get_option('imagine_c09_fixture')['users'];$out=[];foreach(['admin'=>get_users(['role'=>'administrator','number'=>1])[0]->ID,'active'=>$users['A-CARTE'],'buyer'=>$users['P-NUMERO'],'reader'=>$users['V-INSCRIT'],'expired'=>$users['A-EXPIRE'],'suspended'=>$users['A-SUSP']] as $key=>$id){$u=get_userdata($id);if(!$u||!str_ends_with($u->user_email,'@example.org')){throw new RuntimeException('Fictif requis');}$out[$key]=['id'=>$id,'rows'=>$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key='session_tokens'",$id),ARRAY_A)];}echo wp_json_encode($out);''')
    owned=b11.wp('''global $wpdb;$ids=['''+str(fixture['issue'])+','+str(fixture['article'])+'''];$where=implode(',',array_map('intval',$ids));$posts=$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN ($where) OR (post_type='revision' AND post_parent IN ($where)) ORDER BY ID",ARRAY_A);$all=implode(',',array_map('intval',array_column($posts,'ID')));echo wp_json_encode(['posts'=>$posts,'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ($all) ORDER BY meta_id",ARRAY_A),'admin'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id=1 ORDER BY umeta_id",ARRAY_A)]);''')
    durable=b11.private(label,{'sessions':saved,'settings':settings0,'business':business,'owned':owned})
    hashes=b11.b10.b09.b08.c25.b06.hashes(b11.FILES)
    baseline_meta=b11.wp('$o=[];foreach('+b11.php([fixture['issue'],fixture['article']])+' as $id){$o[$id]=[get_post_meta($id,Imagine\\Site\\Medias::VIDEO,true),get_post_meta($id,Imagine\\Site\\Medias::PODCAST,true)];}echo wp_json_encode($o);')
    c26path=b11.ROOT/'production/C-26/correction-livraison-V2-inventaire.json'
    c26fixture=json.loads(c26path.read_text(encoding='utf-8'))
    # Liste complète livrée C26, jamais une matrice ni un paquet rescellé.
    witnesses=c26.denied_markers(c26fixture,'anonyme')
    assert len(witnesses)>10
    checks={};network={};requests=[];external=[];auth={};surface_rows=[];mutations={};observations={};cleanup={};error=None;editors={};settings_evidence=[]
    def check(name,ok,fatal=True):
        checks[name]=bool(ok)
        if not ok and fatal:raise AssertionError(name)
    def read_options(names):
        return b11.wp('$o=[];foreach('+b11.php(names)+' as $n){$o[$n]=get_option($n,null);}echo wp_json_encode($o);')
    def metas():
        return b11.wp('$o=[];foreach('+b11.php([fixture['issue'],fixture['article']])+' as $id){$o[$id]=[get_post_meta($id,"_imagine_video",true),get_post_meta($id,"_imagine_podcast",true)];}echo wp_json_encode($o);')
    ancillary=b11.wp('''global $wpdb;echo wp_json_encode(['styles'=>$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE post_type='wp_global_styles' ORDER BY ID",ARRAY_A),'options'=>$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name LIKE 'imagine_%' ORDER BY option_id",ARRAY_A)]);''')
    b11.private(label+'-ancillary',ancillary)
    try:
        b11.upload(observer,(b11.ROOT/'wp/tests/demo/b11-observer.php').read_bytes())
        check('observateur_relu',b11.b10.b09.b08.c25.b06.hashes([observer])[observer]==hashlib.sha256((b11.ROOT/'wp/tests/demo/b11-observer.php').read_bytes()).hexdigest())
        positive=b11.wp("$_GET['b11_observe']='positive';wp_mail('fictif@example.org','Fictif','Fictif');wp_remote_get('https://example.invalid/');wp_oembed_get('https://example.invalid/');$r=get_option('imagine_b11_observations');delete_option('imagine_b11_observations');echo wp_json_encode($r);")
        check('observateur_positif_mail_HTTP_oembed',positive.get('positive_mail')==1 and positive.get('positive_http',0)>=1 and positive.get('positive_oembed')==1)
        auth=b11.wp('$o=[];foreach('+b11.php({k:v['id'] for k,v in saved.items()})+' as $k=>$id){$t=WP_Session_Tokens::get_instance($id)->create(time()+3600);$o[$k]=[LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,"logged_in",$t),AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,"auth",$t),SECURE_AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,"secure_auth",$t)];}echo wp_json_encode($o);')
        with sync_playwright() as p:
            try: browser=p.chromium.launch(headless=True)
            except Exception:browser=p.chromium.launch(headless=True,channel='msedge')
            def context(role=''):
                ctx=browser.new_context()
                ctx.set_default_timeout(20000)
                def route(r):
                    if urlsplit(r.request.url).netloc!=urlsplit(identity['url']).netloc:
                        try: origin=r.request.frame.page.url
                        except Exception: origin='unavailable'
                        external.append({'url':r.request.url,'context':role or 'anon','origin':origin,'blocked_before_transport':True});r.abort()
                    else:r.continue_()
                ctx.route('**/*',route);ctx.on('request',lambda r:requests.append(r.url))
                if role:ctx.add_cookies([{'name':k,'value':v,'url':identity['url']} for k,v in auth[role].items()])
                return ctx
            contexts={role:context(role) for role in ['admin','active','buyer','reader','expired','suspended']}
            contexts['anon']=context()
            admin=contexts['admin'];page=admin.new_page()
            def setting(value):
                page.goto(identity['url']+'/wp-admin/admin.php?page=imagine-reglages');page.wait_for_load_state('networkidle')
                check('section_reglages_natifs',page.locator('#imagine-medias-reglages').count()==1)
                page.locator('[name="imagine_medias[hosts]"]').fill('video-fictive.example.invalid')
                page.locator('[name="imagine_medias[integration]"]').select_option(value)
                form=page.locator('form').filter(has=page.locator('#imagine-medias-reglages'))
                names=form.locator('[name]').evaluate_all("es=>Array.from(new Set(es.map(e=>e.name.split('[')[0]))).filter(n=>n.startsWith('imagine_'))")
                check('formulaire_reglages_complet',len(names)>3 and 'imagine_medias' in names)
                before=read_options(names)
                page.locator('#submit').click();page.wait_for_load_state('networkidle')
                check('reglage_'+value+'_readback',b11.wp('echo wp_json_encode(Imagine\\Site\\Medias::configuration());')=={'hosts':['video-fictive.example.invalid'],'integration':value})
                after=read_options(names)
                other=[n for n in names if n!='imagine_medias']
                settings_evidence.append({'mode':value,'names':names,'others_unchanged':all(before[n]==after[n] for n in other),'changed_others':[{'name':n,'before_sha256':hashlib.sha256(json.dumps(before[n],sort_keys=True).encode()).hexdigest(),'after_sha256':hashlib.sha256(json.dumps(after[n],sort_keys=True).encode()).hexdigest()} for n in other if before[n]!=after[n]]})
                check('autres_reglages_conserves_'+value,all(before[n]==after[n] for n in other),fatal=False)
                page.reload();page.wait_for_load_state('networkidle')
                check('reglage_'+value+'_reload',page.locator('[name="imagine_medias[integration]"]').input_value()==value)
            def edit(ident,video=VIDEO,podcast=PODCAST,phase='save'):
                # Parcours livré : aucun changement d'éditeur, de formulaire ou de nonce.
                page.goto(identity['url']+'/wp-admin/post.php?post='+str(ident)+'&action=edit&b11_observe='+phase);page.wait_for_load_state('networkidle')
                box=next((f for f in page.frames if f.locator('#b11-video').count()),None)
                check('metabox_'+str(ident),box is not None and box.locator('#b11-podcast').count()==1)
                block=page.locator('.block-editor').count()>0
                editors[str(ident)]={'kind':'block' if block else 'classic','forced':False,'metabox_frame':box!=page.main_frame}
                box.locator('#b11-video').fill(video);box.locator('#b11-podcast').fill(podcast)
                if block:
                    button=page.locator('.editor-post-publish-button__button')
                    if not button.count():button=page.get_by_role('button',name=re.compile('^(Enregistrer|Mettre à jour|Save|Update)$')).first
                    button.click();page.wait_for_timeout(2500);page.wait_for_load_state('networkidle')
                else:
                    page.locator('#publish').click();page.wait_for_load_state('networkidle')
                content=page.content()
                page.reload();page.wait_for_load_state('networkidle')
                readbox=next((f for f in page.frames if f.locator('#b11-video').count()),None)
                check('champs_relus_reload_'+str(ident),readbox is not None)
                editors[str(ident)]['reload_values']=[readbox.locator('#b11-video').input_value(),readbox.locator('#b11-podcast').input_value()]
                return content
            for value in ['0','1']:
                setting(value)
                start=len(external);seen=len(requests)
                changed={str(i):[VIDEO+'&correction='+value+'-'+str(i),PODCAST+'?correction='+value+'-'+str(i)] for i in [fixture['issue'],fixture['article']]}
                check('valeurs_reellement_changees_'+value,all(all(v!=old for v,old in zip(changed[k],baseline_meta[k])) for k in changed))
                for ident in [fixture['issue'],fixture['article']]:edit(ident,*changed[str(ident)],phase='mode'+value+'-save')
                check('save_'+value+'_readback',persisted(metas(),changed) and all(editors[k]['reload_values']==v for k,v in changed.items()))
                cleared={k:['',''] for k in changed}
                for ident in [fixture['issue'],fixture['article']]:edit(ident,'','',phase='clear-save')
                check('effacement_'+value+'_readback',persisted(metas(),cleared) and all(editors[k]['reload_values']==v for k,v in cleared.items()))
                for ident in [fixture['issue'],fixture['article']]:edit(ident,phase='render-save')
                check('valeurs_rendu_'+value,persisted(metas(),{k:[VIDEO,PODCAST] for k in changed}))
                pub=contexts['buyer'].new_page()
                for url,kind in [(identity['url']+'/b11-article-medias-fictifs/','article'),(identity['url']+'/numeros/demo-2026-t1/','numero')]:
                    r=pub.goto(url+'?b11_observe=mode'+value+'-render');pub.wait_for_load_state('networkidle')
                    check('rendu_'+value+'_'+kind,r.status==200 and pub.locator('[data-imagine-video]').get_attribute('href')==VIDEO and pub.locator('[data-imagine-podcast]').get_attribute('href')==PODCAST and pub.locator('[data-imagine-video-emplacement]').count()==int(value))
                    check('zero_ressource_tiers_'+value+'_'+kind,pub.locator('iframe,script[src*="example.invalid"],img[src*="example.invalid"]').count()==0)
                    if kind=='numero':
                        audio=pub.locator('[data-imagine-audio]')
                        duration=audio.evaluate("e=>new Promise((resolve,reject)=>{e.addEventListener('loadedmetadata',()=>resolve(e.duration),{once:true});e.addEventListener('error',()=>reject(Error('audio decode failed')),{once:true});e.load();})")
                        check('lecteur_natif_decode_3_secondes_'+value,duration==3 and audio.get_attribute('controls') is not None and audio.get_attribute('preload')=='none')
                network[value]={'browser_requests':requests[seen:],'external':[e for e in external[start:] if forbidden_external(e)],'all_external_attempts':external[start:]}
                check('navigateur_'+value+'_zero_tiers',not network[value]['external'] and bool(network[value]['browser_requests']))
            try:
                b11.upload(mutant,(b11.ROOT/'wp/tests/demo/b11-no-persist.php').read_bytes())
                check('mutant_non_persistance_relu',b11.b10.b09.b08.c25.b06.hashes([mutant])[mutant]==hashlib.sha256((b11.ROOT/'wp/tests/demo/b11-no-persist.php').read_bytes()).hexdigest())
                admin.set_extra_http_headers({'X-Imagine-B11-Mutation':'no-persist'})
                before=metas()
                for ident in [fixture['issue'],fixture['article']]:
                    attempted=[VIDEO+'&no-persist='+str(ident),PODCAST+'?no-persist='+str(ident)]
                    edit(ident,*attempted,phase='mutation-no-persist')
                    actual=metas()
                    expected={**before,str(ident):attempted}
                    mutations['no_persist_'+str(ident)]={'attempted':attempted,'actual':actual[str(ident)],'persistence_control_failed':not persisted(actual,expected),'reload':editors[str(ident)]['reload_values']}
                    check('mutation_non_persistance_'+str(ident)+'_rougit',not persisted(actual,expected) and actual==before and editors[str(ident)]['reload_values']==before[str(ident)])
            finally:
                admin.set_extra_http_headers({})
                remove_probes([mutant])
                check('mutant_non_persistance_absent',b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+mutant+'"));'))
            invalid=edit(fixture['article'],'https://evil.invalid/INTERDIT',phase='bad-host-save')
            check('mauvais_host_POST_natif_refuse','Médias refusés' in invalid and b11.wp('echo wp_json_encode(get_post_meta('+str(fixture['article'])+',Imagine\\Site\\Medias::VIDEO,true));')==VIDEO)
            badslash=edit(fixture['article'],VIDEO+'\\bad',phase='backslash-save')
            check('antislash_POST_refuse_sans_perte','Médias refusés' in badslash and b11.wp('echo wp_json_encode(get_post_meta('+str(fixture['article'])+',Imagine\\Site\\Medias::VIDEO,true));')==VIDEO)
            # Vrais GET binaires ; chaque demande reprend la décision C06, jamais une URL publique statique.
            def get(role,path,method='GET'):
                r=contexts[role].request.fetch(identity['url']+path,method=method,max_redirects=0)
                return r.status,dict(r.headers),r.body()
            for role,issue,allowed in [('buyer',fixture['issue'],True),('active',fixture['issue_active'],True),('active',fixture['issue'],False),('buyer',fixture['issue_active'],False),('anon',fixture['issue'],False),('reader',fixture['issue'],False),('expired',fixture['issue_active'],False),('suspended',fixture['issue_active'],False)]:
                response=get(role,'/?imagine_audio='+str(issue)+'&b11_observe=audio-render')
                ok=response[0]==200 and hashlib.sha256(response[2]).hexdigest()==fixture['silence_sha256'] if allowed else response[0]==302 and not response[2].startswith(b'RIFF') and 'imagine_audio' not in response[1].get('location','')
                check('audio_'+role+'_'+str(issue),ok)
                check('audio_headers_'+role+'_'+str(issue),'no-store' in response[1].get('cache-control','') and response[1].get('x-content-type-options')=='nosniff' and 'cookie' in response[1].get('vary','').lower())
            head=get('buyer','/?imagine_audio='+str(fixture['issue']),'HEAD')
            check('audio_HEAD',head[0]==200 and head[2]==b'' and head[1]['content-length']=='48044')
            check('audio_POST_405',get('buyer','/?imagine_audio='+str(fixture['issue']),'POST')[0]==405)
            for raw in ['0','bad','9999999','11%2F..','%5B%5D']:
                check('audio_malformed_'+raw,get('anon','/?imagine_audio='+raw)[0]==404)
            # Page inverse d'abord : liens/texte présents pour acheteur et abonné (article C06).
            for role in ['buyer','active']:
                r=get(role,'/b11-article-medias-fictifs/')
                check('temoin_article_positif_'+role,c26.c23.assess_response(r,[BODY,VIDEO,PODCAST],positive=True)['ok'] and all(w in c26.c23.canonical(r[2],raw=True) for w in [BODY,VIDEO,PODCAST]))
            paths=[('/b11-article-medias-fictifs/','html'),('/wp-json/wp/v2/posts/'+str(fixture['article']),'rest'),('/?rest_route=/wp/v2/posts/'+str(fixture['article']),'rest'),('/wp-json/wp/v2/posts?include='+str(fixture['article']),'collection'),('/?feed=rss2','feed'),('/wp-json/oembed/1.0/embed?'+urlencode({'url':identity['url']+'/b11-article-medias-fictifs/'}),'oembed'),('/b11-article-medias-fictifs/embed/','embed'),('/?s=B11&post_type=post','search')]
            for role in ['anon','reader','expired','suspended']:
                for path,kind in paths:
                    r=get(role,path)
                    surface=bool(r[2]) and ((b'<main' in r[2] or b'wp-embed' in r[2]) if kind in ['html','search','embed'] else (b'<rss' in r[2] if kind=='feed' else (isinstance(json.loads(r[2]),(dict,list)))))
                    verdict=c26.c23.assess_response(r,witnesses+[BODY,VIDEO,PODCAST,'imagine_audio='],expected=(200,))
                    check('etanche_'+role+'_'+kind,surface and verdict['ok'])
                    surface_rows.append({'role':role,'kind':kind,'path':path,'status':r[0],'bytes':len(r[2]),'sha256':hashlib.sha256(r[2]).hexdigest(),'surface_present':surface,**verdict})
            for role in ['anon','reader']:
                r=get(role,'/numeros/demo-2026-t1/')
                check('page_numero_sans_adresse_audio_'+role,b'imagine_audio=' not in r[2] and b'Sommaire audio' in r[2])
                rest=get(role,'/wp-json/wp/v2/imagine_numero/'+str(fixture['issue']))
                check('REST_numero_sans_adresse_audio_'+role,rest[0]==200 and json.loads(rest[2]).get('id')==fixture['issue'] and b'imagine_audio' not in rest[2] and b'_imagine_audio_blob' not in rest[2])
            # Mutation réelle B11 seulement : garde article ôtée, puis remise et relue.
            name='plugins/imagine-site/Medias.php';original=(b11.ROOT/'wp'/name).read_bytes()
            token=b"&& !Paywall::decision($post)['complet']"
            assert original.count(token)==1
            try:
                b11.upload(name,original.replace(token,b'&& false'));time.sleep(3)
                r=get('anon','/b11-article-medias-fictifs/')
                verdict=c26.c23.assess_response(r,[VIDEO,PODCAST])
                mutations['garde_article']={'status':r[0],**verdict}
                check('mutation_garde_article_tuee',verdict['leak'] and not verdict['ok'])
            finally:
                b11.upload(name,original);time.sleep(3);assert b11.b10.b09.b08.c25.b06.hashes([name])[name]==hashlib.sha256(original).hexdigest()
            check('garde_article_revenue',c26.c23.assess_response(get('anon','/b11-article-medias-fictifs/'),[VIDEO,PODCAST])['ok'])
            name='plugins/imagine-site/AudioNumero.php';original=(b11.ROOT/'wp'/name).read_bytes();token=b"if (Paywall::decisionPdf($issue)['complet'])"
            assert original.count(token)==1
            try:
                b11.upload(name,original.replace(token,b'if (true)'));time.sleep(3)
                r=get('anon','/?imagine_audio='+str(fixture['issue']))
                mutations['garde_audio']={'status':r[0],'bytes':len(r[2]),'binary_sha256':hashlib.sha256(r[2]).hexdigest()}
                check('mutation_garde_audio_tuee',r[0]==200 and hashlib.sha256(r[2]).hexdigest()==fixture['silence_sha256'])
            finally:
                b11.upload(name,original);time.sleep(3);assert b11.b10.b09.b08.c25.b06.hashes([name])[name]==hashlib.sha256(original).hexdigest()
            check('garde_audio_revenue',get('anon','/?imagine_audio='+str(fixture['issue']))[0]==302)
            # Chaque témoin C26 est détecté dans la réponse B11 brute, commentaires compris.
            actual=get('anon','/b11-article-medias-fictifs/')
            control=[]
            for witness in witnesses+[BODY,VIDEO,PODCAST,'imagine_audio=']:
                changed=(actual[0],actual[1],actual[2]+('<!-- '+witness+' -->').encode())
                v=c26.c23.assess_response(changed,[witness])
                control.append(v['leak'] and not v['ok'])
            check('mutations_detecteur_tous_temoins_C26',all(control))
            mutations['detecteur_reponse_seulement']={'count':len(control),'detected':sum(control),'not_source_mutations':True}
            a=contexts['anon'].new_page();a.goto(identity['url']+'/b11-article-medias-fictifs/')
            n=len(external);a.evaluate("fetch('https://example.invalid/b11-positive').catch(()=>{})");a.wait_for_timeout(200)
            check('observateur_navigateur_positif_bloque',len(external)==n+1 and forbidden_external(external[-1]));external.pop()
            n=len(external);a.evaluate("fetch('https://secure.gravatar.com/avatar/b11-public-witness').catch(()=>{})");a.wait_for_timeout(300)
            witness=external.pop() if len(external)==n+1 else None
            mutations['gravatar_public']={'event':witness,'zero_tiers_failed':bool(witness and forbidden_external(witness))}
            check('mutation_gravatar_public_rougit_avant_transport',bool(witness and forbidden_external(witness) and witness['blocked_before_transport']))
            setting('0')
            browser.close()
        observations=b11.wp('echo wp_json_encode(get_option("imagine_b11_observations",[]));')
        destinations=observations.get('destinations',[]) if isinstance(observations,dict) else []
        check('save_render_B11_zero_HTTP_oembed_mail',not any(d['subject_b11'] for d in destinations) and not any(v for k,v in (observations.items() if isinstance(observations,dict) else []) if k.endswith(('_oembed','_mail')) and not k.startswith('ambiance_')))
        check('tentatives_ambiance_qualifiees_bloquees_B00',all(d['ambient_novamira_update'] and d['host']=='license.dynamic.ooo' for d in destinations))
        check('toutes_tentatives_HTTP_coupees_avant_transport',all(observations.get(k.removesuffix('_http')+'_blocked',0)==v for k,v in observations.items() if k.endswith('_http')) and not any(k.endswith('_NOT_BLOCKED') for k in observations))
        check('seuls_gravatars_admin_bloques',all(not forbidden_external(e) and e['blocked_before_transport'] for e in external))
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)
    finally:
        # Les inverses sont indépendantes ; aucune session ni nonce dans les reçus publics.
        remove_probes([observer,mutant]);cleanup['observer_removed']=True
        b11.wp('delete_option("imagine_b11_observations");update_option("imagine_medias",'+b11.php(settings0)+',false);echo wp_json_encode(true);')
        cleanup['settings_restored']=b11.wp('echo wp_json_encode(get_option("imagine_medias",null));')==settings0
        for session in saved.values():
            uid=session['id'];rows=session['rows']
            b11.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["user_id"=>'+str(uid)+',"meta_key"=>"session_tokens"]);foreach('+b11.php(rows)+' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete('+str(uid)+',"user_meta");echo wp_json_encode(true);')
            actual=b11.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=\'session_tokens\'",'+str(uid)+'),ARRAY_A));')
            cleanup['session_'+str(uid)]=actual==rows
        cleanup['owned_restored']=b11.wp('''global $wpdb;$old='''+b11.php(owned)+''';$ids=['''+str(fixture['issue'])+','+str(fixture['article'])+'''];$where=implode(',',array_map('intval',$ids));$all=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE ID IN ($where) OR (post_type='revision' AND post_parent IN ($where))");$allSql=implode(',',array_map('intval',$all));$wpdb->query('START TRANSACTION');try{$wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id IN ($allSql)");$oldIds=array_column($old['posts'],'ID');foreach($all as $id){if(!in_array($id,$oldIds,true)){$wpdb->delete($wpdb->posts,['ID'=>$id]);}}foreach($old['posts'] as $r){$id=$r['ID'];unset($r['ID']);$wpdb->update($wpdb->posts,$r,['ID'=>$id]);}foreach($old['meta'] as $r){$wpdb->insert($wpdb->postmeta,$r);}$wpdb->delete($wpdb->usermeta,['user_id'=>1]);foreach($old['admin'] as $r){$wpdb->insert($wpdb->usermeta,$r);}$wpdb->query('COMMIT');}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}foreach($all as $id){clean_post_cache((int)$id);}clean_user_cache(1);echo wp_json_encode(true);''')
        cleanup['observer_absent_readback']=b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'")&&get_option("imagine_b11_observations",null)===null);')
        cleanup['owned_exact_readback']=b11.wp('''global $wpdb;$ids=['''+str(fixture['issue'])+','+str(fixture['article'])+'''];$where=implode(',',array_map('intval',$ids));$posts=$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN ($where) OR (post_type='revision' AND post_parent IN ($where)) ORDER BY ID",ARRAY_A);$all=implode(',',array_map('intval',array_column($posts,'ID')));echo wp_json_encode(['posts'=>$posts,'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ($all) ORDER BY meta_id",ARRAY_A),'admin'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id=1 ORDER BY umeta_id",ARRAY_A)]);''')==owned
        cleanup['global_styles_restored']=b11.wp('''global $wpdb;$old='''+b11.php(ancillary['styles'])+''';$ids=array_column($old,'ID');foreach($wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE post_type='wp_global_styles'",ARRAY_A) as $r){if(!in_array($r['ID'],$ids,true)){if($r['post_name']!=='wp-global-styles-imagine'){throw new RuntimeException('Style tiers inattendu');}wp_delete_post((int)$r['ID'],true);}}echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE post_type='wp_global_styles' ORDER BY ID",ARRAY_A)===$old);''')
        # Exactes lignes des options du groupe livré, même en cas de normalisation hors B11.
        cleanup['options_restored']=restore_options(ancillary['options'])
        cleanup['mutant_absent_readback']=b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+mutant+'"));')
        cleanup['sources_restored']=b11.b10.b09.b08.c25.b06.hashes(b11.FILES)==hashes
        cleanup['business_preserved']=b11.state()==business
        b11.save(label+'-details',{'editors':editors,'settings_evidence':settings_evidence,'external_attempts':external})
        b11.save(label+'-nettoyage',cleanup)
        b11.save(label,{'identity':identity,'checks':checks,'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'network':network,'server_observations':observations,'C26_witness_inventory':{'file':str(c26path.relative_to(b11.ROOT)),'sha256':hashlib.sha256(c26path.read_bytes()).hexdigest(),'count':len(witnesses)},'surfaces':surface_rows,'mutations':mutations,'cleanup':cleanup,'sources':b11.sources(),'private_snapshot':durable})
    print(json.dumps({'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'cleanup':cleanup},ensure_ascii=False))
    assert error is None and all(checks.values()) and all(cleanup.values()),error

if __name__=='__main__':run(sys.argv[1])
