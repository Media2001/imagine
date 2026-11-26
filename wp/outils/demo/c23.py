"""C23 : commande visiteur GET, sessions préparées en mémoire hors commande."""
import html
import json
import re
import unicodedata
import sys
from pathlib import Path
from datetime import datetime, timezone
import hashlib
from urllib.parse import urlencode, urlsplit, urljoin
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler
sys.dont_write_bytecode = True
BASE = 'http://192.168.129.32:8085'
PROOF = Path(__file__).resolve().parents[3] / 'production/C-23'
PUBLICS = ['anonyme', 'connecte-sans-abonnement', 'decouverte-epuisee', 'acheteur-autre-numero', 'faux-robot']

def canonical(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    try:
        text = json.dumps(json.loads(text), ensure_ascii=False)
    except (ValueError, TypeError):
        pass
    text = text.replace('<![CDATA[','').replace(']]>','')
    text = html.unescape(text)
    text = html.unescape(re.sub(r'<[^>]*>', ' ', text))
    return ' '.join(unicodedata.normalize('NFC', text).split())

def assess(status, body, witnesses, present=None, expected=(200,), positive=False):
    text = canonical(body)
    found = [w for w in witnesses if canonical(w) in text]
    exists = present is None or canonical(present) in text
    errors = any(x in text for x in ('Fatal error', 'Uncaught Error', 'critical error', 'Warning:'))
    return {'ok': status in expected and exists and not errors and (bool(found) if positive else not found),
            'leak': bool(found) and not positive, 'witnesses_found': len(found), 'surface_present': exists}


def search_results_body(body):
    main=re.search(rb'<main\b[^>]*>(.*?)</main>',body,re.S|re.I)
    if not main:
        raise ValueError('Recherche sans résultat inspectable')
    return re.sub(rb'<form\b.*?</form>|<h1\b.*?</h1>',b'',main.group(1),flags=re.S|re.I)


def validate_path(path):
    if (not isinstance(path, str) or not path.startswith('/') or path.startswith('//')
        or '\\' in path or any(ord(c) < 32 for c in path) or urlsplit(path).netloc):
        raise ValueError('Chemin hors démonstration refusé')
    return path


class DemoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(urljoin(req.full_url, newurl))
        if target.scheme != 'http' or target.netloc != '192.168.129.32:8085':
            raise ValueError('Redirection hors démonstration refusée')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(path, headers=None):
    # Seul transport de la commande : GET, jamais de corps, POST, CLI ou écriture distante.
    validate_path(path)
    client = build_opener(DemoRedirect())
    try:
        response = client.open(Request(BASE + path, headers={'User-Agent':'Imagine-C23/1.0',
            **(headers or {})}, method='GET'), timeout=45)
    except HTTPError as error:
        response = error
    with response:
        return response.code, {k.lower():v for k,v in response.headers.items()}, response.read()


def build_routes(f):
    a, n, pdf = str(f['article']), str(f['issue']), str(f['pdf'])
    slug = f['issue_slug']
    routes = []
    def add(name, path, present=None, denied=False, statuses=(200,), **kw):
        routes.append(dict(name=name,path=path,present=present,denied=denied,statuses=list(statuses),**kw))
    title = f.get('article_title', slug)
    add('article', f['article_path'], title)
    add('accueil', '/', 'C08', structure='cards')
    add('numero', f['issue_path'], title, structure='cards')
    add('kiosque', '/numeros/', f.get('issue_title','Numéro fictif 4'), structure='cards')
    add('thematique', f['term_path'], title, structure='cards')
    add('archives', f['posts_archive'], title, structure='archive')
    add('rest-contenu', '/wp-json/wp/v2/posts/'+a, title, structure='rest-item')
    add('rest-collection', '/wp-json/wp/v2/posts?include='+a+'&_embed=1', title, structure='rest-list')
    add('rest-champs', '/wp-json/wp/v2/posts/'+a+'?_fields=id,content,excerpt', str(f['article']), structure='rest-item')
    add('rest-route', '/?rest_route=/wp/v2/posts/'+a, title, structure='rest-item')
    add('rest-embed', '/wp-json/wp/v2/posts/'+a+'?context=embed', title, structure='rest-item')
    add('rest-recherche', '/wp-json/wp/v2/search?search='+urlencode({'s':slug})[2:], title, structure='rest-list')
    add('rest-revisions', '/wp-json/wp/v2/posts/'+a+'/revisions', denied=True, statuses=(401,403), structure='rest-error')
    add('rest-edition', '/wp-json/wp/v2/posts/'+a+'?context=edit', denied=True, statuses=(401,403), structure='rest-error')
    for feed in ['rss2','rss','atom','rdf']:
        add(feed, '/?feed='+feed+'&posts_per_rss=100', f['article_path'], structure='feed')
    add('flux-article', '/?feed=rss2&post_type=post&include='+a, f['article_path'], structure='feed')
    add('oembed', '/wp-json/oembed/1.0/embed?'+urlencode({'url':BASE+f['article_path']}), title, structure='oembed')
    add('embed', f['article_path']+'embed/', title)
    add('recherche', '/?'+urlencode({'s':slug}), title, structure='cards')
    add('recherche-corps', '/?'+urlencode({'s':'CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1'}), 'Aucun résultat', reflected=True)
    add('rest-recherche-corps', '/wp-json/wp/v2/search?search=CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1', '[]', structure='empty-search')
    add('rest-posts-corps', '/wp-json/wp/v2/posts?search=CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1', '[]', structure='empty-search')
    add('partage', f['article_path'], title, structure='sharing')
    add('extrait-automatique', f['auto_path'], 'C08', allow_buyer_c08=True)
    add('c08-article', '/?p='+str(f['c08']), 'C08', allow_buyer_c08=True)
    add('c12-epuisee', '/?p='+str(f['c12']), 'C12', discovery=True)
    add('apercu', '/?p='+a+'&preview=true', title)
    add('multipage', f['article_path']+'?page=2', title, statuses=(200,404))
    add('amp-inactif', f['article_path']+'?amp=1', title)
    add('prefetch', f['article_path'], title, extra={'Sec-Purpose':'prefetch'})
    add('conditionnelle', f['article_path'], title, extra={'If-None-Match':'"c23"','If-Modified-Since':'Tue, 01 Jan 2030 00:00:00 GMT'})
    if f.get('sitemap_enabled',True):
        add('sitemap', '/wp-sitemap.xml', 'wp-sitemap-posts-post-1.xml', structure='sitemap')
        add('sitemap-articles', '/wp-sitemap-posts-post-1.xml', f['article_path'], structure='sitemap')
        add('sitemap-numeros', '/wp-sitemap-posts-imagine_numero-1.xml', f['issue_path'], structure='sitemap')
    else:
        for name,path in [('sitemap','/wp-sitemap.xml'),('sitemap-articles','/wp-sitemap-posts-post-1.xml'),('sitemap-numeros','/wp-sitemap-posts-imagine_numero-1.xml')]:
            add(name,path,denied=True,statuses=(404,),native_disabled=True)
    add('sitemap-pdf', '/wp-sitemap-posts-attachment-1.xml', denied=True, statuses=(404,))
    add('pdf-telechargement', '/?imagine_pdf='+n, f.get('issue_title','Numéro fictif 4'), structure='pdf-denied')
    add('pdf-direct', '/wp-content/uploads/imagine-demo/'+slug+'.pdf', denied=True, statuses=(403,404))
    add('pdf-ancienne-source', '/wp-content/imagine-demo-build/assets/'+slug+'.pdf', denied=True, statuses=(403,404))
    add('pdf-piece-jointe', '/?attachment_id='+pdf, denied=True, statuses=(404,))
    add('pdf-slug', '/'+slug+'-pdf/', denied=True, statuses=(404,))
    add('pdf-media-rest', '/wp-json/wp/v2/media/'+pdf, denied=True, statuses=(401,403,404), structure='rest-error')
    add('pdf-media-route', '/?rest_route=/wp/v2/media/'+pdf, denied=True, statuses=(401,403,404), structure='rest-error')
    add('pdf-media-inclusion', '/wp-json/wp/v2/media?include='+pdf, '[]', structure='empty-search')
    add('pdf-medias-liste', '/wp-json/wp/v2/media?media_type=application&per_page=100', '[]', structure='empty-search')
    add('partenaires', '/partenaires/', 'Partenaires', structure='cards')
    for partner in f['partners']:
        add('partenaire-'+str(partner['id']), partner['path'], partner['title'])
    add('newsletters', '/nos-newsletters/', 'newsletters')
    add('mon-compte', f.get('account_path','/mon-compte/'), 'Mon compte')
    # Toutes les nouvelles entrées d'administration/export depuis C08 : lecture GET
    # sans les nonces, sans jamais déclencher une exportation/effacement/gel.
    for page in ['imagine-reglages','imagine-liste-envoi','imagine-echeances','imagine-commande-client',
                 'imagine-justificatifs','imagine-extractions','imagine-tableau-bord']:
        add('admin-'+page, '/wp-admin/admin.php?page='+page, denied=True, statuses=(200,302,403), structure='admin-denied')
    add('export-c21', '/wp-admin/export-personal-data.php', denied=True, statuses=(200,302,403), structure='admin-denied')
    add('effacement-c21', '/wp-admin/erase-personal-data.php', denied=True, statuses=(200,302,403), structure='admin-denied')
    for post in f.get('posts', []):
        if post['reserved'] and post['id'] not in [f['article'], f['auto'], f['c08'], f['c12']]:
            add('article-inventorie-'+str(post['id']), post['path'], post['title'], issue=post['issue'])
    return routes


def structure_ok(route, status, body, f):
    kind = route.get('structure')
    text = body.decode('utf-8','replace')
    if kind == 'pdf-denied':
        return b'%PDF-' not in body and (b'data-imagine-pdf-bloc=' in body or b'imagine-contents-list' in body and b'data-imagine-pdf-download' not in body)
    if kind == 'sharing':
        return all(x in text for x in ['og:description','twitter:description','application/ld+json','isAccessibleForFree'])
    if kind == 'cards':
        return bool(re.search(r'<a\b[^>]*href=',text)) and ('data-imagine-id=' in text or route['name'] in ['kiosque','partenaires','numero'])
    if kind == 'archive':
        main=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)
        return bool(main and re.search(r'<h2><a href=',main.group(1)))
    if kind == 'feed':
        return ('<item' in text or '<entry' in text) and '<html' not in text[:100]
    if kind == 'sitemap':
        return ('<sitemapindex' in text or '<urlset' in text) and '<loc>' in text
    if kind == 'admin-denied':
        return status == 403 or ('woocommerce-MyAccount' in text or 'id="loginform"' in text) and 'id="wpadminbar"' not in text
    if kind in ['rest-item','rest-list','rest-error','oembed','empty-search']:
        try:
            data = json.loads(body)
        except (ValueError,UnicodeError):
            return False
        if kind == 'rest-item':
            return isinstance(data,dict) and data.get('id') == f['article']
        if kind == 'rest-list':
            return isinstance(data,list) and bool(data) and any(p.get('id') == f['article'] for p in data)
        if kind == 'rest-error':
            return isinstance(data,dict) and isinstance(data.get('code'),str) and 'data' in data
        if kind == 'oembed':
            return isinstance(data,dict) and data.get('type') == 'rich' and bool(data.get('html'))
        return data == []
    return True


