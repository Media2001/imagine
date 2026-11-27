"""Vrai HTTP B09 : POST, admin, callbacks natifs, mutation REST/recherche et inverses indépendantes."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import b09

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.hrefs += [v for k,v in attrs if k=='href']

class SameSite(urllib.request.HTTPRedirectHandler):
    def __init__(self,base):
        self.base=base
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert newurl.startswith(self.base+'/'), 'Redirection hors cible refusée'
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def run(label):
    assert not (b09.PROOF/(label+'.json')).exists()
    identity=b09.b08.c25.b06.guard()
    database=b09.b08.snapshot(); business=b09.b08.c25.b06.state()
    durable=b09.b08.c25.private('b09-'+label,{'database':database,'business':business})
    private_path=Path(os.environ['TMPDIR'])/durable['file']
    observer='mu-plugins/b09-observer.php'
    mutant='mu-plugins/b09-mutation-prive.php'
    assert b09.wp('$v=[];foreach('+b09.php([observer,mutant])+' as $n){$v[]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);')==[False,False]
    assert b09.wp('echo wp_json_encode(get_posts(["post_type"=>"imagine_contact","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]));')==[]
    checks={}; cleanup={}; auth={}; owned=[]; error=None; evidence={}
    try:
        b09.b08.c25.b06.profils.b00.upload(observer,(b09.ROOT/'wp/tests/demo/b09-observer.php').read_bytes())
        positive=b09.wp("wp_mail('fictif@example.org','Fictif','Fictif');wp_remote_get('https://example.org/');$v=get_option('imagine_b09_observations');update_option('imagine_b09_observations',[],false);echo wp_json_encode($v);")
        checks['observateurs_positifs']=positive=={'ambiance_mail':1,'ambiance_http':1}
        known=b09.wp("$u=get_userdata(28);if(!$u||user_can($u,'manage_options')||!str_ends_with($u->user_email,'@example.org')){throw new RuntimeException('Personnage attendu absent');}echo wp_json_encode($u->user_email);")
        unknown='b09-inconnu@example.org'
        assert b09.wp('echo wp_json_encode(email_exists('+b09.php(unknown)+'));') is False
        auth=b09.wp("$out=[];foreach(['admin'=>get_users(['role'=>'administrator','number'=>1])[0]->ID,'lecteur'=>28] as $k=>$id){$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);$out[$k]=['id'=>$id,'cookie'=>LOGGED_IN_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'logged_in',$token).'; '.AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'auth',$token).'; '.SECURE_AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'secure_auth',$token)];}echo wp_json_encode($out);")
        b09.b08.c25.private('b09-'+label+'-auth',auth)
        opener=urllib.request.build_opener(SameSite(identity['url']))
        def http(path,data=None,as_user=''):
            assert path.startswith('/') and not path.startswith('//')
            headers={'User-Agent':'Imagine-B09-fictif'}
            if as_user: headers['Cookie']=auth[as_user]['cookie']
            request=urllib.request.Request(identity['url']+path,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers=headers)
            try: response=opener.open(request,timeout=35)
            except urllib.error.HTTPError as e: response=e
            with response:
                assert response.geturl().startswith(identity['url']+'/')
                return response.status,response.read().decode('utf-8'),response.geturl()
        _,home,_=http('/')
        footer=re.search(r'<nav aria-label="Navigation de pied de page">(.*?)</nav>',home,re.S)
        checks['footer_natif_present']=footer is not None
        footerlinks=Links(); footerlinks.feed(footer.group(1))
        rows=json.loads((b09.PROOF/'pages-reprise.json').read_text(encoding='utf-8'))['readback']
        checks['footer_cinq_pages_natives']=footerlinks.hrefs==[r['url'] for r in rows.values()]
        main=re.search(r'<nav aria-label="Navigation principale">(.*?)</nav>',home,re.S).group(1)
        checks['principal_sans_entree_B09']=all(r['url'] not in main for r in rows.values()) and 'Notre coopérative' in main
        for k,row in rows.items():
            status,body,_=http(urllib.parse.urlsplit(row['url']).path)
            article=body.split('<article>',1)[1].split('</article>',1)[0]
            checks['page_publique_'+k]=status==200 and unescape(re.search(r'<h1>(.*?)</h1>',article,re.S).group(1))==row['title']
            if k in ['cgv','confidentialite','cookies']:
                checks['page_legale_vide_'+k]=re.sub(r'<h1>.*?</h1>','',article,flags=re.S).strip()==''
            if k=='faq':
                checks['FAQ_quatre_rubriques_sans_question']=re.findall(r'<h2[^>]*>(.*?)</h2>',article,re.S)==['Accès numérique','Abonnement','Facturation','Livraison'] and '<details' not in article
        privacy=b09.wp("$v=get_option('imagine_b09_pages');echo wp_json_encode(['id'=>(int)get_option('wp_page_for_privacy_policy'),'expected'=>$v['confidentialite'],'url'=>get_privacy_policy_url()]);")
        checks['privacy_declaree_native']=privacy['id']==privacy['expected']==rows['confidentialite']['id'] and privacy['url']==rows['confidentialite']['url']
        _,form,_=http('/contact/')
        node=form.split('<form id="imagine-contact"',1)[1].split('</form>',1)[0]
        checks['consentement_initial_non_coche']='type="checkbox"' in node and 'checked' not in node and privacy['url'] in node
        nonce=unescape(re.search(r'name="_b09" value="([^"]+)"',node).group(1))
        name='Personnage fictif B09 \\ rédaction'
        text="B09_MESSAGE_PRIVE C:\\dossier\\fichier\nDeuxième ligne \\ et l'apostrophe"
        payload={'action':'imagine_contact','_b09':nonce,'nom':name,'email':known,'contact':text}
        a,body1,url1=http('/wp-admin/admin-post.php',payload)
        b,body2,url2=http('/wp-admin/admin-post.php',{**payload,'email':unknown,'contact':'B09_TIERS_PRIVE','consentement':'1'})
        status=lambda body:unescape(re.search(r'<p role="status">(.*?)</p>',body,re.S).group(1))
        checks['POST_reel_pas_enumeration_compte']=a==b==200 and url1==url2 and 'contact=enregistree' in url1 and status(body1)==status(body2)
        stored=b09.wp('$a=Imagine\\Site\\Contact::ids('+b09.php(known)+');$b=Imagine\\Site\\Contact::ids('+b09.php(unknown)+');echo wp_json_encode(["a"=>$a,"b"=>$b,"consentements"=>[get_post_meta($a[0],"imagine_contact_consentement",true),get_post_meta($b[0],"imagine_contact_consentement",true)],"status"=>[get_post($a[0])->post_status,get_post($b[0])->post_status],"bodies"=>[get_post($a[0])->post_content,get_post($b[0])->post_content]]);')
        owned=stored['a']+stored['b']
        checks['stockage_prive_local']=len(stored['a'])==len(stored['b'])==1 and stored['consentements']==['0','1'] and stored['status']==['private','private'] and stored['bodies']==['','']
        _,invalid,invalid_url=http('/wp-admin/admin-post.php',{**payload,'_b09':'faux'})
        checks['nonce_refuse_sans_insertion']='contact=refusee' in invalid_url and len(b09.wp('echo wp_json_encode(Imagine\\Site\\Contact::ids('+b09.php(known)+'));'))==1
        _,listing,_=http('/wp-admin/edit.php?post_type=imagine_contact',as_user='admin')
        _,detail,_=http('/wp-admin/post.php?post='+str(owned[0])+'&action=edit',as_user='admin')
        checks['admin_liste_detail_positifs']='Messages de contact' in listing and 'B09_MESSAGE_PRIVE' in detail
        field=re.search(r'<strong>Message</strong><br>(.*?)</p>',detail,re.S)
        checks['antislash_detail_exact']=field is not None and unescape(re.sub(r'<[^>]+>','',field.group(1)))==text and name in unescape(detail)
        forbidden_code,forbidden,_=http('/wp-admin/post.php?post='+str(owned[0])+'&action=edit',as_user='lecteur')
        checks['detail_admin_seul']='B09_MESSAGE_PRIVE' not in forbidden and ('imagine-contact-prive' not in forbidden)
        registry=b09.wp("$a=apply_filters('wp_privacy_personal_data_exporters',[]);$b=apply_filters('wp_privacy_personal_data_erasers',[]);echo wp_json_encode(['export'=>isset($a['imagine-contacts']),'erase'=>isset($b['imagine-contacts'])]);")
        checks['declaration_outils_C21_natifs']=registry=={'export':True,'erase':True}
        exported=b09.wp('$r=apply_filters("wp_privacy_personal_data_exporters",[]);echo wp_json_encode(call_user_func($r["imagine-contacts"]["callback"],'+b09.php(known)+',1));')
        fields={f['name']:f['value'] for f in exported['data'][0]['data']}
        checks['export_adresse_antislash_exact_sans_tiers']=len(exported['data'])==1 and fields['Message']==text and fields['Nom']==name and 'B09_TIERS_PRIVE' not in json.dumps(exported)
        _,public_rest,_=http('/wp-json/wp/v2/pages?per_page=100')
        checks['REST_temoin_public_positif']=rows['faq']['id'] in [r['id'] for r in json.loads(public_rest)]
        _,public_search,_=http('/?s=FAQ+du+service+client')
        links=Links();links.feed(public_search)
        checks['recherche_temoin_public_positif']=rows['faq']['url'] in links.hrefs
        def isolation():
            route,collection,_=http('/wp-json/wp/v2/imagine_contact?per_page=100')
            _,native,_=http('/wp-json/wp/v2/search?search=Message%20de%20contact&per_page=100')
            _,search,_=http('/?s=Message+de+contact')
            p=Links();p.feed(search)
            targets=b09.wp('$v=[];foreach('+b09.php(owned)+' as $id){$v[]=get_permalink($id);}echo wp_json_encode($v);')
            rest_ids=[r['id'] for r in json.loads(collection)] if route==200 else []
            native_ids=[r['id'] for r in json.loads(native)]
            return {'route_rest_fermee':route==404 and json.loads(collection).get('code')=='rest_no_route',
                    'REST_aucun_message':not set(owned).intersection(rest_ids+native_ids),
                    'recherche_aucun_message':not any(u in p.hrefs for u in targets)}
        baseline=isolation()
        checks['absence_REST_recherche']=all(baseline.values())
        b09.b08.c25.b06.profils.b00.upload(mutant,(b09.ROOT/'wp/tests/demo/b09-mutation-prive.php').read_bytes())
        b09.wp('echo wp_json_encode(wp_update_post(["ID"=>'+str(owned[0])+',"post_status"=>"publish"])==='+str(owned[0])+');')
        mutation=isolation()
        checks['mutation_reelle_REST_recherche_detectee']=mutation=={'route_rest_fermee':False,'REST_aucun_message':False,'recherche_aucun_message':False}
        b09.wp('echo wp_json_encode(wp_update_post(["ID"=>'+str(owned[0])+',"post_status"=>"private"])==='+str(owned[0])+');')
        b09.remove_remote([mutant])
        after_mutation=isolation()
        checks['isolation_revenue_apres_mutation']=all(after_mutation.values())
        erased=b09.wp('$r=apply_filters("wp_privacy_personal_data_erasers",[]);echo wp_json_encode(call_user_func($r["imagine-contacts"]["callback"],'+b09.php(known)+',1));')
        remaining=b09.wp('echo wp_json_encode([Imagine\\Site\\Contact::ids('+b09.php(known)+'),Imagine\\Site\\Contact::ids('+b09.php(unknown)+')]);')
        checks['effacement_natif_cible_tiers_preserve']=erased['items_removed'] and erased['done'] and remaining==[[],stored['b']]
        checks['effacement_postmeta_relu']=b09.wp('global $wpdb;echo wp_json_encode((int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE post_id='+str(owned[0])+'"));')==0
        observations=b09.wp('echo wp_json_encode(get_option("imagine_b09_observations"));')
        checks['aucun_email_HTTP_du_contact']=not any(v for k,v in (observations.items() if isinstance(observations,dict) else []) if k.startswith('b09_'))
        evidence={'baseline_isolation':baseline,'mutation_isolation':mutation,'after_mutation_isolation':after_mutation,'observations':observations,'native_privacy':privacy}
        assert all(v is True for v in checks.values()),checks
    except Exception as e:
        error=type(e).__name__
        raise
    finally:
        raw=private_path.read_bytes();assert hashlib.sha256(raw).hexdigest()==durable['sha256']
        saved=json.loads(raw)['payload']['database']
        def attempt(key,fn):
            try:
                fn();cleanup[key]=True
            except Exception as e:
                cleanup[key]=False
        # Retirer seulement les contacts nés dans ce parcours (type vide préalablement prouvé).
        def messages():
            b09.wp('''foreach(get_posts(['post_type'=>'imagine_contact','post_status'=>['publish','private','draft','trash'],'numberposts'=>-1]) as $p){wp_delete_post($p->ID,true);}delete_option('imagine_b09_observations');echo wp_json_encode(true);''')
        attempt('contacts_et_observations_retires',messages)
        for role,session in auth.items():
            uid=int(session['id']);rows=[r for r in saved['usermeta'] if int(r['user_id'])==uid]
            def restore_user(uid=uid,rows=rows):
                b09.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["user_id"=>'+str(uid)+']);foreach('+b09.php(rows)+' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete('+str(uid)+',"user_meta");echo wp_json_encode(true);')
            attempt('usermeta_'+role+'_restaure',restore_user)
        def remove_files():
            present=b09.wp('$v=[];foreach('+b09.php([observer,mutant])+' as $n){if(file_exists(WP_CONTENT_DIR."/".$n)){$v[]=$n;}}echo wp_json_encode($v);')
            b09.remove_remote(present)
        attempt('observateur_et_mutation_retires',remove_files)
        exact={};preserved=False
        try:
            current=b09.b08.snapshot()
            exact={k:current[k]==saved[k] for k in ['users','usermeta','posts','postmeta','comments','commentmeta','navigation','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta']}
            opts=lambda db:[r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] in ['cron','theme_mods_imagine','wp_page_for_privacy_policy']]
            exact['options_metier']=opts(current)==opts(saved)
            preserved=business==b09.b08.c25.b06.state()
        finally:
            b09.save(label,{'checks':checks,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved,'private_snapshot':durable,'error':error,**evidence})
            print(json.dumps({'checks':checks,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved},ensure_ascii=False))
        assert cleanup and all(cleanup.values()) and exact and all(exact.values()) and preserved,'Inverse non prouvée'


if __name__=='__main__':
    run(sys.argv[1])
