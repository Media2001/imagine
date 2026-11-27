"""B16 : vrais GET, trois identités, vide et mode lecture, restauration relue."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import b16 as owner
import b13
spec=importlib.util.spec_from_file_location('browser_common', b13.ROOT/'wp/outils/demo/b13-browser.py')
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)

def run(label):
    identity=b13.guard(); _,markers=common.inventory()
    before=b13.c29.state()
    snapshot=b13.wp('''global $wpdb;$ids=[14,17,82];$u=get_option('imagine_c09_fixture')['users'];$out=['posts'=>[],'meta'=>[],'terms'=>[],'sessions'=>[],'cache'=>$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN ('_transient_product_query-transient-version','_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero')",ARRAY_A)];foreach($ids as $id){$out['posts'][$id]=get_post($id)->to_array();$out['meta'][$id]=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d",$id),ARRAY_A);$out['terms'][$id]=wp_get_object_terms($id,'post_tag',['fields'=>'ids']);}foreach(['A-PAPIER','P-NUMERO'] as $r){$id=(int)$u[$r];$out['sessions'][$id]=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key='session_tokens'",$id),ARRAY_A);}echo wp_json_encode($out);''')
    private=b13.b11.private(label,snapshot)
    checks={};rows=[];error=None;external=[]
    def check(name, ok):
        checks[name]=bool(ok);assert ok,name
    try:
        seeded=b13.wp('''$t=wp_insert_term('FICTIF B16 mot-clé','post_tag');if(is_wp_error($t)){throw new RuntimeException('terme');}$term=$t['term_id'];foreach([14,17] as $id){update_post_meta($id,'imagine_signature',wp_slash('Journaliste FICTIF \\ Test'));wp_set_post_terms($id,[$term],'post_tag');}delete_post_meta(82,'imagine_signature');delete_post_meta(82,'imagine_numero_id');$u=get_option('imagine_c09_fixture')['users'];$auth=[];foreach(['A-PAPIER','P-NUMERO'] as $r){$id=(int)$u[$r];$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);$auth[$r]=[LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'logged_in',$token)];}echo wp_json_encode(['term'=>$term,'auth'=>$auth,'paths'=>array_map(static fn($id)=>wp_parse_url(get_permalink($id),PHP_URL_PATH),[14,17,82])]);''')
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,channel='msedge')
            for role in ['anonyme','A-PAPIER','P-NUMERO']:
                ctx=browser.new_context(viewport={'width':1280,'height':1000},java_script_enabled=False)
                def route(r):
                    if urlsplit(r.request.url).netloc != urlsplit(identity['url']).netloc:external.append(r.request.url);r.abort()
                    else:r.continue_()
                ctx.route('**/*',route)
                if role!='anonyme':ctx.add_cookies([{'name':k,'value':v,'url':identity['url']} for k,v in seeded['auth'][role].items()])
                for i,path in enumerate(seeded['paths']):
                    page=ctx.new_page();response=page.goto(identity['url']+path,wait_until='networkidle')
                    check(f'{role}_{i}_200',response.status==200)
                    article=page.locator('article.imagine-article');head=article.locator('header[data-b16="entete"]')
                    check(f'{role}_{i}_structure',article.count()==1 and page.locator('h1').count()==1 and head.count()==1)
                    keys=head.locator('[data-b16]').evaluate_all('(xs)=>xs.map(x=>x.dataset.b16)')
                    if i<2:
                        check(f'{role}_{i}_ordre',keys==['resume','mots-cles','thematique','signature','numero'])
                        check(f'{role}_{i}_signature',head.locator('[data-b16="signature"]').text_content()=='Par Journaliste FICTIF \\ Test')
                        check(f'{role}_{i}_liens',head.locator('[data-b16="numero"] a').count()==1 and head.locator('[data-b16="thematique"] a').count()>0 and head.locator('[data-b16="signature"] a').count()==0)
                    else:
                        check(f'{role}_{i}_vides_omis',all(x not in keys for x in ['resume','signature','numero']))
                    expected=(i==0 and role=='P-NUMERO')
                    check(f'{role}_{i}_cta',article.locator('[data-b16="abonnement"]').count()==int(expected))
                    if expected:
                        check(f'{role}_{i}_lien_menu',article.locator('[data-b16="abonnement"] a').get_attribute('href')==page.locator('nav[aria-label="Navigation principale"] a[href$="/abonnement-en-attente/"]').first.get_attribute('href'))
                    def extract():
                        return head.evaluate('(x)=>x.outerHTML')+article.locator('[data-b16="abonnement"]').evaluate_all('(xs)=>xs.map(x=>x.outerHTML).join(\"\")')
                    surrounding=extract()
                    check(f'{role}_{i}_etanche',common.c26.c23.assess(200,surrounding,markers)['ok'])
                    target=article.locator('[data-b16="abonnement"]') if expected else head
                    target.evaluate('(x,m)=>x.setAttribute(\"data-b16-mutant\",m)',markers[0])
                    mutated=extract()
                    check(f'{role}_{i}_mutation_detectee',not common.c26.c23.assess(200,mutated,markers)['ok'])
                    target.evaluate('(x)=>x.removeAttribute(\"data-b16-mutant\")')
                    page.evaluate("document.documentElement.classList.add('imagine-reading')")
                    check(f'{role}_{i}_lecture_texte_seul',not head.is_visible() and article.locator('[data-imagine-body="article"]').is_visible() and (not expected or not article.locator('[data-b16="abonnement"]').is_visible()))
                    page.evaluate("document.documentElement.classList.remove('imagine-reading')")
                    if i==0 and role=='anonyme':page.screenshot(path=str(owner.OUT/(label+'.png')),full_page=True)
                    rows.append({'role':role,'path':path,'keys':keys,'cta':expected})
                    page.close()
                ctx.close()
            browser.close()
        check('aucun_tiers',external==[])
    except Exception as exc:error=repr(exc)
    finally:
        restore=b13.wp('''global $wpdb;$s='''+b13.php(snapshot)+''';foreach($s['posts'] as $id=>$row){$wpdb->delete($wpdb->postmeta,['post_id'=>$id]);foreach($s['meta'][$id] as $m){$wpdb->insert($wpdb->postmeta,$m);}wp_set_post_terms((int)$id,$s['terms'][$id],'post_tag');clean_post_cache($id);}'''+('wp_delete_term('+str(seeded['term'])+",'post_tag');" if 'seeded' in locals() else '')+'''foreach($s['sessions'] as $id=>$rows){$wpdb->delete($wpdb->usermeta,['user_id'=>$id,'meta_key'=>'session_tokens']);foreach($rows as $r){$wpdb->insert($wpdb->usermeta,$r);}}$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name IN ('_transient_product_query-transient-version','_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero')");foreach($s['cache'] as $row){$wpdb->insert($wpdb->options,$row);}wp_cache_flush();echo wp_json_encode(true);''')
        after=b13.c29.state()
        allowed={'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero'}
        delta={k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k)!=after['option_fingerprints'].get(k)}
        restored=all(before[k]==after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint']) and delta<=allowed
        b13.save(owner,label,{'checks':checks,'total':len(checks),'rows':rows,'error':error,'restored':restored,'markers_count':len(markers),'before':before,'after':after,'private':private,'sources':owner.sources(owner),'external':external})
    print(json.dumps({'checks':len(checks),'rows':len(rows),'error':error,'restored':restored,'failed':[k for k,v in checks.items() if not v]}))
    assert not error and restored and checks and all(checks.values())

if __name__=='__main__':run(sys.argv[1])
