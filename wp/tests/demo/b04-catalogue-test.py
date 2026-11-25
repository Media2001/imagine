"""Native archive/main-query pagination, taxonomy and public C14 destination."""
from pathlib import Path
import importlib.util
import json
import sys
from urllib.parse import urlsplit
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
s=importlib.util.spec_from_file_location('b04_http',HERE/'b04-http.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.work
w.guard()
checks={}
phase=sys.argv[1] if len(sys.argv)>1 else 'final'
inventory=w.wp(r'''
$out=['archive'=>get_post_type_archive_link('imagine_numero'),'issues'=>[], 'terms'=>[]];
foreach(get_posts(['post_type'=>'imagine_numero','post_status'=>'publish','numberposts'=>-1,'meta_key'=>'imagine_sortie','orderby'=>['meta_value'=>'DESC','ID'=>'DESC']]) as $p){$out['issues'][]=['id'=>$p->ID,'date'=>get_post_meta($p->ID,'imagine_sortie',true),'title'=>$p->post_title,'cover'=>get_post_thumbnail_id($p->ID)];}
foreach(get_terms(['taxonomy'=>'imagine_thematique','hide_empty'=>true]) as $term){
$row=['url'=>get_term_link($term),'articles'=>[]];
foreach(get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>-1,'tax_query'=>[['taxonomy'=>'imagine_thematique','terms'=>[$term->term_id]]]]) as $p){
$issue=(int)get_post_meta($p->ID,'imagine_numero_id',true);
$row['articles'][]=['id'=>$p->ID,'issue'=>$issue];}
$out['terms'][(string)$term->term_id]=$row;}
$out['product_url']=get_permalink(get_option('imagine_b04_fixture')['product']);
echo wp_json_encode($out);
''')
expected=w.wp(r'''
$users=get_option('imagine_c09_fixture')['users'];$out=[];
foreach(['anonyme'=>0,'a-carte'=>$users['A-CARTE'],'p-numero'=>$users['P-NUMERO']] as $label=>$id){wp_set_current_user($id);
foreach(get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>-1]) as $p){$out[$label][(string)$p->ID]=Imagine\Theme\imagine_access_status(Imagine\Site\Paywall::decision($p));}}
echo wp_json_encode($out);
''')
accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
clients={'anonyme':None,'a-carte':m.http.login(accounts['A-CARTE']),'p-numero':m.http.login(accounts['P-NUMERO'])}
def pages(url,client=None):
    seen=set();out=[]
    while url:
        path=urlsplit(url).path+('?' + urlsplit(url).query if urlsplit(url).query else '')
        assert path not in seen and len(seen)<20
        seen.add(path)
        code,headers,text=m.http.fetch(path,client)
        soup=m.BeautifulSoup(text,'html.parser')
        out.append((path,code,headers,soup,text))
        next_link=soup.select_one('a.next.page-numbers')
        url=next_link['href'] if next_link else None
    return out
archive_pages=pages(inventory['archive'])
archive_ids=[]
for path,code,headers,soup,text in archive_pages:
    checks['archive:'+path+':HTTP']=code==200
    checks['archive:'+path+':HTML5']=not m.validate_html(text)
    checks['archive:'+path+':cache']='private' in headers.get('cache-control','')
    for row in soup.select('main .imagine-list > li[data-imagine-id]'):
        id=int(row['data-imagine-id']);archive_ids.append(id)
        issue=next(i for i in inventory['issues'] if i['id']==id)
        checks['archive:date:'+str(id)]=bool(row.select_one('time[datetime="'+issue['date']+'"]'))
        checks['archive:cover:'+str(id)]=bool(row.select_one('img')) if issue['cover'] else True
        checks['archive:status:'+str(id)]=bool(row.select_one('[data-imagine-access]'))
checks['archive:ordre_complet_sans_doublon']=archive_ids==[i['id'] for i in inventory['issues']]
for label,client in clients.items():
    for term_id,term in inventory['terms'].items():
        collected=[]
        for path,code,headers,soup,text in pages(term['url'],client):
            prefix=label+':term:'+term_id+':'+path
            checks[prefix+':HTTP']=code==200
            checks[prefix+':HTML5']=not m.validate_html(text)
            checks[prefix+':cache']='private' in headers.get('cache-control','') and 'no-store' in headers.get('cache-control','')
            checks[prefix+':pas_PDF']='imagine_pdf=' not in text and '_imagine_pdf_blob' not in text
            for row in soup.select('main .imagine-list > li[data-imagine-id]'):
                id=int(row['data-imagine-id']);collected.append(id)
                badge=row.select_one('[data-imagine-access]');status=expected[label][str(id)]
                checks[prefix+':statut:'+str(id)]=bool(badge and badge.get('data-imagine-access')==status['code'] and badge.get_text(strip=True)==status['label'])
                checks[prefix+':numero:'+str(id)]=any('Dans le numéro' in p.get_text() for p in row.select('p'))
        checks[label+':term:'+term_id+':tous_numeros']=set(collected)=={a['id'] for a in term['articles']} and len(collected)==len(set(collected))
        checks[label+':term:'+term_id+':preuve_transversale']=len({a['issue'] for a in term['articles']})>1
code,headers,text=m.http.fetch(urlsplit(inventory['product_url']).path)
soup=m.BeautifulSoup(text,'html.parser')
checks['C14:produit_public_HTTP200']=code==200
checks['C14:label_fictif']='FICTIF B04' in soup.get_text()
form=soup.select_one('form.cart')
checks['C14:formulaire_natif_ajout_panier']=bool(form and form.select_one('[name="add-to-cart"]'))
checks['C14:pas_de_passerelle_formulaire_paiement']=not soup.select('input[name="payment_method"],iframe[src*="stripe"],script[src*="paypal"]')
# Exercise native main-query pagination without touching the site's posts_per_page option.
native=w.wp(r'''
$old=$GLOBALS['wp_the_query'];$out=[];$_SERVER['REQUEST_URI']='/numeros/';
for($page=1;$page<=3;$page++){
$q=new WP_Query();$GLOBALS['wp_the_query']=$q;$GLOBALS['wp_query']=$q;
$q->query(['post_type'=>'imagine_numero','post_status'=>'publish','posts_per_page'=>2,'paged'=>$page]);
$nav=get_the_posts_pagination();$out[]=['ids'=>wp_list_pluck($q->posts,'ID'),'size'=>$q->get('posts_per_page'),'found'=>$q->found_posts,'pages'=>$q->max_num_pages,'native_navigation'=>str_contains($nav,'page-numbers')&&str_contains($nav,'/numeros/')];}
$GLOBALS['wp_the_query']=$old;$GLOBALS['wp_query']=$old;
echo wp_json_encode($out);
''')
checks['pagination:taille_native_preservee']=all(p['size']==2 for p in native)
checks['pagination:navigation_WP_native']=all(p['native_navigation'] for p in native)
checks['pagination:pages_2_2_1']=[len(p['ids']) for p in native]==[2,2,1]
checks['pagination:ordre_descendant_sans_doublon']=[id for p in native for id in p['ids']]==[i['id'] for i in inventory['issues']]
result={'scope':'imagine-test-demo','total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],'native_pagination':native,'archive_pages':len(archive_pages),'term_count':len(inventory['terms'])}
(w.PROOF/('catalogue-'+phase+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'total':len(checks),'failures':result['failures']}))
if result['failures']:raise SystemExit(1)
