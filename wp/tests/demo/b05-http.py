"""B05 actual browser/HTTP probes with reversible fictional partner-body canary."""
from pathlib import Path
import hashlib, importlib.util, json, sys
from urllib.parse import urlencode, urlparse, parse_qs
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b05
BASE = 'http://192.168.129.32:8085'
OPTION = 'imagine_partenaire_du_mois'


def home_article_checks(page, partners):
    """Inspect the real list, require content, then test both exclusion rules."""
    links = page.locator('section[aria-labelledby="imagine-latest-posts"] .imagine-list a')
    anchors = links.evaluate_all('(xs)=>xs.map(a=>({href:a.href,rel:a.rel}))')
    ids = [str(p['ID']) for p in partners]
    slugs = [p['post_name'] for p in partners]
    return {
        'articles_accueil_presents': len(anchors) > 0,
        'articles_accueil_non_sponsored': len(anchors) > 0 and all('sponsored' not in a['rel'].split() for a in anchors),
        'articles_accueil_sans_partenaire': len(anchors) > 0 and all(not any(('p', x) in [(k,v) for k,values in parse_qs(urlparse(a['href']).query).items() for v in values] or ('/partenaires/' + s + '/') in a['href'] for x,s in zip(ids,slugs)) for a in anchors),
    }


def home_mutations(page, partners):
    """Browser DOM only: mutations cannot persist on the demo."""
    selector = 'section[aria-labelledby="imagine-latest-posts"] .imagine-list'
    original = page.locator(selector).inner_html()
    probes = {}
    try:
        page.locator(selector + ' a').first.evaluate('(a)=>a.rel="sponsored"')
        probes['mutation_sponsored_detectee'] = home_article_checks(page, partners)['articles_accueil_non_sponsored'] is False
        page.locator(selector).evaluate('(e,html)=>e.innerHTML=html', original)
        page.locator(selector + ' a').first.evaluate('(a,url)=>a.href=url', BASE + '/?p=' + str(partners[0]['ID']))
        probes['mutation_partenaire_detectee'] = home_article_checks(page, partners)['articles_accueil_sans_partenaire'] is False
        page.locator(selector).evaluate('(e)=>e.innerHTML=""')
        probes['mutation_liste_vide_detectee'] = not any(home_article_checks(page, partners).values())
    finally:
        page.locator(selector).evaluate('(e,html)=>e.innerHTML=html', original)
    probes['DOM_restaure'] = all(home_article_checks(page, partners).values())
    return probes


