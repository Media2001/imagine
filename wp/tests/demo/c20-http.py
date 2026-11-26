"""C20 authenticated real pages and safe native navigation; never a mutation fallback."""
from pathlib import Path
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlsplit
import importlib.util, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import importlib
c20 = importlib.import_module('c20-second')


def run(label='http-final'):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', label):
        raise ValueError('C20 HTTP receipt label refused')
    c20.c20.profils.guard('imagine-test-demo')
    spec = importlib.util.spec_from_file_location('c20_http_transport', Path(__file__).with_name('c12-http.py'))
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {p:h.login(accounts[p]) for p in ('A-CARTE','A-SEPA4','A-VIR','A-PAPIER')}
    account_path = c20.wp('echo wp_json_encode(parse_url(wc_get_page_permalink("myaccount"),PHP_URL_PATH));')
    before = c20.snapshot()
    checks = {}
    views = {}
    for who, client in clients.items():
        status, headers, page = h.fetch(account_path, client)
        blocks = re.findall(r'<aside data-imagine-renouvellement="([^"]+)">(.*?)</aside>', page, re.S)
        checks[who + '_account_real_200_one_block'] = status == 200 and len(blocks) == 1
        expected = 'quatre_fois' if who == 'A-SEPA4' else 'manuel'
        checks[who + '_mode'] = bool(blocks) and blocks[0][0] == expected
        checks[who + '_private_no_store'] = 'no-store' in headers.get('cache-control','')
        checks[who + '_no_false_action'] = bool(blocks) and all(x not in blocks[0][1] for x in ('<button','<form'))
        if who == 'A-CARTE':
            checks['A_CARTE_honest_manual_no_gateway'] = 'aucune carte ni passerelle raccordée' in unescape(page)
        sub_id = before['profiles'][who]['id']
        url = c20.wp('$s=wcs_get_subscription(' + str(sub_id) + ');echo wp_json_encode($s->get_view_order_url());')
        parsed = urlsplit(url)
        assert parsed.scheme == 'http' and parsed.netloc == '192.168.129.32:8085'
        views[who] = parsed.path
        status, _, page = h.fetch(parsed.path, client)
        checks[who + '_native_view_no_cancel_resume'] = status == 200 and 'change_subscription_to=cancelled' not in page and 'change_subscription_to=active' not in page
    status, _, page = h.fetch(views['A-CARTE'], clients['A-VIR'])
    checks['other_owner_native_view_no_details'] = status in (200,403) and 'class="shop_table subscription_details"' not in page
    blocked = []
    captures = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for who, width, height in [('A-CARTE',1280,1000),('A-SEPA4',390,844)]:
                jar = next(handler.cookiejar for handler in clients[who].handlers if hasattr(handler,'cookiejar'))
                context = browser.new_context(viewport={'width':width,'height':height},locale='fr-BE')
                def route(r):
                    if r.request.url.startswith(h.BASE + '/'):
                        r.continue_()
                    else:
                        blocked.append(r.request.url.split('?')[0]);r.abort()
                context.route('**/*',route)
                context.add_cookies([{'name':c.name,'value':c.value,'domain':c.domain,'path':c.path,'secure':c.secure} for c in jar])
                tab = context.new_page()
                tab.goto(h.BASE + account_path, wait_until='networkidle')
                aside = tab.locator('[data-imagine-renouvellement]')
                checks[who + '_browser_visible'] = aside.is_visible()
                name = who.lower() + '-' + label + '-' + str(width) + '.png'
                aside.screenshot(path=str(c20.PROOF/name))
                captures.append(name)
                tab.get_by_role('link',name='Gérer cet abonnement dans WooCommerce',exact=True).first.click()
                tab.wait_for_load_state('networkidle')
                checks[who + '_real_manage_link_native_without_cancel'] = urlsplit(tab.url).path == views[who] and tab.locator('a[href*="change_subscription_to=cancelled"]').count() == 0
                context.close()
        finally:
            browser.close()
    after = c20.snapshot()
    checks['profiles_actions_exact_after_HTTP_browser'] = before['profiles'] == after['profiles']
    c20.save(label + '-before', before)
    c20.save(label + '-after', after)
    result = {'at':datetime.now(timezone.utc).isoformat(),'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],
              'captures':captures,'outside_requests_blocked':blocked,'confirmation_action_delivered':False,'visual_approval':False}
    c20.save(label,result)
    print(json.dumps(result,ensure_ascii=False))
    assert not result['failures'],result['failures']

if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else 'http-final')
