"""C18 read-only browser capture with outside-demo requests blocked."""
from pathlib import Path
import importlib.util, json, sys
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c18


def run():
    c18.c17.profils.guard('imagine-test-demo')
    spec = importlib.util.spec_from_file_location('c18_http', Path(__file__).with_name('c18-http.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    h = module.transport()
    account = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']['E-ABO']
    client = h.login(account)
    jar = next(handler.cookiejar for handler in client.handlers if hasattr(handler, 'cookiejar'))
    before = c18.state()
    blocked = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            context = browser.new_context(viewport={'width': 1280, 'height': 1000}, locale='fr-BE')
            def route(r):
                if r.request.url.startswith(h.BASE + '/'):
                    r.continue_()
                else:
                    blocked.append(r.request.url.split('?')[0])
                    r.abort()
            context.route('**/*', route)
            context.add_cookies([{'name':c.name, 'value':c.value, 'domain':c.domain, 'path':c.path, 'secure':c.secure} for c in jar])
            page = context.new_page()
            response = page.goto(h.BASE + '/wp-admin/admin.php?page=imagine-extractions&extraction=localite&pays=FR', wait_until='networkidle')
            assert response.status == 200
            assert page.locator('h1', has_text='Extractions').is_visible()
            assert page.locator('[data-imagine-extraction-nombre]').get_attribute('data-imagine-extraction-nombre') == '2'
            assert page.locator('#imagine-extraction option[disabled]').count() == 2
            page.screenshot(path=str(c18.PROOF / 'extractions-referent.png'))
            context.close()
        finally:
            browser.close()
    assert before == c18.state()
    result = {'capture': 'extractions-referent.png', 'actual_browser': 'Chromium', 'native_preserved': True,
              'outside_demo_requests_blocked': blocked, 'visual_approval': False}
    c18.save('visuel', result)
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == '__main__':
    run()
