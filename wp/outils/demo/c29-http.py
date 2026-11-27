"""C29 authenticated native HTTP, read-only probe and exact fixture/session restoration."""
import sys
sys.dont_write_bytecode=True
import base64
import hashlib
import json
import re
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import c29
import b11
import c19
ROOT,OUT=c29.ROOT,c29.OUT
wp,php=b11.wp,b11.php

def observation(body):
    matches=re.findall(r'<!-- C29_OBSERVATION ([A-Za-z0-9+/=]+) -->',body)
    assert len(matches)==1, 'Observation HTTP absente'
    return json.loads(base64.b64decode(matches[0]))

def totals(body):
    return {k:int(n) for k,n in re.findall(r'data-brevo-total="([^"]+)">(\d+)</td>',body)}

def fiche(body):
    import html
    m=re.search(r'<pre data-brevo-fiche>(.*?)</pre>',body,re.S)
    return json.loads(html.unescape(m[1])) if m else None

def run(label):
    assert not (OUT/(label+'.json')).exists()
    identity=b11.guard();before=c19.state()
    f=wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    ids=list(f['users'].values())
    names=['imagine_newsletters_catalogue','imagine_personnalisation_questions','imagine_brevo_tarifs']
    keys=['imagine_newsletters_preferences','imagine_personnalisation_reponses','imagine_personnalisation_consentement','imagine_cooperateur','imagine_sans_email','session_tokens']
    # Sessions stay in this process only; never written to evidence or stdout.
    old=wp('global $wpdb;$ids='+php(ids)+';$keys='+php(keys)+';$names='+php(names)+''';$o=['options'=>[],'meta'=>[]];foreach($names as $n){$o['options']=array_merge($o['options'],$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->options} WHERE option_name=%s",$n),ARRAY_A));}foreach($ids as $id){foreach($keys as $key){$o['meta']=array_merge($o['meta'],$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=%s",$id,$key),ARRAY_A));}}echo wp_json_encode($o);''')
    probe='mu-plugins/c29-observer.php'
    assert wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+probe+'"));') is False
    checks={};observations=[];external=[];surfaces=[];error=None;restored=False;removed=False
    def check(name,ok):
        checks[name]=bool(ok)
        if not ok:raise AssertionError(name)
    try:
        b11.upload(probe,(ROOT/'wp/tests/demo/c29-observer.php').read_bytes())
        import b06
        check('observateur_relu',b06.hashes([probe])[probe]==hashlib.sha256((ROOT/'wp/tests/demo/c29-observer.php').read_bytes()).hexdigest())
        seed=(ROOT/'wp/tests/demo/c29-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1].split('$writes = [];')[0]
        expected=(ROOT/'wp/tests/demo/c29-attendus.php').read_text(encoding='utf-8').split('<?php',1)[1]
        seed=seed.replace("require __DIR__ . '/c29-attendus.php'",'eval('+php(expected)+')')
        wp(seed+'echo wp_json_encode(true);')
        roles={k:f['users'][v] for k,v in {'admin':'E-ADMIN','referent':'E-ABO','redac':'E-REDAC','reader':'A-CARTE'}.items()}
        auth=wp('$o=[];foreach('+php(roles)+''' as $key=>$id){if(!str_ends_with(get_userdata($id)->user_email,'@example.org')){throw new RuntimeException('Fictif requis');}$t=WP_Session_Tokens::get_instance($id)->create(time()+3600);$o[$key]=[LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'logged_in',$t),AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'auth',$t),SECURE_AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'secure_auth',$t)];}echo wp_json_encode($o);''')
        path='/wp-admin/admin.php?page=imagine-contact-brevo'
        with sync_playwright() as p:
            try:browser=p.chromium.launch(headless=True)
            except Exception:browser=p.chromium.launch(headless=True,channel='msedge')
            contexts={}
            for role in [*roles,'anon']:
                ctx=browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE')
                def route(r):
                    if urlsplit(r.request.url).netloc!=urlsplit(identity['url']).netloc:
                        external.append({'url':r.request.url.split('?')[0],'blocked_before_transport':True});r.abort()
                    else:r.continue_()
                ctx.route('**/*',route)
                if role!='anon':ctx.add_cookies([{'name':k,'value':v,'url':identity['url']} for k,v in auth[role].items()])
                contexts[role]=ctx
            def get(role,suffix='',method='GET',data=None):
                r=contexts[role].request.fetch(identity['url']+path+suffix,method=method,data=data,max_redirects=0)
                return r.status,dict(r.headers),r.text()
            for code in f['users']:
                status,headers,body=get('referent','&compte='+str(f['users'][code]))
                obs=observation(body);observations.append({'code':code,**obs})
                check('HTTP_'+code,status==200 and obs=={'entered':True,'finished':True,'sql':[],'http':[],'mail':[]})
                check('HTTP_no_store_'+code,'no-store' in headers.get('cache-control',''))
                surfaces.append({'code':code,'fiche':fiche(body),'reason':re.findall(r'data-brevo-raison="([^"]+)"',body),'totals':totals(body)})
            want=json.loads((OUT/'native-special-corrected3-V2.json').read_text(encoding='utf-8'))
            want=json.loads(want['native']['stdout'])['profils']
            check('HTTP_27_profils_egal_attendus_independants',all(row['fiche']==want[row['code']]['fiche'] and row['reason']==[want[row['code']]['raison']] for row in surfaces))
            expected_counts={k:0 for k in ['abonne','non_abonne','inconnu','a_retirer','absent']}
            for value in want.values():expected_counts[(value['fiche'] or {}).get('statut','absent')]+=1
            # Extra native accounts (B00 and operations) are included on screen, never silently omitted.
            extra=wp('$ids='+php(ids)+';$out=[];foreach(get_users(["fields"=>"ID"]) as $id){if(!in_array((int)$id,$ids,true)){$out[]=Imagine\\Site\\ContactBrevo::fiche((int)$id);}}echo wp_json_encode($out);')
            for value in extra:expected_counts[(value['fiche'] or {}).get('statut','absent')]+=1
            check('HTTP_totaux_tous_comptes_exacts',all(row['totals']==expected_counts for row in surfaces))
            status,_,body=get('admin','&compte='+str(f['users']['A-CARTE']))
            check('admin_200_memes_fiche_totaux',status==200 and fiche(body)==want['A-CARTE']['fiche'] and totals(body)==expected_counts)
            status,_,body=get('referent','&compte=999999999')
            check('compte_absent_raison_sans_fiche',status==200 and 'data-brevo-raison="compte_absent"' in body and fiche(body) is None)
            status,_,body=get('referent','&compte[]=9')
            check('compte_tableau_refuse_sans_fiche',status==200 and fiche(body) is None)
            status,_,body=get('referent','',method='HEAD')
            check('HEAD_200_sans_corps',status==200 and body=='')
            status,headers,body=get('referent',method='POST',data='imagine_brevo_tarifs={}&compte=9')
            check('POST_405_sans_fiche',status==405 and fiche(body) is None and headers.get('allow')=='GET, HEAD')
            for role in ['redac','reader']:
                for method in ['GET','POST']:
                    status,_,body=get(role,method=method,data='a=b' if method=='POST' else None)
                    check(role+'_'+method+'_403',status==403 and fiche(body) is None and totals(body)=={})
            status,_,body=get('anon')
            check('anonyme_aucune_fiche',status in [302,403] and fiche(body) is None and not totals(body))
            status,_,body=get('referent','&c29_witness=1')
            witness=observation(body)
            check('temoin_HTTP_observateur_SQL_HTTP_mail',status==200 and witness=={'entered':True,'finished':True,'sql':['INSERT'],'http':['blocked'],'mail':['blocked']})
            # Separate Settings API group: deliberate configuration, never the read-only screen.
            r=contexts['admin'].request.get(identity['url']+'/wp-admin/options-general.php?page=imagine-brevo-tarifs')
            nonce=re.search(r'name="_wpnonce" value="([^"]+)"',r.text())
            check('reglage_separe_accessible_admin',r.status==200 and nonce is not None)
            r=contexts['admin'].request.post(identity['url']+'/wp-admin/options.php',form={'option_page':'imagine_brevo_tarifs','action':'update','_wpnonce':nonce[1],'imagine_brevo_tarifs':json.dumps({str(f['tariffs']['normal-1']):'normal-1'})},max_redirects=0)
            check('reglage_natif_sauve_relu',r.status==302 and wp('echo wp_json_encode(get_option(Imagine\\Site\\ContactBrevo::TARIFS));')=={str(f['tariffs']['normal-1']):'normal-1'})
            page=contexts['referent'].new_page()
            page.goto(identity['url']+'/wp-admin/admin.php?page=imagine-tableau-de-bord',wait_until='networkidle')
            page.locator('#adminmenu a[href="admin.php?page=imagine-contact-brevo"]').click()
            page.wait_for_load_state('networkidle')
            check('menu_natif_referent',page.locator('[data-imagine-brevo] h1').inner_text()=='Ce qui partirait vers Brevo')
            page.locator('#imagine-brevo-compte').fill(str(f['users']['A-CARTE']))
            page.locator('[data-imagine-brevo] button').click();page.wait_for_load_state('networkidle')
            check('formulaire_GET_lecture_seule',page.locator('[data-brevo-fiche]').count()==1 and 'compte='+str(f['users']['A-CARTE']) in page.url)
            page.screenshot(path=str(OUT/(label+'.png')),full_page=True)
            check('ressources_C29_aucun_tiers',all(urlsplit(e['url']).hostname=='secure.gravatar.com' for e in external))
            browser.close()
    except Exception as exc:error=repr(exc)
    finally:
        code='global $wpdb;$old='+php(old)+';$ids='+php(ids)+';$keys='+php(keys)+';$names='+php(names)+''';foreach($names as $n){$wpdb->delete($wpdb->options,['option_name'=>$n]);}foreach($old['options'] as $r){$wpdb->insert($wpdb->options,$r);}foreach($ids as $id){foreach($keys as $key){$wpdb->delete($wpdb->usermeta,['user_id'=>$id,'meta_key'=>$key]);}}foreach($old['meta'] as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_flush();echo wp_json_encode(true);'''
        wp(code)
        b11.b10.b09.remove_remote([probe])
        removed=wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
        after=c19.state();restored=before==after
        # Explicit session equality; C19's generic native fingerprint excludes session tokens.
        session_ok=wp('global $wpdb;$old='+php(old['meta'])+';$ids='+php(ids)+''';$expected=array_values(array_filter($old,static fn($r)=>$r['meta_key']==='session_tokens'));$actual=$wpdb->get_results('SELECT * FROM '.$wpdb->usermeta.' WHERE user_id IN ('.implode(',',$ids).") AND meta_key='session_tokens' ORDER BY umeta_id",ARRAY_A);usort($expected,static fn($a,$b)=>(int)$a['umeta_id']<=>(int)$b['umeta_id']);echo wp_json_encode($actual===$expected);''')
        c29.save(label,{'identity':identity,'checks':checks,'total':len(checks),'observations':observations,'surfaces':surfaces,'witness':locals().get('witness'),'external_browser':external,'business_preserved':restored,'sessions_restored':session_ok,'probe_removed':removed,'strict_before':before,'strict_after':after,'error':error})
    print(json.dumps({'checks':len(checks),'failed':[k for k,v in checks.items() if not v],'restored':restored,'sessions_restored':session_ok,'probe_removed':removed,'error':error},ensure_ascii=False))
    assert not error and checks and all(checks.values()) and restored and session_ok and removed
if __name__=='__main__':run(sys.argv[1])
