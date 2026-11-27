"""B15 : égalité HTML brute sur quatre pages, plus FAQ pour le contexte actif."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import re
import b15
spec = importlib.util.spec_from_file_location('browser_b13', b15.ROOT/'wp/outils/demo/b13-browser.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
EXPECTED = None
REFERENCE = None

def checker(page, body, role, index, fixture, markers, check):
    global REFERENCE
    foot = page.locator('.imagine-shell > footer')
    raw = re.findall(r'<footer>(.*?)</footer>', body, re.S)
    prefix = role+'_'+str(index)
    check(prefix+'_footer_present_unique', foot.count() == 1 and len(raw) == 1 and len(raw[0]) > 100)
    html = raw[0]
    if REFERENCE is None:
        REFERENCE = html
    check(prefix+'_html_brut_identique', html == REFERENCE)
    zones = foot.locator(':scope > section').evaluate_all('(els)=>els.map(e=>e.dataset.b15Zone)')
    check(prefix+'_cinq_zones_ordre', zones == ['abonnement','newsletter','numero','point-vente','mentions'])
    check(prefix+'_abonnement_commun', foot.locator('[data-b15-zone="abonnement"] a').get_attribute('href') == EXPECTED['subscribe'])
    check(prefix+'_newsletter_lien', foot.locator('[data-b15-zone="newsletter"] a').get_attribute('href') == fixture['base']+'/nos-newsletters/')
    check(prefix+'_numero_commun', foot.locator('[data-b15-numero]').get_attribute('data-b15-numero') == str(EXPECTED['issue']))
    check(prefix+'_couverture_differee', foot.locator('img').count() == 1 and foot.locator('img').get_attribute('loading') == 'lazy' and foot.locator('img').get_attribute('fetchpriority') == 'low')
    check(prefix+'_point_vente_lien_local', foot.locator('[data-b15-zone="point-vente"] a').get_attribute('href') == fixture['base']+'/points-de-vente/')
    check(prefix+'_liens_b09_uniques', all(foot.locator('a[href="'+url+'"]').count() == 1 for url in EXPECTED['legal']))
    forbidden = 'script,iframe,input,form'
    check(prefix+'_sans_saisie_geo_script', foot.locator(forbidden).count() == 0 and 'navigator.geolocation' not in html and 'geoip_' not in html)
    foot.evaluate("""(e)=>e.insertAdjacentHTML('beforeend','<script data-b15-mutant>navigator.geolocation.getCurrentPosition(function(){})</script><form data-b15-mutant><input type="email"></form>')""")
    check(prefix+'_mutation_saisie_geo_refusee', foot.locator(forbidden).count() != 0)
    foot.locator('[data-b15-mutant]').evaluate_all('(els)=>els.forEach(e=>e.remove())')
    check(prefix+'_absence_temoins_C26', b.c26.c23.assess(200, html, markers)['ok'])
    check(prefix+'_mutation_fuite_refusee', not b.c26.c23.assess(200, html+'<!-- '+markers[0]+' -->', markers)['ok'])
    if index == 1:
        page.evaluate('document.documentElement.classList.add("imagine-reading")')
        check(prefix+'_mode_lecture_masque_pied', foot.evaluate('(e)=>getComputedStyle(e).display') == 'none')
        page.evaluate('document.documentElement.classList.remove("imagine-reading")')
    return {'footer':html,'footer_sha256':b.hashlib.sha256(html.encode()).hexdigest(),'zones':zones,'links_b09':EXPECTED['legal']}

if __name__ == '__main__':
    b15.guard()
    f, _ = b.inventory()
    EXPECTED = b15.wp('$m=get_option("imagine_b09_menu");$links=[];foreach($m["items"] as $id){$links[]=get_permalink((int)get_post_meta($id,"_menu_item_object_id",true));}echo wp_json_encode(["issue"=>Imagine\\Site\\Accueil::numero()->ID,"subscribe"=>Imagine\\Site\\Navigation::abonnementUrl(),"legal"=>$links]);')
    paths = ['/', f['article_path'], f['issue_path'], f['account_path'], '/faq-service-client/']
    b.run(b15, sys.argv[1], checker, paths=paths, warm=lambda:b15.wp('Imagine\\Site\\Navigation::thematiques();Imagine\\Site\\PiedPage::numero();echo wp_json_encode(true);'))
