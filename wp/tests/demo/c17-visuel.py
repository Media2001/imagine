"""Read-only Chromium captures of the actual C17 synthetic screens."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c17_http as t
from playwright.sync_api import sync_playwright

def run():
    t.c17.profils.guard('imagine-test-demo')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    before=t.c17.state();out={};blocked=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            for code,path,selector,name in [
                ('P-SOL-ATT','/my-account/','[data-imagine-justificatif]','compte-attente.png'),
                ('P-SOL-OK','/my-account/','[data-imagine-justificatif]','compte-valide.png'),
                ('E-ABO',t.ADMIN,'[data-imagine-file-justificatifs]','file-referent.png'),
                ('E-ADMIN','/wp-admin/admin.php?page=imagine-reglages','#imagine-solidaire-categories','reglage-categories.png')]:
                client=t.h.login(accounts[code]);jar=next(h.cookiejar for h in client.handlers if hasattr(h,'cookiejar'))
                ctx=browser.new_context(viewport={'width':1280,'height':900},locale='fr-BE')
                def route(r):
                    if r.request.url.startswith(t.h.BASE+'/'):r.continue_()
                    else:blocked.append(r.request.url.split('?')[0]);r.abort()
                ctx.route('**/*',route)
                ctx.add_cookies([{'name':c.name,'value':c.value,'domain':c.domain,'path':c.path,'secure':c.secure} for c in jar])
                page=ctx.new_page();response=page.goto(t.h.BASE+path,wait_until='networkidle')
                assert response.status==200
                target=page.locator(selector);assert target.count()==1 and target.is_visible()
                target.screenshot(path=str(t.c17.PROOF/name))
                out[code]={'route':path,'selector':selector,'capture':name,'visible':True}
                ctx.close()
        finally:browser.close()
    assert t.c17.state()==before
    t.c17.save('visuel',{'screens':out,'native_state_preserved':True,'outside_demo_requests_blocked':blocked,'visual_approval':False})
    print(json.dumps({'screens':list(out),'native_preserved':True,'visual_approval':False}))
if __name__=='__main__':run()
