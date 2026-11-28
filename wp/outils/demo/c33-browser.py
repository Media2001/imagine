"""C33: réponses natives anonymes, cinq mutations, REST admin/éditeur conservé."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,re,secrets
from urllib.parse import urlencode,urlsplit
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
import c33 as o
import b13
sp=importlib.util.spec_from_file_location('c33_common',o.ROOT/'wp/outils/demo/b13-browser.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
i=o.guard();catalog,markers=b.inventory();before=b13.c29.state()
options=o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN (\'blog_public\',\'user_count\',\'rewrite_rules\') ORDER BY option_name",ARRAY_A));')
run=secrets.token_hex(6);login='fictif-c33-'+run;display='NOM_COMPTE_FICTIF_C33_'+run;slug='article-c33-'+run;signature='SIGNATURE_FICTIVE_C33'
private=b13.b11.private(sys.argv[1],{'options':options,'login':login,'slug':slug})
probe='mu-plugins/c33-observer.php';checks={};rows=[];error=None;external=[];fixture=None

def check(n,ok):checks[n]=bool(ok);assert ok,n

def control(kind,status,body,headers,expected_signature=signature):
    leak=any(t in body+'\n'+json.dumps(headers) for t in [login,display])
    if kind=='author':present=bool(body or headers.get('location'));ok=status==404
    elif kind=='rest':
        try:d=json.loads(body);present=isinstance(d,dict) and isinstance(d.get('code'),str)
        except ValueError:present=False
        ok=status==404
    elif kind=='sitemap':
        try:x=ET.fromstring(body);locs=[e.text for e in x.iter() if e.tag.endswith('loc')];present=x.tag.endswith('sitemapindex') and bool(locs)
        except ET.ParseError:present=False;locs=[]
        ok=status==200 and not any('wp-sitemap-users-' in (x or '') for x in locs)
    elif kind=='users-sitemap':present=bool(body);ok=status==404
    elif kind=='feed':
        try:x=ET.fromstring(body);present=any(e.tag.endswith('item') or e.tag.endswith('entry') for e in x.iter()) and fixture['path'] in body
        except ET.ParseError:present=False
        ok=status==200 and expected_signature in body
    else:
        try:d=json.loads(body);present=d.get('type')=='rich' and bool(d.get('html')) and d.get('title')=='FICTIF C33 article public'
        except ValueError:present=False;d={}
        ok=status==200 and d.get('author_name')==expected_signature and 'author_url' not in d
    return {'ok':bool(present and ok and not leak),'present':bool(present),'leak':leak}

try:
    assert o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    b13.b11.upload(probe,(o.ROOT/'wp/tests/demo/c33-observer.php').read_bytes())
    fixture=o.wp('''if(username_exists('''+o.php(login)+''') || get_page_by_path('''+o.php(slug)+''',OBJECT,'post')){throw new RuntimeException('Collision témoin');}
$u=wp_insert_user(['user_login'=>'''+o.php(login)+''','user_email'=>'''+o.php(login+'@example.org')+''','user_pass'=>wp_generate_password(48),'display_name'=>'''+o.php(display)+''','user_url'=>home_url('/author/'''+login+'''/'),'role'=>'administrator']);if(is_wp_error($u)){throw new RuntimeException('Compte témoin refusé');}
$p=wp_insert_post(['post_type'=>'post','post_status'=>'publish','post_author'=>$u,'post_name'=>'''+o.php(slug)+''','post_title'=>'FICTIF C33 article public','post_content'=>'Article public de recette C33, entièrement fictif.'],true);if(is_wp_error($p)){throw new RuntimeException('Article témoin refusé');}
update_post_meta($p,Imagine\\Site\\PageArticle::SIGNATURE,'''+o.php(signature)+''');update_option('blog_public',1);echo wp_json_encode(['uid'=>$u,'pid'=>$p,'path'=>wp_make_link_relative(get_permalink($p)),'author_path'=>wp_make_link_relative(get_author_posts_url($u)),'published'=>get_post($p)->post_status==='publish']);''')
    check('temoin_publie',fixture['published'])
    uid,pid=fixture['uid'],fixture['pid']
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,channel='msedge');ctx=browser.new_context(viewport={'width':1280,'height':1000},java_script_enabled=True)
        def route(r):
            if urlsplit(r.request.url).netloc!=urlsplit(i['url']).netloc:external.append(urlsplit(r.request.url).netloc);r.abort()
            else:r.continue_()
        ctx.route('**/*',route)
        def fetch(name,kind,path,mutant=False,expected_signature=signature):
            response=ctx.request.get(i['url']+path,max_redirects=0);body=response.text();headers={k:v for k,v in response.headers.items() if k in ['location','content-type','link']}
            verdict=control(kind,response.status,body,headers,expected_signature)
            filename=sys.argv[1]+'-'+name+'.txt'
            with (o.OUT/filename).open('x',encoding='utf-8') as f:f.write(json.dumps({'status':response.status,'headers':headers},ensure_ascii=False)+'\n\n'+body)
            rows.append({'name':name,'kind':kind,'path':path,'status':response.status,'headers':headers,'response':filename,'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'mutant':mutant,**verdict})
            if mutant:check(name+'_mutation_detectee',not verdict['ok'] and (verdict['leak'] or kind=='sitemap' and 'wp-sitemap-users-' in body))
            else:
                check(name+'_voie_presente',verdict['present']);check(name+'_fermee_ou_signature',verdict['ok'])
                check(name+'_etanche',b.c26.c23.assess(response.status,body,markers)['ok'])
            return body
        fetch('archive-nom','author',fixture['author_path']);fetch('archive-numero','author','/?author='+str(uid))
        fetch('rest-liste','rest','/wp-json/wp/v2/users?'+urlencode({'include':uid}));fetch('rest-detail','rest','/wp-json/wp/v2/users/'+str(uid));fetch('rest-alias','rest','/?rest_route=/wp/v2/users/'+str(uid));fetch('rest-casse','rest','/wp-json/WP/V2/USERS/'+str(uid))
        index=fetch('sitemap-index','sitemap','/wp-sitemap.xml');fetch('sitemap-users','users-sitemap','/wp-sitemap-users-1.xml')
        sitemap_types=re.findall(r'wp-sitemap-posts-([a-zA-Z0-9_]+)-[0-9]+\.xml',index)
        check('sitemap_posts_non_vide',bool(sitemap_types));private_types=['imagine_sujet','imagine_contact','imagine_inscription','attachment','imagine_justificatif']
        private_sitemap_findings=[t for t in sitemap_types if t in private_types]
        fetch('rss2','feed','/?feed=rss2&p='+str(pid));fetch('atom','feed','/?feed=atom&p='+str(pid))
        embed='/wp-json/oembed/1.0/embed?'+urlencode({'url':i['url']+fixture['path']})
        fetch('oembed','oembed',embed)
        o.wp('delete_post_meta('+str(pid)+',Imagine\\Site\\PageArticle::SIGNATURE);echo wp_json_encode(true);')
        sitename=o.wp('echo wp_json_encode(get_bloginfo("name"));')
        fetch('rss2-repli','feed','/?feed=rss2&p='+str(pid),expected_signature=sitename);fetch('oembed-repli','oembed',embed,expected_signature=sitename)
        o.wp('update_post_meta('+str(pid)+',Imagine\\Site\\PageArticle::SIGNATURE,'+o.php(signature)+');echo wp_json_encode(true);')
        mutations=[('author','author','/?author='+str(uid)),('rest','rest','/wp-json/wp/v2/users/'+str(uid)),('sitemap','sitemap','/wp-sitemap.xml'),('feed','feed','/?feed=rss2&p='+str(pid)),('oembed','oembed',embed)]
        for name,kind,path in mutations:fetch('mutation-'+name,kind,path+('&' if '?' in path else '?')+'c33_mutate='+name,True)
        auth=o.wp('$id='+str(uid)+';wp_set_current_user($id);$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);wp_set_current_user(0);$_COOKIE[LOGGED_IN_COOKIE]=wp_generate_auth_cookie($id,time()+3600,"logged_in",$token);wp_set_current_user($id);echo wp_json_encode(["cookies"=>[LOGGED_IN_COOKIE=>$_COOKIE[LOGGED_IN_COOKIE]],"nonce"=>wp_create_nonce("wp_rest")]);')
        ctx.add_cookies([{'name':k,'value':v,'url':i['url']} for k,v in auth['cookies'].items()])
        for role in ['administrator','editor']:
            o.wp('$u=new WP_User('+str(uid)+');$u->set_role('+o.php(role)+');echo wp_json_encode(true);')
            q='/wp-json/wp/v2/users?'+urlencode({'include':uid,'who':'authors'})
            res=ctx.request.get(i['url']+q,headers={'X-WP-Nonce':auth['nonce']});data=res.json()
            check(role+'_selecteur_auteur_natif',res.status==200 and isinstance(data,list) and any(x.get('id')==uid for x in data))
            res=ctx.request.get(i['url']+'/wp-json/wp/v2/posts/'+str(pid)+'?context=edit',headers={'X-WP-Nonce':auth['nonce']})
            check(role+'_edition_article_native',res.status==200 and res.json().get('author')==uid)
        ctx.clear_cookies();page=ctx.new_page();res=page.goto(i['url']+'/wp-json/wp/v2/users/'+str(uid),wait_until='networkidle');check('navigateur_reel_404',res.status==404 and login not in page.locator('body').inner_text());page.screenshot(path=str(o.OUT/(sys.argv[1]+'.png')),full_page=True)
        ctx.close();browser.close()
    check('aucun_tiers',not external)
except Exception as exc:error=repr(exc)
finally:
    # Retrouver les objets par leurs identités réservées même si la création a échoué après écriture.
    cleaned=o.wp('''global $wpdb;$u=get_user_by('login','''+o.php(login)+''');$p=get_page_by_path('''+o.php(slug)+''',OBJECT,'post');if($p){if(!$u || (int)$p->post_author!==(int)$u->ID){throw new RuntimeException('Article étranger');}wp_delete_post($p->ID,true);}if($u){$wpdb->delete($wpdb->usermeta,['user_id'=>$u->ID]);$wpdb->delete($wpdb->users,['ID'=>$u->ID]);clean_user_cache($u->ID);}foreach(['blog_public','user_count','rewrite_rules'] as $key){$wpdb->delete($wpdb->options,['option_name'=>$key]);}foreach('''+o.php(options)+''' as $r){$wpdb->insert($wpdb->options,$r);}wp_cache_flush();echo wp_json_encode(!get_user_by('login','''+o.php(login)+''') && !get_page_by_path('''+o.php(slug)+''',OBJECT,'post'));''')
    b13.b11.b10.b09.remove_remote([probe]);removed=o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
    after=b13.c29.state();allowed={'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero'}
    delta={k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k)!=after['option_fingerprints'].get(k)}
    restored=all(before[k]==after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta<=allowed
    b13.save(o,sys.argv[1],{'checks':checks,'total':len(checks),'rows':rows,'error':error,'restored':restored,'fixture_removed':cleaned,'probe_removed':removed,'private':private,'before':before,'after':after,'option_delta':sorted(delta),'external':external,'sources':o.sources(o),'sitemap_types':locals().get('sitemap_types',[]),'private_sitemap_findings':locals().get('private_sitemap_findings',[]),'baseline_sitemap_disabled':any(x['option_name']=='blog_public' and x['option_value']=='0' for x in options)})
print({'total':len(checks),'rows':len(rows),'error':error,'restored':restored,'fixture_removed':cleaned,'probe_removed':removed})
assert not error and restored and cleaned and removed and all(checks.values())