def run(label):
    b05.profils.guard('imagine-test-demo')
    assert not (b05.PROOF / (label + '.json')).exists()
    checks, blocked, pages = {}, [], {}
    baseline = b05.state()
    fixture = b05.wp(r'''global $wpdb;echo wp_json_encode(['option'=>$wpdb->get_row("SELECT * FROM {$wpdb->options} WHERE option_name='imagine_partenaire_du_mois'",ARRAY_A),
        'article'=>get_post(17), 'partners'=>get_posts(['post_type'=>'imagine_partenaire','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC'])]);''')
    partners = fixture['partners']
    assert len(partners) == 2
    one, two = partners
    def select(value):
        b05.wp('update_option("' + OPTION + '",' + str(value) + ',false);echo wp_json_encode(get_option("' + OPTION + '"));')
    try:
        # Existing B00 partners only; temporary body with preserved rel and varied anchors.
        canary = '<p><a href="https://example.org/b05-fictif" rel="noopener nofollow">Partenaire fictif externe</a> <a href="//example.org/b05-autre">Autre lien fictif</a> <a href=" https://example.org/b05-espace">Espace initial</a> <a href="https:////example.org/b05-slashes">Autorité atypique</a> <a href="/partenaires/">Interne</a> <a href="#suite">Ancre</a></p>'
        for partner in partners:
            content = partner['post_content'] + canary
            b05.wp('global $wpdb;$wpdb->update($wpdb->posts,["post_content"=>' + b05.php_json(content) + '],["ID"=>' + str(partner['ID']) + ']);clean_post_cache(' + str(partner['ID']) + ');echo wp_json_encode(true);')
        article = fixture['article']
        content = article['post_content'] + '<p><a href="https://example.org/editorial-b05" rel="noopener">Source éditoriale témoin</a></p>'
        b05.wp('global $wpdb;$wpdb->update($wpdb->posts,["post_content"=>' + b05.php_json(content) + '],["ID"=>17]);clean_post_cache(17);echo wp_json_encode(true);')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                context = browser.new_context(viewport={'width':1280,'height':1000}, locale='fr-BE')
                def route(r):
                    if r.request.url.startswith(BASE + '/'):
                        r.continue_()
                    else:
                        blocked.append(r.request.url.split('?')[0]); r.abort()
                context.route('**/*', route)
                page = context.new_page()
                def visit(key, path):
                    response = page.goto(BASE + path, wait_until='networkidle')
                    checks[key + '_HTTP200'] = response.status == 200
                    text = page.content()
                    pages[key] = {'path':path, 'sha256':hashlib.sha256(text.encode()).hexdigest(), 'status':response.status}
                    return text
                select(0)
                visit('accueil_sans', '/')
                checks['bloc_absent_sans_choix'] = page.locator('[data-imagine-partenaire-mois]').count() == 0
                for i, partner in enumerate(partners):
                    select(partner['ID'])
                    visit('accueil_' + str(i), '/')
                    block = page.locator('[data-imagine-partenaire-mois]')
                    checks['bloc_unique_choix_' + str(i)] = block.count() == 1 and block.get_attribute('data-imagine-partenaire-mois') == str(partner['ID'])
                    checks['etiquette_accueil_' + str(i)] = block.count() == 1 and block.locator('.imagine-partnership-label').inner_text() == 'Partenariat'
                    checks['conteneur_accueil_' + str(i)] = block.count() == 1 and 'imagine-partnership' in block.get_attribute('class').split()
                    checks.update({key + '_' + str(i): value for key,value in home_article_checks(page, partners).items()})
                    checks.update({key + '_' + str(i): value for key,value in home_mutations(page, partners).items()})
                visit('liste', '/partenaires/')
                checks['titre_nos_partenaires'] = page.locator('h1').inner_text() == 'Nos partenaires'
                checks['liste_deux_fiches_distinctes'] = page.locator('main .imagine-partnership[data-imagine-id]').count() == 2
                checks['etiquettes_liste'] = page.locator('main .imagine-partnership-label', has_text='Partenariat').count() == 2
                for i, partner in enumerate(partners):
                    visit('fiche_' + str(i), '/?p=' + str(partner['ID']))
                    checks['fiche_classe_et_etiquette_' + str(i)] = page.locator('main .imagine-partnership .imagine-partnership-label', has_text='Partenariat').count() == 1
                    anchors = page.locator('main .imagine-partnership a').evaluate_all('(xs)=>xs.map(a=>({href:a.href,rel:a.rel,raw:a.getAttribute("href")}))')
                    outgoing = [a for a in anchors if a['href'].startswith(('http:','https:')) and not a['href'].startswith(BASE + '/')]
                    checks['tous_sortants_sponsored_' + str(i)] = len(outgoing) == 4 and all('sponsored' in a['rel'].split() for a in outgoing)
                    checks['rel_preexistant_conserve_' + str(i)] = any(set(['sponsored','noopener','nofollow']) <= set(a['rel'].split()) for a in outgoing)
                    checks['liens_internes_non_commerciaux_' + str(i)] = all('sponsored' not in a['rel'].split() for a in anchors if a not in outgoing)
                for kind, params in [('recherche', {'s':'fictifs'}), ('recherche_type_force', {'s':'fictifs','post_type':'imagine_partenaire'}), ('flux', {'feed':'rss2'}), ('flux_type_force', {'feed':'rss2','post_type':'imagine_partenaire'})]:
                    visit(kind, '/?' + urlencode(params))
                    text = page.content()
                    checks[kind + '_sans_partenaire'] = all(p['post_title'] not in text and ('?p=' + str(p['ID'])) not in text and ('/partenaires/' + p['post_name'] + '/') not in text for p in partners)
                visit('article', '/?p=17')
                checks['fiche_article_non_sponsored'] = page.locator('main a[href="https://example.org/editorial-b05"]').count() == 1 and page.locator('main a[rel~=sponsored]').count() == 0
                select(one['ID'])
                context.close()
            finally:
                browser.close()
    finally:
        for partner in partners + [fixture['article']]:
            b05.wp('global $wpdb;$wpdb->update($wpdb->posts,["post_content"=>' + b05.php_json(partner['post_content']) + '],["ID"=>' + str(partner['ID']) + ']);clean_post_cache(' + str(partner['ID']) + ');echo wp_json_encode(true);')
        raw = fixture['option']
        code = 'global $wpdb;$wpdb->delete($wpdb->options,["option_name"=>"' + OPTION + '"]);'
        if raw:
            code += '$wpdb->insert($wpdb->options,json_decode(' + json.dumps(json.dumps(raw)) + ',true));'
        code += 'wp_cache_flush();echo wp_json_encode(true);'
        b05.wp(code)
    checks['restauration_profils_et_corps_exacte'] = baseline == b05.state()
    checks['option_restauree_exactement'] = b05.wp(r'''global $wpdb;echo wp_json_encode($wpdb->get_row("SELECT * FROM {$wpdb->options} WHERE option_name='imagine_partenaire_du_mois'",ARRAY_A));''') == fixture['option']
    failures = [k for k,v in checks.items() if v is not True]
    result = {'checks':checks, 'total':len(checks), 'failures':failures, 'pages':pages, 'outside_demo_blocked':blocked, 'canaries_restored':True}
    b05.save(label, result)
    print(json.dumps({'total':len(checks), 'failures':failures},ensure_ascii=False))
    assert not failures


if __name__ == '__main__':
    run(sys.argv[1])
