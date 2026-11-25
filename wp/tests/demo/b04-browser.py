"""Read-only browser QA: responsive geometry, keyboard and native public destination."""
from pathlib import Path
import http.cookiejar
import importlib.util
import json
import sys
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
s=importlib.util.spec_from_file_location('m',HERE/'b04-http.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.work;w.guard()
inventory=w.wp(m.INVENTORY)
accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
checks={};screens=[];errors=[];external=[]
def cookies(client):
    for h in client.handlers:
        if hasattr(h,'cookiejar'):
            return [{'name':c.name,'value':c.value,'domain':c.domain,'path':c.path,'secure':c.secure} for c in h.cookiejar]
    raise RuntimeError('Native cookie jar unavailable')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for label in ['anonyme','a-carte','p-numero']:
        context=browser.new_context()
        if label!='anonyme':context.add_cookies(cookies(m.http.login(accounts['A-CARTE' if label=='a-carte' else 'P-NUMERO'])))
        def route(r):
            u=urlsplit(r.request.url)
            if u.netloc and u.netloc!='192.168.129.32:8085':
                external.append(u.netloc);r.abort()
            else:r.continue_()
        context.route('**/*',route)
        page=context.new_page()
        page.on('pageerror',lambda e:errors.append(type(e).__name__))
        pages=[('numero11',inventory['issues']['demo-2026-t1']['path']),('numero39',inventory['issues']['demo-2026-t4']['path'])]
        if label=='anonyme':pages += [('kiosque','/numeros/'),('thematique','/thematiques/demo-thematique-1/')]
        for width,height in [(1280,900),(375,812)]:
            page.set_viewport_size({'width':width,'height':height})
            for family,path in pages:
                prefix=label+':'+str(width)+':'+family
                response=page.goto(m.http.BASE+path,wait_until='networkidle')
                checks[prefix+':HTTP']=response.status==200
                checks[prefix+':sans_debordement']=page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                checks[prefix+':main_et_h1_uniques']=page.locator('main').count()==page.locator('h1').count()==1
                checks[prefix+':IDs_uniques']=page.evaluate('(()=>{const ids=[...document.querySelectorAll("[id]")].map(e=>e.id);return ids.length===new Set(ids).size;})()')
                # Native links remain operable through the keyboard, no injected tabindex.
                link=page.locator('main .imagine-list li a').first
                link.focus()
                checks[prefix+':focus_visible']=link.evaluate('(e)=>{const s=getComputedStyle(e);return e===document.activeElement && s.outlineStyle!=="none" && parseFloat(s.outlineWidth)>0;}')
                page.locator('h1').click()
                name=prefix.replace(':','-')+'.png'
                target=w.PROOF/'captures'/name;target.parent.mkdir(exist_ok=True)
                page.screenshot(path=str(target),full_page=True);screens.append(str(target.relative_to(w.ROOT)))
        if label=='anonyme':
            page.goto(m.http.BASE+inventory['issues']['demo-2026-t1']['path'],wait_until='networkidle')
            buy=page.locator('a[data-imagine-buy]');url=buy.get_attribute('href');buy.focus();page.keyboard.press('Enter');page.wait_for_url(url)
            checks['clavier:achat_destination_native_publique']=page.locator('form.cart button[name="add-to-cart"]').count()==1
            checks['clavier:produit_fictif']=page.locator('h1').inner_text().startswith('FICTIF B04')
            page.goto(m.http.BASE+inventory['issues']['demo-2026-t1']['path'],wait_until='networkidle')
            link=page.locator('#imagine-contents-list li a').first;url=link.get_attribute('href');link.focus();page.keyboard.press('Enter');page.wait_for_url(url)
            checks['clavier:sommaire_article_reel']=page.locator('.imagine-paywall-body').count()==1
            checks['clavier:article_reste_ferme']=page.locator('[data-imagine-bloc]').count()>0
        context.close()
    browser.close()
checks['zero_exception_JS']=not errors
checks['aucune_dependance_exterieure']=not external
result={'scope':'imagine-test-demo','total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],
        'screenshots':screens,'browser':'Chromium headless','viewports':[[1280,900],[375,812]],'exceptions_JS':errors,'external_hosts_blocked':sorted(set(external))}
(w.PROOF/'browser.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'total':len(checks),'failures':result['failures'],'screenshots':len(screens)}))
if result['failures']:raise SystemExit(1)
