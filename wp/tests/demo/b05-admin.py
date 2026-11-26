"""B05 native C10 form save and two settled browser captures; test accounts only."""
from pathlib import Path
import importlib.util, json, sys
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b05
BASE = 'http://192.168.129.32:8085'
OPTION = 'imagine_partenaire_du_mois'


def rows(names):
    return b05.wp('global $wpdb;$out=[];foreach(' + b05.php_json(names) + ' as $n){$out[$n]=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->options} WHERE option_name=%s",$n),ARRAY_A);}echo wp_json_encode($out);')


def run(label, capture=False, read_only=False):
    b05.profils.guard('imagine-test-demo')
    assert not (b05.PROOF / (label + '.json')).exists()
    spec = importlib.util.spec_from_file_location('b05_transport', Path(__file__).with_name('c18-http.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    h = module.transport()
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    admin = h.login(accounts['E-ADMIN'])
    jar = next(handler.cookiejar for handler in admin.handlers if hasattr(handler, 'cookiejar'))
    before = b05.state()
    checks, blocked, old = {}, [], None
    selected_before = b05.wp('echo wp_json_encode(get_option("' + OPTION + '",null));')
    try:
        bad = urlencode({'option_page':'imagine_reglages','action':'update',OPTION:'49','_wpnonce':'invalide'}).encode()
        status, _, _ = h.fetch('/wp-admin/options.php', admin, bad)
        checks['nonce_invalide_refuse'] = status == 403
        reader = h.login(accounts['E-REDAC'])
        status, _, _ = h.fetch('/wp-admin/options.php', reader, bad)
        checks['redacteur_sans_droit_refuse'] = status == 403
        checks['refus_sans_mutation'] = b05.wp('echo wp_json_encode(get_option("' + OPTION + '",null));') == selected_before
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                context = browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE')
                def route(r):
                    if r.request.url.startswith(BASE + '/'):
                        r.continue_()
                    else:
                        blocked.append(r.request.url.split('?')[0]); r.abort()
                context.route('**/*', route)
                context.add_cookies([{'name':c.name,'value':c.value,'domain':c.domain,'path':c.path,'secure':c.secure} for c in jar])
                page = context.new_page()
                response = page.goto(BASE + '/wp-admin/admin.php?page=imagine-reglages',wait_until='networkidle')
                form = page.locator('form[action="options.php"]')
                field = form.locator('#imagine-partenaire-du-mois')
                checks['champ_formulaire_C10_unique'] = response.status == 200 and field.count() == 1
                checks['nonce_et_groupe_natifs'] = form.locator('input[name=_wpnonce]').count() == 1 and form.locator('input[name=option_page]').input_value() == 'imagine_reglages'
                names = form.locator('[name]').evaluate_all('(xs)=>[...new Set(xs.map(x=>x.name.split("[")[0]).filter(x=>x.startsWith("imagine_")))]')
                assert OPTION in names
                checks['choix_manuel_non_multiple'] = field.get_attribute('multiple') is None and field.locator('option').count() == 3
                checks['injection_sans_avertissement'] = page.locator('.imagine-partenaire-injection-erreur').count() == 0
                if read_only:
                    checks['lecture_sans_sauvegarde_C10'] = field.input_value() == str(selected_before)
                else:
                    old = rows(names)
                    field.select_option('48')
                    with page.expect_navigation(wait_until='networkidle'):
                        form.evaluate('(f)=>f.requestSubmit()')
                    checks['sauvegarde_native_C10'] = b05.wp('echo wp_json_encode((int) get_option("' + OPTION + '"));') == 48
                    checks['choix_relu_ecran'] = page.locator('#imagine-partenaire-du-mois').input_value() == '48'
                context.close()
                if capture:
                    public = browser.new_context(viewport={'width':1280,'height':1000},locale='fr-BE')
                    public.route('**/*',route)
                    page = public.new_page()
                    page.goto(BASE + '/',wait_until='networkidle')
                    block = page.locator('[data-imagine-partenaire-mois="48"]')
                    checks['accueil_canonique_selectionne'] = block.count() == 1
                    block.scroll_into_view_if_needed()
                    page.screenshot(path=str(b05.PROOF / 'accueil-partenaire-V2.png'))
                    page.goto(BASE + '/partenaires/demo-partners-1/',wait_until='networkidle')
                    checks['fiche_canonique_visible'] = page.locator('.imagine-partnership-label',has_text='Partenariat').is_visible()
                    page.screenshot(path=str(b05.PROOF / 'fiche-partenaire-V2.png'))
                    public.close()
            finally:
                browser.close()
    finally:
        # The C10 form may initialize missing predecessor options. Restore those exact
        # rows/absences only; keep native append-only journals, never reset profiles.
        if old is not None:
            restore = {k:v for k,v in old.items() if k != OPTION}
            b05.wp('global $wpdb;foreach(' + b05.php_json(restore) + ' as $n=>$row){$wpdb->delete($wpdb->options,["option_name"=>$n]);if($row!==null)$wpdb->insert($wpdb->options,$row);}wp_cache_flush();echo wp_json_encode(true);')
            checks['autres_reglages_restaures_exactement'] = rows(list(restore)) == restore
    checks['profils_et_action_metier_exacts'] = b05.state() == before
    checks['choix_final_manuel_48'] = b05.wp('echo wp_json_encode((int) get_option("' + OPTION + '"));') == 48
    failures = [k for k,v in checks.items() if v is not True]
    b05.save(label, {'checks':checks,'total':len(checks),'failures':failures,'option_before':selected_before,'option_after':48,'outside_demo_blocked':blocked,'captures':['accueil-partenaire-V2.png','fiche-partenaire-V2.png'] if capture else [],'visual_approval':False})
    print(json.dumps({'total':len(checks),'failures':failures},ensure_ascii=False))
    assert not failures


if __name__ == '__main__':
    run(sys.argv[1], '--capture' in sys.argv, '--read-only' in sys.argv)
