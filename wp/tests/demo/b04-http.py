"""B04 vrais cookies/GET uniquement ; aucun seed ni création d’objet/droit."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs
import importlib.util
import json
import hashlib
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / 'production/B-04'

def module(name):
    spec = importlib.util.spec_from_file_location('b04_' + name.replace('-','_'), HERE / name)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

work = module('b04-work.py')
http = module('c12-http.py')
from b01_html import BeautifulSoup, validate_html

# Lire les objets existants. Les marqueurs de corps restent en mémoire, jamais dans les reçus.
INVENTORY = r'''
$manifest=get_option('imagine_demo_manifest');$profiles=get_option('imagine_c09_fixture')['users'];
$out=['issues'=>[], 'expected'=>[]];
foreach(['demo-2026-t1','demo-2026-t4'] as $slug){
 $p=get_post($manifest[$slug]);$articles=get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>-1,
 'meta_key'=>'imagine_numero_id','meta_value'=>$p->ID,'orderby'=>['menu_order'=>'ASC','ID'=>'ASC']]);
 $row=['id'=>$p->ID,'path'=>wp_parse_url(get_permalink($p),PHP_URL_PATH),'title'=>$p->post_title,'articles'=>[],'product'=>null];
 foreach($articles as $a){$paragraphs=preg_split('/<\/p>/', $a->post_content);$markers=[];
 foreach($paragraphs as $paragraph){$text=trim(wp_strip_all_tags($paragraph));if(mb_strlen($text)>35 && !str_contains($a->post_excerpt,$text) && !str_contains($p->post_excerpt,$text)){$markers[]=$text;}}
 $row['articles'][]=['id'=>$a->ID,'path'=>wp_parse_url(get_permalink($a),PHP_URL_PATH),'title'=>$a->post_title,'markers'=>$markers];}
 foreach(get_posts(['post_type'=>'product','post_status'=>'publish','numberposts'=>-1,'meta_key'=>Imagine\Site\AchatsNumeros::PRODUIT,'meta_value'=>$p->ID,'orderby'=>'ID','order'=>'ASC']) as $productPost){
 $product=wc_get_product($productPost->ID);if(Imagine\Site\AchatsNumeros::numero($product)===$p->ID && $product->is_purchasable() && $product->is_in_stock()){$row['product']=$product->get_permalink();break;}}
 $out['issues'][$slug]=$row;
}
foreach(['anonyme'=>0,'a-carte'=>$profiles['A-CARTE'],'p-numero'=>$profiles['P-NUMERO']] as $label=>$uid){wp_set_current_user($uid);
 foreach($out['issues'] as $slug=>$row){$p=get_post($row['id']);$d=Imagine\Site\Paywall::decisionPdf($p);$expected=['pdf'=>$d['complet'],'motif_pdf'=>$d['motif'],'owned'=>$d['complet'],'statuses'=>[]];
 foreach(Imagine\Site\AchatsNumeros::droits($uid) as $right){if(($right['numero']??'')===(string)$p->ID){$expected['owned']=true;}}
 foreach($row['articles'] as $a){$decision=Imagine\Site\Paywall::decision(get_post($a['id']));$expected['statuses'][(string)$a['id']]=Imagine\Theme\imagine_access_status($decision);}
 $out['expected'][$label][$slug]=$expected;}}
echo wp_json_encode($out);
'''

def require_private_markers(inventory):
    for issue in inventory['issues'].values():
        for article in issue['articles']:
            if not article['markers'] or not all(isinstance(m, str) and m.strip() for m in article['markers']):
                raise AssertionError('Fixture sans marqueur de corps non vide : ' + str(article['id']))


def run(phase='final'):
    work.guard()
    inventory=work.wp(INVENTORY)
    require_private_markers(inventory)
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients={'anonyme':None,'a-carte':http.login(accounts['A-CARTE']),'p-numero':http.login(accounts['P-NUMERO'])}
    checks, responses={}, {}
    for label, client in clients.items():
        for slug, issue in inventory['issues'].items():
            prefix=label+':'+slug+':'
            expected=inventory['expected'][label][slug]
            code, headers, text=http.fetch(issue['path'], client)
            soup=BeautifulSoup(text,'html.parser')
            checks[prefix+'HTTP200']=code==200
            checks[prefix+'HTML5']=not validate_html(text)
            checks[prefix+'cache_prive']='private' in headers.get('cache-control','') and 'no-store' in headers.get('cache-control','')
            checks[prefix+'sommaire_complet']= [int(e['data-imagine-id']) for e in soup.select('#imagine-contents-list > li')] == [a['id'] for a in issue['articles']]
            for article in issue['articles']:
                badge=soup.select_one('#imagine-contents-list [data-imagine-id="'+str(article['id'])+'"] [data-imagine-access]')
                status=expected['statuses'][str(article['id'])]
                checks[prefix+'statut:'+str(article['id'])]=bool(badge and badge.get('data-imagine-access')==status['code'] and badge.get_text(strip=True)==status['label'])
                acode, _, article_html = http.fetch(article['path'], client)
                body = BeautifulSoup(article_html, 'html.parser').select_one('.imagine-paywall-body')
                article_text = body.get_text(' ', strip=True) if body else ''
                private_markers = article['markers']
                checks[prefix+'destination:'+str(article['id'])] = acode == 200 and bool(body) and (
                    all(marker in article_text for marker in private_markers) if status['code'] != 'reserve'
                    else all(marker not in article_html for marker in private_markers))
            checks[prefix+'aucun_corps_article']=all(marker not in text for a in issue['articles'] for marker in a['markers'])
            free=[a for a in issue['articles'] if expected['statuses'][str(a['id'])]['code']=='libre']
            feature=soup.select_one('[data-imagine-free-article]')
            checks[prefix+'article_libre_mis_en_avant']=bool(feature and int(feature['data-imagine-free-article'])==free[0]['id']) if free else feature is None
            audio=soup.select_one('section[aria-labelledby="imagine-audio-contents"]')
            checks[prefix+'emplacement_audio_sans_fichier']=bool(audio and not audio.select('audio,source,iframe,a[href]') and 'Sommaire audio' in audio.get_text())
            buy=soup.select_one('a[data-imagine-buy]')
            checks[prefix+'achat_selon_possession']=bool(buy)==bool(not expected['owned'] and issue['product'])
            if buy:
                checks[prefix+'achat_vrai_produit_C14']=buy.get('href')==issue['product'] and buy.get_text(strip=True)=='Acheter ce numéro'
            pdf=soup.select_one('a[data-imagine-pdf]')
            checks[prefix+'PDF_selon_decision']=bool(pdf)==expected['pdf']
            if pdf:
                checks[prefix+'PDF_route_C11']=parse_qs(urlsplit(pdf['href']).query).get('imagine_pdf')==[str(issue['id'])]
                status, pdfheaders, data=http.fetch('/?imagine_pdf='+str(issue['id']), client)
                checks[prefix+'PDF_reel_autorise']=status==200 and pdfheaders.get('content-type','').startswith('application/pdf') and data.startswith('%PDF-')
            else:
                checks[prefix+'aucune_adresse_ni_indice_PDF']='imagine_pdf=' not in text and 'data-imagine-pdf' not in text and '.pdf' not in text and 'PDF' not in soup.select_one('main').get_text()
                denied_code, denied_headers, denied = http.fetch('/?imagine_pdf='+str(issue['id']), client)
                checks[prefix+'PDF_route_serveur_refusee']=denied_code==200 and not denied_headers.get('content-type','').startswith('application/pdf') and not denied.startswith('%PDF-')
            checks[prefix+'pas_de_chemin_prive']='imagine-private-pdf' not in text and '_imagine_pdf_blob' not in text
            responses[prefix]={'path':issue['path'],'status':code,'sha256':hashlib.sha256(text.encode()).hexdigest(),'article_count':len(issue['articles']),'pdf_allowed':expected['pdf'],'pdf_motif':expected['motif_pdf']}
    result={'scope':'imagine-test-demo','at':datetime.now(timezone.utc).isoformat(),'total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if v is not True],'responses':responses}
    PROOF.mkdir(exist_ok=True,parents=True)
    (PROOF/('http-'+phase+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'phase':phase,'total':result['total'],'failures':result['failures']},ensure_ascii=False))
    if result['failures']: raise SystemExit(1)
    return result

if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'final')
