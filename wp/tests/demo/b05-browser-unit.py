"""B05 reusable HTTP guards exercised offline by real Chromium."""
from pathlib import Path
import importlib.util, json, sys
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('b05_http',Path(__file__).with_name('b05-http.py'))
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
partners=[{'ID':48,'post_name':'demo-partners-1'}]

def run(label):
    checks={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page()
            page.route('**/*',lambda route:route.abort())
            page.set_content('<section aria-labelledby="imagine-latest-posts"><h2 id="imagine-latest-posts">Derniers articles</h2><ul class="imagine-list"><li><a href="'+h.BASE+'/?p=17">Article fictif</a></li></ul></section>')
            checks.update(h.home_article_checks(page,partners))
            checks.update(h.home_mutations(page,partners))
            # Explicitly reproduce the old false positive on the same DOM.
            page.locator('.imagine-list a').evaluate('(a)=>a.rel="sponsored"')
            checks['ancien_selecteur_passe_a_tort']=page.locator('#imagine-latest-posts a[rel~=sponsored]').count()==0
            checks['nouveau_selecteur_refuse_mutation']=h.home_article_checks(page,partners)['articles_accueil_non_sponsored'] is False
        finally: browser.close()
    failures=[k for k,v in checks.items() if v is not True]
    h.b05.save(label,dict(checks=checks,total=len(checks),failures=failures,network='all requests blocked'))
    print(json.dumps(dict(total=len(checks),failures=failures)))
    assert not failures
if __name__=='__main__': run(sys.argv[1])
