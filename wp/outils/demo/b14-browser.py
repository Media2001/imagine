"""B14 vrai accueil anonyme/A-PAPIER ; banc et témoins C26 inchangés."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import re
import b14
spec = importlib.util.spec_from_file_location('browser_b13', b14.ROOT/'wp/outils/demo/b13-browser.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
EXPECTED = None

def checker(page, body, role, index, fixture, markers, check):
    main = page.locator('main')
    keys = main.locator(':scope > section').evaluate_all('(els)=>els.map(e=>e.dataset.b14Section || (e.hasAttribute("data-imagine-partenaire-mois")?"partenaire":"autre"))')
    want = ['numero','conversion'] + (['reportage'] if EXPECTED['free'] else []) + ['newsletter','thematiques','evenements','soutenir','cooperative','partenaire']
    check(role+'_ordre_sections', keys == want)
    check(role+'_numero_attendu', main.locator('[data-b14-section="numero"] h3').inner_text() == EXPECTED['title'])
    check(role+'_une_prioritaire', page.locator('img[fetchpriority="high"]').count() == 1 and page.locator('img[loading="eager"]').count() == 1)
    check(role+'_autres_differees', page.locator('img:not([fetchpriority="high"])').evaluate_all('(els)=>els.every(e=>e.loading==="lazy")'))
    check(role+'_dimensions_images', page.locator('img').evaluate_all('(els)=>els.length>1 && els.every(e=>e.hasAttribute("width")&&e.hasAttribute("height"))'))
    check(role+'_aucune_video_iframe', page.locator('video,iframe').count() == 0)
    for tag in ['video', 'iframe']:
        main.evaluate('(e,tag)=>{let n=document.createElement(tag);n.dataset.b14Mutant="1";e.append(n)}', tag)
        check(role+'_mutation_'+tag+'_refusee', page.locator('video,iframe').count() != 0)
        main.locator('[data-b14-mutant]').evaluate('(e)=>e.remove()')
    check(role+'_newsletter_sans_saisie', main.locator('[data-b14-section="newsletter"] a').count() == 1 and main.locator('[data-b14-section="newsletter"] input, [data-b14-section="newsletter"] form').count() == 0)
    main.locator('[data-b14-section="newsletter"]').evaluate("""(e)=>e.insertAdjacentHTML('beforeend','<form data-b14-mutant><input type="email"></form>')""")
    check(role+'_mutation_saisie_newsletter_refusee', main.locator('[data-b14-section="newsletter"] input, [data-b14-section="newsletter"] form').count() != 0)
    main.locator('[data-b14-mutant]').evaluate('(e)=>e.remove()')
    events = main.locator('[data-b14-evenement]').evaluate_all('(els)=>els.map(e=>Number(e.dataset.b14Evenement))')
    check(role+'_evenements_b07_max_trois', events == EXPECTED['events'][:3] and len(events) <= 3)
    check(role+'_partenariat_b05', main.locator('[data-imagine-partenaire-mois] .imagine-partnership-label').inner_text() == 'Partenariat')
    check(role+'_derniers_articles_retires', 'Derniers articles' not in main.inner_text() and page.locator('#imagine-latest-posts').count() == 0)
    main.evaluate("""(e)=>e.insertAdjacentHTML('beforeend','<section data-b14-mutant id="imagine-latest-posts">Derniers articles</section>')""")
    check(role+'_mutation_derniers_articles_refusee', not ('Derniers articles' not in main.inner_text() and page.locator('#imagine-latest-posts').count() == 0))
    main.locator('[data-b14-mutant]').evaluate('(e)=>e.remove()')
    buy = main.locator('[data-b14-acheter]').count()
    check(role+'_achat_selon_vente_native', buy == int(bool(EXPECTED['buy'])))
    if not EXPECTED['buy']:
        main.evaluate("""(e)=>e.insertAdjacentHTML('beforeend', '<a data-b14-acheter data-b14-mutant href="#">Mutant</a>')""")
        check(role+'_mutation_achat_refusee', main.locator('[data-b14-acheter]').count() != int(bool(EXPECTED['buy'])))
        main.locator('[data-b14-mutant]').evaluate('(e)=>e.remove()')
    check(role+'_ancre_menu_valide', page.locator('#imagine-thematiques').count() == 1)
    check(role+'_absence_temoins_C26', b.c26.c23.assess(200, body, markers)['ok'])
    check(role+'_mutation_fuite_refusee', not b.c26.c23.assess(200, body+'<!-- '+markers[0]+' -->', markers)['ok'])
    anchor = page.locator('#imagine-abonnement')
    check(role+'_ancre_abonnement_unique', anchor.count() == 1)
    check(role+'_ancre_contient_cta', anchor.locator('a[href="'+page.locator('.imagine-nav-abonnement > a').get_attribute('href')+'"]').count() == 1)
    if role == 'anonyme':
        response = page.goto(fixture['base']+fixture['article_path'], wait_until='networkidle')
        check('paywall_200_zero_sortant', response.status == 200 and b.observation(response.text()) == {'http': [], 'mail': []})
        target = page.locator('[data-imagine-bloc] a[href$="#imagine-abonnement"]')
        check('paywall_lien_abonnement_present', target.count() > 0)
        target.first.click()
        page.wait_for_load_state('networkidle')
        check('paywall_atteint_conversion_avec_cta', page.url.endswith('#imagine-abonnement')
            and page.locator('#imagine-abonnement').count() == 1
            and "S'abonner" in page.locator('#imagine-abonnement').inner_text().replace('’', "'"))
    return {'sections':keys,'events':events,'buy':buy,'main_sha256':b.hashlib.sha256(main.inner_html().encode()).hexdigest()}

if __name__ == '__main__':
    b14.guard()
    EXPECTED = b14.wp('$n=Imagine\\Site\\Accueil::numero();$f=Imagine\\Site\\Accueil::libre($n);echo wp_json_encode(["issue"=>$n->ID,"title"=>get_the_title($n),"free"=>$f?->ID,"buy"=>Imagine\\Theme\\imagine_issue_product($n->ID),"events"=>array_column(Imagine\\Site\\Agenda::groupes()["futurs"],"id")]);')
    b.run(b14, sys.argv[1], checker, paths=['/'], warm=lambda:b14.wp('Imagine\\Site\\Navigation::thematiques();echo wp_json_encode(true);'))