def matrix(context, label='matrice'):
    f, sessions = context['fixture'], context['sessions']
    if f.get('scope') != 'imagine-test-demo' or f.get('base') != BASE or not all(f.get('guards',{}).values()):
        raise ValueError('Identité/coupe-circuits non prouvés')
    if not f['posts'] or not f['issues'] or str(f['issue']) in f['buyer_issues'] or not f['buyer_issues']:
        raise ValueError('Inventaire ou témoin acheteur invalide')
    routes = build_routes(f)
    if not routes or len({r['name'] for r in routes}) != len(routes):
        raise ValueError('Inventaire des voies invalide')
    # Les témoins sont déjà dans les vrais corps, jamais plantés par cette commande.
    markers = []
    for p in f['posts']:
        if p['reserved']:
            matches = re.findall(r'CONTENU_FICTIF_RESERVE_[A-Z0-9_-]+|Les lucioles violettes de C08 gardent le secret du village fictif\.|Les lanternes argentées de C08 composent un autre récit fictif\.|Le texte réservé C12 [^<]+', p['body'])
            markers.extend((w,p['issue']) for w in matches)
    primary = 'CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1'
    if not any(w == primary for w,_ in markers) or not any('lucioles' in w for w,_ in markers):
        raise ValueError('Témoins existants absents')
    results=[]
    def probe(name, public, route, headers, witnesses, positive=False, pdf_hash=None):
        try:
            status, hs, body = fetch(route['path'], headers)
            inspected=body
            if route.get('reflected'):
                # La recherche réaffiche légitimement le terme ; inspecter les cartes et leurs IDs.
                inspected=search_results_body(body)
            present = route.get('present')
            # Une marque d'attribut doit exister dans le HTML brut, pas dans le texte visible.
            attr = present and present.startswith('data-')
            verdict=assess(status, inspected, witnesses, None if attr else present, route.get('statuses',[200]),positive)
            if attr:
                verdict['surface_present'] = present.encode() in body
                verdict['ok'] &= verdict['surface_present']
            verdict['structure'] = True if positive else structure_ok(route,status,body,f)
            verdict['ok'] &= verdict['structure']
            if route.get('reflected'):
                ids=re.findall(rb'data-imagine-id="(\d+)"',body)
                verdict['structure'] = str(f['article']).encode() not in ids
                verdict['ok'] &= verdict['structure']
            if route.get('discovery') and public == 'decouverte-epuisee':
                verdict['ok'] &= b'data-imagine-bloc="decouverte_epuisee"' in body
            if pdf_hash:
                verdict['ok'] &= hashlib.sha256(body).hexdigest() == pdf_hash and hs.get('content-type','').startswith('application/pdf')
            row=dict(name=name,public=public,path=route['path'],status=status,bytes=len(body),
                     body_sha256=hashlib.sha256(body).hexdigest(),**verdict)
        except Exception as error:
            row=dict(name=name,public=public,path=route['path'],status=0,ok=False,leak=False,error=type(error).__name__)
        results.append(row)
        return row
    # Les cookies/nonces restent en mémoire et n'entrent jamais dans le reçu.
    publics={'anonyme':{},'faux-robot':{'User-Agent':'Googlebot/2.1','X-Forwarded-For':'66.249.66.1','X-Real-IP':'66.249.66.1'}}
    for public in PUBLICS[1:4]+['abonne-actif']:
        session=sessions[public]
        headers={'Cookie':session['cookie'],'X-WP-Nonce':session['nonce']}
        publics[public]=headers
        identity=probe('identite-REST','controle-'+public,dict(path='/wp-json/wp/v2/users/me',present=None,statuses=[200]),headers,[])
        status,_,body=fetch('/wp-json/wp/v2/users/me',headers)
        valid=status==200 and json.loads(body).get('id')==session['id']
        identity['ok'] &= valid
    # Inverse AVANT anonymes : les réponses complètes ne doivent pas contaminer les suivantes.
    probe('inverse-article','abonne-actif',dict(path=f['article_path'],present=f['article_title']),publics['abonne-actif'],[primary],True)
    probe('inverse-pdf','abonne-actif',dict(path='/?imagine_pdf='+str(f['issue']),present=None),publics['abonne-actif'],['IMAGINE - DEMONSTRATION FICTIVE'],True,f['pdf_sha256'])
    probe('inverse-C08','abonne-actif',dict(path='/?p='+str(f['c08']),present='C08'),publics['abonne-actif'],['Les lucioles violettes de C08 gardent le secret du village fictif.'],True)
    for route in routes:
        cells=[]
        for public in PUBLICS:
            denied_markers=[w for w,issue in markers if public!='acheteur-autre-numero' or str(issue) not in f['buyer_issues']]
            denied_markers+=['IMAGINE - DEMONSTRATION FICTIVE','%PDF-']
            effective=dict(route)
            # C14 est un vrai droit : le numéro T1 possédé peut être lu, mais aucun témoin T4 ne doit sortir.
            if public=='acheteur-autre-numero' and (route.get('allow_buyer_c08') or str(route.get('issue','')) in f['buyer_issues']):
                effective['present']=route['present']
            row=probe(route['name'],public,effective,{**publics[public],**route.get('extra',{})},denied_markers)
            cells.append('FUITE' if row['leak'] else 'OK' if row['ok'] else 'ECHEC')
        print(route['name']+' | '+' | '.join(cells),flush=True)
    # Deuxième faux moteur et contrôle du numéro effectivement acheté.
    probe('faux-bing','faux-robot',dict(path=f['article_path'],present=f['article_title']),{'User-Agent':'bingbot/2.0'},[w for w,_ in markers]+['%PDF-'])
    probe('inverse-achat-C14','acheteur-autre-numero',dict(path='/?p='+str(f['c08']),present='C08'),publics['acheteur-autre-numero'],['Les lucioles violettes de C08 gardent le secret du village fictif.'],True)
    leaks=sum(bool(r['leak']) for r in results)
    failures=sum(not r['ok'] for r in results)
    summary=f'ETANCHEITE : {len(results)} contrôles, {leaks} fuites — '+('PASS' if not failures else 'FAIL')
    receipt=dict(scope=f['scope'],at=datetime.now(timezone.utc).isoformat(),routes=len(routes),publics=PUBLICS,
                 total=len(results),leaks=leaks,failures=failures,summary=summary,results=results,
                 fixture_sha256=hashlib.sha256(json.dumps(f,sort_keys=True).encode()).hexdigest())
    PROOF.mkdir(parents=True,exist_ok=True)
    (PROOF/(label+'.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    (PROOF/(label+'.md')).write_text('# Matrice C-23\n\nVoie | '+' | '.join(PUBLICS)+'\n---|'+'---|'*5+'\n'+
        '\n'.join(r['name']+' | '+' | '.join(next(('FUITE' if x['leak'] else 'OK' if x['ok'] else 'ECHEC') for x in results if x['name']==r['name'] and x['public']==p) for p in PUBLICS) for r in routes)+'\n\n'+summary+'\n',encoding='utf-8')
    print(summary,flush=True)
    return 0 if not failures else 1


if __name__ == '__main__':
    try:
        if sys.argv[1:] and (len(sys.argv)!=2 or not re.fullmatch('[a-z0-9-]+',sys.argv[1])):
            raise ValueError('Nom de reçu refusé')
        context=json.load(sys.stdin)
        raise SystemExit(matrix(context,sys.argv[1] if len(sys.argv)>1 else 'matrice'))
    except Exception as error:
        print('ETANCHEITE : 0 contrôles, 0 fuites — FAIL ; prérequis '+type(error).__name__)
        raise SystemExit(1)
