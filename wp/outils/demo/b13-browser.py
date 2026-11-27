"""Recette navigateur commune bornée, jamais de matrice C26 modifiée."""
import sys
sys.dont_write_bytecode = True
import base64
import hashlib
import json
import re
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import b13
import c26
ROOT = b13.ROOT

def inventory():
    src = (ROOT/'wp/outils/demo/c23-inventaire.php').read_text(encoding='utf-8').split('<?php', 1)[1]
    f = b13.wp(src)
    historical = json.loads((ROOT/'production/C-26/mutations-livraison-inventaire.json').read_text(encoding='utf-8'))
    markers = c26.denied_markers(historical, 'anonyme')
    for post in f['posts']:
        if post['reserved']:
            markers.extend(c26.c23.reserved_witnesses(post['body']))
    markers = list(dict.fromkeys(markers))
    assert markers and any('CONTENU_FICTIF_RESERVE_' in x for x in markers)
    return f, markers

def observation(body):
    found = re.findall(r'<!-- B13_OBSERVATION ([A-Za-z0-9+/=]+) -->', body)
    assert len(found) == 1, 'Sonde publique non entrée'
    return json.loads(base64.b64decode(found[0]))

def run(owner, label, checker, paths=None, warm=None):
    identity = b13.guard()
    f, markers = inventory()
    paths = paths or ['/', f['article_path'], f['issue_path']]
    if warm:
        warm()
    probe = 'mu-plugins/b13-observer.php'
    assert b13.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+probe+'"));') is False
    uid = b13.wp('echo wp_json_encode((int)get_option("imagine_c09_fixture")["users"]["A-PAPIER"]);')
    old = b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=%s",'+str(uid)+',"session_tokens"),ARRAY_A));')
    private = b13.b11.private(label, {'session_rows': old})
    before = b13.c29.state()
    rows = []; checks = {}; external = []; err = None; removed = False; restored = False
    def check(name, ok):
        checks[name] = bool(ok)
        assert ok, name
    try:
        b13.b11.upload(probe, (ROOT/'wp/tests/demo/b13-observer.php').read_bytes())
        auth = b13.wp('$id='+str(uid)+';$t=WP_Session_Tokens::get_instance($id)->create(time()+3600);echo wp_json_encode([LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,"logged_in",$t)]);')
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True, channel='msedge')
            for role in ['anonyme', 'A-PAPIER']:
                ctx = browser.new_context(viewport={'width':1280,'height':1000}, locale='fr-BE', java_script_enabled=False)
                def route(r):
                    if urlsplit(r.request.url).netloc != urlsplit(identity['url']).netloc:
                        external.append({'url': r.request.url.split('?')[0], 'blocked': True}); r.abort()
                    else:
                        r.continue_()
                ctx.route('**/*', route)
                if role != 'anonyme':
                    ctx.add_cookies([{'name': k, 'value': v, 'url': identity['url']} for k,v in auth.items()])
                for index,path in enumerate(paths):
                    page = ctx.new_page()
                    response = page.goto(identity['url']+path, wait_until='networkidle')
                    body = page.content()
                    check(role+'_'+str(index)+'_200', response.status == 200)
                    obs = observation(body)
                    check(role+'_'+str(index)+'_zero_sortant', obs == {'http': [], 'mail': []})
                    item = checker(page, body, role, index, f, markers, check)
                    rows.append({'role':role,'path':path,'observation':obs,'body_sha256':hashlib.sha256(body.encode()).hexdigest(), **item})
                    if role == 'anonyme' and index == 0:
                        page.screenshot(path=str(owner.OUT/(label+'.png')), full_page=True)
                    page.close()
                r = ctx.request.get(identity['url']+'/?imagine_b13_witness=1', max_redirects=0)
                check(role+'_temoins_transport', r.status == 200 and observation(r.text()) == {'http':['blocked'],'mail':['blocked']})
                ctx.close()
            browser.close()
        check('aucune_ressource_tierce', external == [])
    except Exception as exc:
        err = repr(exc)
    finally:
        b13.wp('global $wpdb;$id='+str(uid)+';$old='+b13.php(old)+';$wpdb->delete($wpdb->usermeta,["user_id"=>$id,"meta_key"=>"session_tokens"]);foreach($old as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_flush();echo wp_json_encode(true);')
        session_ok = b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=%s",'+str(uid)+',"session_tokens"),ARRAY_A)==='+b13.php(old)+');')
        b13.b11.b10.b09.remove_remote([probe])
        removed = b13.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+probe+'"));')
        after = b13.c29.state()
        # Seuls caches de rendu des lots B13/B15, jamais profil, action ou option métier.
        allowed = {'_transient_imagine_b13_thematiques','_transient_timeout_imagine_b13_thematiques','_transient_imagine_b15_numero','_transient_timeout_imagine_b15_numero'}
        delta = {k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k) != after['option_fingerprints'].get(k)}
        stable = all(before[k] == after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint'])
        restored = stable and delta <= allowed
        b13.save(owner, label, {'checks':checks,'total':len(checks),'rows':rows,'markers_count':len(markers),
            'private_snapshot':private,'session_restored':session_ok,'restored':restored,'probe_removed':removed,
            'before':before,'after':after,'option_delta':sorted(delta),'external':external,'error':err,'sources':b13.sources(owner)})
    print(json.dumps({'total':len(checks),'failed':[k for k,v in checks.items() if not v], 'error':err,'restored':restored,'sessions':session_ok,'probe_removed':removed,'rows':len(rows)}, ensure_ascii=False))
    assert not err and checks and all(checks.values()) and restored and session_ok and removed


def b13_checker(page, body, role, index, f, markers, check):
    nav = page.locator('nav[aria-label="Navigation principale"]')
    top = nav.locator(':scope > ul > li > a').all_text_contents()
    check(role+'_'+str(index)+'_menu_huit', top == ['Nos numéros','Thématiques','Nos newsletters','Nos événements','Notre coopérative','Soutenir',"S'abonner",'Connexion'])
    menu = nav.inner_html()
    check(role+'_'+str(index)+'_selection_titre', 'B13 — Illustration fictive' in menu and 'data-b13-article=' in menu and '<img' in menu)
    check(role+'_'+str(index)+'_liste_imbriquee', nav.locator('[data-imagine-menu-etendu] > li > ul > li').count() > 0)
    check(role+'_'+str(index)+'_absence_reserve', c26.c23.assess(200, menu, markers)['ok'] and 'EXTRAIT_B13_INTERDIT_DANS_MENU_' not in menu)
    check(role+'_'+str(index)+'_mutation_absence_refusee', not c26.c23.assess(200, menu+'<!-- '+markers[0]+' -->', markers)['ok'])
    return {'menu':menu,'top':top}

if __name__ == '__main__':
    run(b13, sys.argv[1], b13_checker, warm=lambda:b13.wp('Imagine\\Site\\Navigation::thematiques();echo wp_json_encode(true);'))
