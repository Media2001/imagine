"""C26 extension de la commande visiteur C23 ; transport exclusivement GET local."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode, quote
import c23
PROOF = Path(__file__).resolve().parents[3] / 'production/C-26'
FAMILIES = ['agenda', 'personnalisation', 'retractation', 'sujet']
MUTATIONS = FAMILIES + ['cooperateurs', 'cooperative', 'archive', 'autorisation-b06']


def source_hashes():
    root = Path(__file__).resolve().parents[3]
    files = [p for folder in ['wp/outils/demo','wp/tests/demo']
             for p in (root/folder).glob('c26*') if p.is_file()]
    files += [root/name for name in ['wp/outils/demo/c23.py', 'wp/outils/demo/c23-inventaire.php',
        'wp/outils/demo/c23-preparer.py', 'wp/tests/demo/c23-tests.py']]
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def routes(f):
    if not f.get('pages') or not f.get('events') or any(not f.get(k) for k in ['registration', 'subject', 'order']):
        raise ValueError('C26 inventaire incomplet')
    rows = []
    def add(name, family, kind, path, title=None, statuses=(200,), **kw):
        c23.validate_path(path)
        rows.append(dict(name=name, family=family, kind=kind, path=path, title=title, statuses=list(statuses), **kw))
    for family, items, rest in [('cooperative', f['pages'], 'pages'), ('agenda', f['events'], 'imagine_evenement')]:
        for p in items:
            prefix = family + '-' + str(p['id'])
            add(prefix+'-page', family, 'page', p['path'], p['title'])
            add(prefix+'-rest', family, 'rest', '/wp-json/wp/v2/'+rest+'/'+str(p['id']), p['title'], object_id=p['id'])
            add(prefix+'-collection', family, 'rest', '/wp-json/wp/v2/'+rest+'?include='+str(p['id']), p['title'], object_id=p['id'])
            add(prefix+'-alias', family, 'rest', '/?rest_route=/wp/v2/'+rest+'/'+str(p['id']), p['title'], object_id=p['id'])
            add(prefix+'-oembed', family, 'oembed', '/wp-json/oembed/1.0/embed?'+urlencode({'url':c23.BASE+p['path']}), p['title'])
            add(prefix+'-embed', family, 'embed', p['path']+'embed/', p['title'])
            add(prefix+'-search', family, 'search', '/?'+urlencode({'s':p['title'], 'post_type':'page' if rest=='pages' else rest}), p['title'], target_path=p['path'])
    add('agenda-archive', 'agenda', 'agenda-archive', '/evenements/', 'Agenda', events=f['events'])
    add('agenda-flux', 'agenda', 'feed', '/?feed=rss2&post_type=imagine_evenement&posts_per_rss=100', object_id=f['events'][0]['id'])
    for family, typ, ident in [('agenda', 'imagine_inscription', f['registration']), ('sujet', 'imagine_sujet', f['subject'])]:
        add(family+'-prive-page', family, 'private-page', '/?p='+str(ident), statuses=(200,404))
        add(family+'-prive-rest', family, 'rest-denied', '/wp-json/wp/v2/'+typ+'/'+str(ident), statuses=(404,))
        add(family+'-prive-collection', family, 'rest-denied', '/wp-json/wp/v2/'+typ, statuses=(404,))
        add(family+'-prive-feed', family, 'private-feed', '/?feed=rss2&post_type='+typ, statuses=(200,404))
        add(family+'-prive-search', family, 'search', '/?'+urlencode({'s':f['markers'][family]}), reflected=f['markers'][family])
        add(family+'-admin', family, 'admin', '/wp-admin/edit.php?post_type='+typ, statuses=(200,403))
        add(family+'-admin-detail', family, 'admin', '/wp-admin/post.php?post='+str(ident)+'&action=edit', statuses=(200,403))
    account = f.get('account_path', '/my-account/')
    add('personnalisation-compte', 'personnalisation', 'account', account, 'Mon compte')
    add('personnalisation-utilisateur-rest', 'personnalisation', 'rest-denied', '/wp-json/wp/v2/users/'+str(f.get('owner', 999999))+'?context=edit', statuses=(401,403))
    add('personnalisation-reglages', 'personnalisation', 'admin', '/wp-admin/admin.php?page=imagine-reglages', statuses=(200,403))
    add('personnalisation-action-GET', 'personnalisation', 'refusal', '/wp-admin/admin-post.php?action=imagine_personnalisation', statuses=(403,))
    add('retractation-compte-tiers', 'retractation', 'account', account+'?imagine_retractation='+str(f['order']), 'Mon compte')
    add('retractation-commande-tiers', 'retractation', 'account', account+'view-order/'+str(f['order'])+'/', 'Mon compte')
    add('retractation-admin', 'retractation', 'admin', '/wp-admin/admin.php?page=imagine-retractations', statuses=(200,403))
    add('retractation-rest', 'retractation', 'rest-denied', '/wp-json/wc/v3/orders/'+str(f['order']), statuses=(401,403,404))
    add('sujet-action-GET', 'sujet', 'refusal', '/wp-admin/admin-post.php?action=imagine_sujet', statuses=(405,))
    add('agenda-action-GET', 'agenda', 'refusal', '/wp-admin/admin-post.php?action=imagine_agenda', statuses=(403,))
    for name in ['export-personal-data', 'erase-personal-data']:
        add('privacy-'+name, 'personnalisation', 'admin', '/wp-admin/'+name+'.php', statuses=(200,403))
    add('commun-accueil', 'commun', 'common-page', '/')
    add('commun-flux-articles', 'commun', 'common-feed', '/?feed=rss2&posts_per_rss=100')
    add('commun-rest-articles', 'commun', 'rest', '/wp-json/wp/v2/posts?per_page=100', object_id=f.get('article',42))
    add('commun-rest-pages', 'commun', 'rest', '/wp-json/wp/v2/pages?per_page=100', object_id=f['pages'][0]['id'])
    for family in ['personnalisation','retractation']:
        add(family+'-search',family,'search','/?'+urlencode({'s':f['markers'][family]}),reflected=f['markers'][family])
    return rows


def search_body(body, term):
    body = c23.search_results_body(body, term)
    # Seule la variante native encodée du lien RSS réfléchi, pas la tête entière.
    expected = (c23.BASE+'/search/'+quote(term,safe='')+'/feed/rss2/').encode()
    def feed(match):
        tag = match[0]
        if b'application/rss+xml' in tag and expected in tag:
            tag = re.sub(rb'(\btitle=[\"\'])([^\"\']*)([\"\'])',lambda m:m[1]+m[2].replace(term.encode(),b'[terme recherche]')+m[3],tag)
        return tag
    return re.sub(rb'<link\b[^>]*>',feed,body,flags=re.I)


def assess(route, response, markers):
    status, _, body = response
    inspected = search_body(body, route['reflected']) if route.get('reflected') else body
    result = c23.assess_response(response, markers, expected=route['statuses'], inspected=inspected)
    text = body.decode('utf-8', 'replace')
    kind = route['kind']
    if kind in ['rest', 'rest-denied', 'oembed']:
        try:
            data = json.loads(body)
        except (ValueError, UnicodeError):
            data = None
        if kind == 'rest-denied':
            exists = isinstance(data, dict) and isinstance(data.get('code'), str) and isinstance(data.get('data'), dict)
        elif kind == 'oembed':
            exists = isinstance(data, dict) and data.get('type') == 'rich' and bool(data.get('html')) and display_title(route['title']) in display_title(data.get('title', ''))
        else:
            exists = any(isinstance(x, dict) and x.get('id') == route.get('object_id') for x in (data if isinstance(data, list) else [data]))
    elif kind == 'feed':
        exists = ('<item>' in text or '<entry>' in text) and all(p in text for p in ['<rss', '/evenements/'])
    elif kind == 'agenda-archive':
        main = re.search(r'<main\b[^>]*>(.*?)</main>', text, re.S)
        exists = bool(main and '<h1>Agenda</h1>' in main[1]
            and all('id="agenda-'+group+'"' in main[1] for group in ['futurs','passes'])
            and all('data-evenement="'+str(e['id'])+'"' in main[1]
                    and e['path'] in main[1] for e in route['events']))
    elif kind == 'common-feed':
        exists = ('<item>' in text or '<entry>' in text) and '<rss' in text
    elif kind == 'private-feed':
        exists = ('<rss' in text or '<feed' in text) if status == 200 else '<html' in text.lower()
    elif kind == 'admin':
        exists = c23.structure_ok({'structure':'admin-denied'}, status, body, {})
    elif kind == 'refusal':
        exists = bool(body) and ('refus' in text.lower() or 'error-page' in text)
    elif kind == 'private-page':
        exists = '<main' in text and ('<h1' in text or '<h2' in text)
    elif kind == 'embed':
        exists = 'wp-embed' in text and display_title(route['title']) in display_title(body)
    elif kind == 'search':
        main = re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)
        if route.get('reflected'):
            exists = bool(main and 'Aucun résultat pour votre recherche.' in main[1])
        else:
            exists = bool(main and re.search(r'<h2\b[^>]*>\s*<a\b[^>]*href=[\"\'][^\"\']*'+re.escape(route['target_path']),main[1]))
    elif kind == 'account':
        exists = '<main' in text and ('woocommerce-MyAccount' in text or 'id="loginform"' in text or 'woocommerce-form-login' in text and 'woocommerce-login-nonce' in text)
    elif kind == 'common-page':
        exists = '<main' in text and 'data-imagine-id=' in text
    else:
        main = re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S)
        h1 = re.search(r'<h1\b[^>]*>(.*?)</h1>',main[1],re.S) if main else None
        exists = bool(h1 and display_title(route.get('title',''))==display_title(h1[1]))
    result['surface_present'] = bool(exists)
    result['ok'] &= bool(exists)
    return result


def privacy_assess(payload, markers, positive=False):
    valid = isinstance(payload, dict) and isinstance(payload.get('data'), list) and payload.get('done') is True
    result = c23.assess(200, json.dumps(payload, ensure_ascii=False), markers, positive=positive)
    result['surface_present'] = valid
    result['ok'] &= valid
    return result


def display_title(text):
    return c23.canonical(text).replace("'", '’')


def cooperator_expected(f):
    """Oracle documentaire : P-COOP seul possède le statut ; rôles livrés lus bruts.

    Ni autorise(), ni la liste native observée, ni un statut modifié ne définissent
    l'attendu. Les autres personnages C09 sont lecteurs sans statut B06.
    """
    roles = f['cooperator_roles']
    if (not isinstance(roles, list) or len(roles) != len(set(roles))
            or not set(roles) <= {'administrator', 'editor', 'shop_manager'}):
        roles = []  # Même défaut prudent documenté : réglage invalide fermé.
    return [public for public, actor in f['cooperator_actors'].items()
            if actor['code'] == 'P-COOP' or set(actor['roles']) & set(roles)]


def validate_cooperator(f):
    expected = cooperator_expected(f)
    if (set(f['cooperator_publics']) != set(expected)
            or len(f['cooperator_publics']) != len(expected)
            or any(a['status'] is not (a['code'] == 'P-COOP')
                   for a in f['cooperator_actors'].values())):
        raise ValueError('B06 décision native / personnages documentés divergents')
    return expected


def denied_markers(f, public):
    markers = list(f['extension']['markers'].values())
    # Valider TOUS les corps, y compris ceux légitimement lisibles par ce public.
    for p in f['posts']:
        if not p['reserved']:
            continue
        found = c23.reserved_witnesses(p['body'])
        if public != 'abonne-actif' and (public != 'acheteur-autre-numero'
                or str(p['issue']) not in f['buyer_issues']):
            markers.extend(found)
    # Un abonnement ou achat au numéro ne donne aucun droit coopérateur, et vice versa.
    for p in f.get('cooperator_pages', []):
        found = re.findall(r'C23_COOP_TEMOIN_[0-9]+', p['body'])
        if len(found) != 1:
            raise ValueError('B06 contenu sans témoin reconnu')
        if public not in f.get('cooperator_publics', []):
            markers.extend(found)
    return list(dict.fromkeys(markers))


def matrix(context, label):
    f, sessions = context['fixture'], context['sessions']
    if f.get('scope') != 'imagine-test-demo' or f.get('base') != c23.BASE:
        raise ValueError('C26 cible refusée')
    validate_cooperator(f)
    denied_markers(f, 'anonyme')  # Échec de prérequis avant toute requête.
    c23.PROOF = PROOF
    base_code = c23.matrix(context, label+'-c23')
    extension = f['extension']
    catalog = routes(extension)
    publics = c23.audience_order(f) + ['abonne-actif']

    results = []
    def probe(item):
        r, public = item
        session = sessions.get(public)
        headers = {'Cookie':session['cookie'], 'X-WP-Nonce':session['nonce']} if session else {}
        if public == 'faux-robot':
            headers = {'User-Agent':'Googlebot/2.1', 'X-Forwarded-For':'66.249.66.1'}
        try:
            response = c23.fetch(r['path'], headers)
            status, _, body = response
            verdict = assess(r, response, denied_markers(f, public))
            return dict(name=r['name'], family=r['family'], public=public, path=r['path'], status=status,
                        bytes=len(body), body_sha256=hashlib.sha256(body).hexdigest(), **verdict)
        except Exception as e:
            return dict(name=r['name'], family=r['family'], public=public, path=r['path'], status=0,
                        ok=False, leak=False, surface_present=False, error=type(e).__name__)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, [(r,p) for r in catalog for p in publics]))
    failures = sum(not r['ok'] for r in results)
    leaks = sum(bool(r['leak']) for r in results)
    receipt = dict(scope=f['scope'], coverage='C26-nouvelles-sorties', routes=catalog, publics=publics,
                   total=len(results), failures=failures, leaks=leaks, results=results, c23_exit=base_code)
    (PROOF/(label+'.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    (PROOF/(label+'.md')).write_text('# Matrice C26\n\nVoie | '+' | '.join(publics)+'\n---|'+'---|'*len(publics)+'\n'+'\n'.join(r['name']+' | '+' | '.join('OK' if next(x for x in results if x['name']==r['name'] and x['public']==p)['ok'] else 'ECHEC' for p in publics) for r in catalog)+'\n',encoding='utf-8')
    print(f'C26 : {len(results)} contrôles, {leaks} fuites, {failures} échecs ; C23 exit {base_code}', flush=True)
    return 1 if failures or base_code else 0


if __name__ == '__main__':
    import re
    if len(sys.argv) != 2 or not re.fullmatch('[a-zA-Z0-9-]+', sys.argv[1]):
        raise SystemExit(1)
    raise SystemExit(matrix(json.load(sys.stdin), sys.argv[1]))
