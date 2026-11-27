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


def run(label):
    assert not (b11.OUT/(label+'.json')).exists()
    identity=b11.guard();business=b11.state();fixture=b11.wp('echo wp_json_encode(get_option("imagine_b11_fixture"));')
    settings0=b11.wp('echo wp_json_encode(get_option("imagine_medias",null));')
    observer='mu-plugins/b11-observer.php'
    assert b11.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+observer+'"));') is False
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
    checks={};network={};requests=[];external=[];auth={};surface_rows=[];mutations={};observations={};cleanup={};error=None
    def check(name,ok):
        checks[name]=bool(ok)
        if not ok:raise AssertionError(name)
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
                ctx=browser.new_context(extra_http_headers={'X-Imagine-B11-Settings':'fictif'})
                def route(r):
                    if urlsplit(r.request.url).netloc!=urlsplit(identity['url']).netloc:external.append(r.request.url);r.abort()
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
                form.evaluate("e=>e.setAttribute('action','options.php?b11_observe=settings-save')")
                page.locator('#submit').click();page.wait_for_load_state('networkidle')
                check('reglage_'+value+'_readback',b11.wp('echo wp_json_encode(Imagine\\Site\\Medias::configuration());')=={'hosts':['video-fictive.example.invalid'],'integration':value})
            def edit(ident,video=VIDEO,podcast=PODCAST,phase='save'):
                page.goto(identity['url']+'/wp-admin/post.php?post='+str(ident)+'&action=edit');page.wait_for_load_state('networkidle')
                # Le formulaire classique natif et son nonce, sans fabriquer une saisie par WP-CLI.
                check('metabox_'+str(ident),page.locator('#b11-video').count()==1 and page.locator('#b11-podcast').count()==1)
                page.locator('#b11-video').fill(video);page.locator('#b11-podcast').fill(podcast)
                form=page.locator('#post');form.evaluate("(e,q)=>e.setAttribute('action',q)",identity['url']+'/wp-admin/post.php?b11_observe='+phase)
                page.locator('#publish').click();page.wait_for_load_state('networkidle')
                return page.content()
            for value in ['0','1']:
                setting(value)
                start=len(external);seen=len(requests)
                for ident in [fixture['issue'],fixture['article']]:edit(ident,phase='mode'+value+'-save')
                check('save_'+value+'_readback',b11.wp('$o=[];foreach('+b11.php([fixture['issue'],fixture['article']])+' as $id){$o[$id]=[get_post_meta($id,Imagine\\Site\\Medias::VIDEO,true),get_post_meta($id,Imagine\\Site\\Medias::PODCAST,true)];}echo wp_json_encode($o);')==baseline_meta)
                pub=contexts['buyer'].new_page()
                for url,kind in [(identity['url']+'/b11-article-medias-fictifs/','article'),(identity['url']+'/numeros/demo-2026-t1/','numero')]:
                    r=pub.goto(url+'?b11_observe=mode'+value+'-render');pub.wait_for_load_state('networkidle')
                    check('rendu_'+value+'_'+kind,r.status==200 and pub.locator('[data-imagine-video]').get_attribute('href')==VIDEO and pub.locator('[data-imagine-podcast]').get_attribute('href')==PODCAST and pub.locator('[data-imagine-video-emplacement]').count()==int(value))
                    check('zero_ressource_tiers_'+value+'_'+kind,pub.locator('iframe,script[src*="example.invalid"],img[src*="example.invalid"]').count()==0)
                network[value]={'browser_requests':requests[seen:],'external':[u for u in external[start:] if urlsplit(u).netloc!='secure.gravatar.com']}
                check('navigateur_'+value+'_zero_tiers',not network[value]['external'] and bool(network[value]['browser_requests']))
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
            check('observateur_navigateur_positif_bloque',len(external)==n+1);external.pop()
            setting('0')
            browser.close()
        observations=b11.wp('echo wp_json_encode(get_option("imagine_b11_observations",[]));')
        destinations=observations.get('destinations',[]) if isinstance(observations,dict) else []
        check('save_render_B11_zero_HTTP_oembed_mail',not any(d['subject_b11'] for d in destinations) and not any(v for k,v in (observations.items() if isinstance(observations,dict) else []) if k.endswith(('_oembed','_mail')) and not k.startswith('ambiance_')))
        check('tentatives_ambiance_qualifiees_bloquees_B00',all(d['ambient_novamira_update'] and d['host']=='license.dynamic.ooo' for d in destinations))
        check('seuls_gravatars_admin_bloques',all(urlsplit(u).netloc=='secure.gravatar.com' for u in external))
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)
    finally:
        # Les inverses sont indépendantes ; aucune session ni nonce dans les reçus publics.
        b11.b10.b09.remove_remote([observer]);cleanup['observer_removed']=True
        b11.wp('delete_option("imagine_b11_observations");update_option("imagine_medias",'+b11.php(settings0)+',false);echo wp_json_encode(true);')
        cleanup['settings_restored']=b11.wp('echo wp_json_encode(get_option("imagine_medias",null));')==settings0
        for session in saved.values():
            uid=session['id'];rows=session['rows']
            b11.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["user_id"=>'+str(uid)+',"meta_key"=>"session_tokens"]);foreach('+b11.php(rows)+' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete('+str(uid)+',"user_meta");echo wp_json_encode(true);')
            actual=b11.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=\'session_tokens\'",'+str(uid)+'),ARRAY_A));')
            cleanup['session_'+str(uid)]=actual==rows
        cleanup['owned_restored']=b11.wp('''global $wpdb;$old='''+b11.php(owned)+''';$ids=['''+str(fixture['issue'])+','+str(fixture['article'])+'''];$where=implode(',',array_map('intval',$ids));$all=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE ID IN ($where) OR (post_type='revision' AND post_parent IN ($where))");$allSql=implode(',',array_map('intval',$all));$wpdb->query('START TRANSACTION');try{$wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id IN ($allSql)");$oldIds=array_column($old['posts'],'ID');foreach($all as $id){if(!in_array($id,$oldIds,true)){$wpdb->delete($wpdb->posts,['ID'=>$id]);}}foreach($old['posts'] as $r){$id=$r['ID'];unset($r['ID']);$wpdb->update($wpdb->posts,$r,['ID'=>$id]);}foreach($old['meta'] as $r){$wpdb->insert($wpdb->postmeta,$r);}$wpdb->delete($wpdb->usermeta,['user_id'=>1]);foreach($old['admin'] as $r){$wpdb->insert($wpdb->usermeta,$r);}$wpdb->query('COMMIT');}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}foreach($all as $id){clean_post_cache((int)$id);}clean_user_cache(1);echo wp_json_encode(true);''')
        cleanup['observer_absent_readback']=b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'")&&get_option("imagine_b11_observations",null)===null);')
        cleanup['sources_restored']=b11.b10.b09.b08.c25.b06.hashes(b11.FILES)==hashes
        cleanup['business_preserved']=b11.state()==business
        b11.save(label+'-nettoyage',cleanup)
        b11.save(label,{'identity':identity,'checks':checks,'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'network':network,'server_observations':observations,'C26_witness_inventory':{'file':str(c26path.relative_to(b11.ROOT)),'sha256':hashlib.sha256(c26path.read_bytes()).hexdigest(),'count':len(witnesses)},'surfaces':surface_rows,'mutations':mutations,'cleanup':cleanup,'sources':b11.sources(),'private_snapshot':durable})
    print(json.dumps({'total':len(checks),'failures':sum(not v for v in checks.values()),'error':error,'cleanup':cleanup},ensure_ascii=False))
    assert error is None and all(checks.values()) and all(cleanup.values()),error

if __name__=='__main__':run(sys.argv[1])
