"""B03-C1 : navigateur réel, sondes DOM éphémères ; aucune écriture WordPress."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-03'
URL = 'http://192.168.129.32:8085/c08-article-reserve-article/'


def run(phase='corrections'):
    checks, samples = {}, []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width, height in [(390, 844), (1440, 900)]:
            context = browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce')
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            response = page.goto(URL, wait_until='networkidle')
            checks[f'{width}:HTTP200'] = response.status == 200
            page.wait_for_selector('#imagine-reading-toggle', state='visible')
            checks[f'{width}:viewport'] = page.evaluate('innerWidth') == width
            requests = []
            page.on('request', lambda request: requests.append(request.url))
            original = page.locator('.imagine-article-body').inner_html()
            page.evaluate('''() => {
                const box = document.createElement('section'); box.id = 'b03-color-probes';
                box.innerHTML = '<p id="b03-black" style="color:#000000">Sonde noire</p>' +
                    '<div id="b03-block" class="has-text-color has-black-color has-vivid-red-background-color has-background" style="background-color:#cf2e2e;color:#000000"><span>Sonde de bloc</span></div>' +
                    '<p id="b03-inline" style="color:#ffffff;background-color:#0000ff">Sonde en ligne</p>' +
                    '<img id="b03-image" alt="Sonde image temporaire" width="24" height="24" style="background-color:#00ff00;color:#ff00ff">';
                box.querySelector('img').src = 'data:image/svg+xml,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><rect width="24" height="24" fill="red"/></svg>`);
                document.querySelector('.imagine-paywall-body').append(box);
                const style = document.createElement('style'); style.id = 'b03-probe-style';
                style.textContent = '.has-black-color {color:#000 !important}.has-vivid-red-background-color {background-color:#cf2e2e !important}';
                document.head.append(style);
            }''')
            probe_html = page.locator('#b03-color-probes').inner_html()
            image = page.locator('#b03-image').evaluate('(e) => [e.outerHTML, getComputedStyle(e).backgroundColor, getComputedStyle(e).color]')
            page.locator('#imagine-reading-toggle').click()
            for theme in ['light', 'sepia', 'dark']:
                page.select_option('#imagine-reading-theme', theme)
                values = page.evaluate('''() => {
                    function rgb(s) {return s.match(/[\\d.]+/g).slice(0,3).map(Number);}
                    function luminance(s) {return rgb(s).map(v => v/255).map(v => v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4).reduce((a,v,i) => a+v*[.2126,.7152,.0722][i],0);}
                    function background(e) {while(e) {const c=getComputedStyle(e).backgroundColor; if(c!=='rgba(0, 0, 0, 0)' && c!=='transparent') return c; e=e.parentElement;} throw Error('Fond opaque absent');}
                    return ['b03-black','b03-block','b03-inline'].map(id => {
                        const e=document.getElementById(id), color=getComputedStyle(e).color, bg=background(e);
                        const a=luminance(color), b=luminance(bg);
                        return {id,color,background:bg,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
                    });
                }''')
                for row in values:
                    checks[f'{width}:{theme}:{row["id"]}:AA'] = row['ratio'] >= 4.5
                    samples.append({'width': width, 'theme': theme, **row})
                checks[f'{width}:{theme}:DOM_intact'] = page.locator('#b03-color-probes').inner_html() == probe_html
                checks[f'{width}:{theme}:image_intacte'] = page.locator('#b03-image').evaluate('(e) => [e.outerHTML, getComputedStyle(e).backgroundColor, getComputedStyle(e).color]') == image
                checks[f'{width}:{theme}:paywall_visible'] = page.locator('[data-imagine-bloc]').is_visible()
            page.locator('#imagine-reading-toggle').click()
            checks[f'{width}:couleur_auteur_retablie'] = page.locator('#b03-black').evaluate('(e) => getComputedStyle(e).color') == 'rgb(0, 0, 0)'
            page.evaluate("document.getElementById('b03-color-probes').remove(); document.getElementById('b03-probe-style').remove()")
            checks[f'{width}:contenu_DOM_original'] = page.locator('.imagine-article-body').inner_html() == original
            page.locator('#imagine-reading-toggle').click()
            sizes = []
            for size in ['normal', 'large', 'larger']:
                page.select_option('#imagine-reading-size', size)
                sizes.append(page.locator('.imagine-article').evaluate('(e) => parseFloat(getComputedStyle(e).fontSize)'))
            checks[f'{width}:trois_tailles_croissantes'] = sizes[0] < sizes[1] < sizes[2]
            checks[f'{width}:colonne_70ch'] = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--imagine-reading-column').trim()") == '70ch'
            checks[f'{width}:navigation_masquee'] = not page.locator('.imagine-shell > header').is_visible()
            checks[f'{width}:sans_debordement'] = page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            checks[f'{width}:progression_fixe'] = page.locator('#imagine-reading-progress').evaluate('(e) => getComputedStyle(e).position') == 'fixed'
            page.evaluate('scrollTo(0, document.documentElement.scrollHeight)')
            page.wait_for_function("document.getElementById('imagine-reading-progress').value === 100")
            checks[f'{width}:progression_fin'] = page.locator('#imagine-reading-progress').evaluate('(e) => e.value') == 100
            checks[f'{width}:aucune_requete_reglages'] = not requests
            page.reload(wait_until='networkidle')
            page.wait_for_function("document.documentElement.classList.contains('imagine-reading')")
            checks[f'{width}:mode_repris'] = page.locator('#imagine-reading-toggle').get_attribute('aria-pressed') == 'true'
            checks[f'{width}:fond_repris'] = page.locator('#imagine-reading-theme').input_value() == 'dark'
            checks[f'{width}:taille_reprise'] = page.locator('#imagine-reading-size').input_value() == 'larger'
            checks[f'{width}:position_reprise'] = page.locator('#imagine-reading-progress').evaluate('(e) => e.value') == 100
            page.keyboard.press('Escape')
            checks[f'{width}:echap_sortie'] = page.locator('#imagine-reading-toggle').get_attribute('aria-pressed') == 'false'
            checks[f'{width}:focus_retabli'] = page.evaluate("document.activeElement.id === 'imagine-reading-toggle'")
            checks[f'{width}:navigation_retablie'] = page.locator('.imagine-shell > header').is_visible()
            context.close()
        nojs = browser.new_context(java_script_enabled=False, viewport={'width': 1440, 'height': 900})
        page = nojs.new_page()
        page.goto(URL, wait_until='networkidle')
        checks['sans_JS:bouton_masque'] = not page.locator('#imagine-reading-toggle').is_visible()
        checks['sans_JS:article_lisible'] = page.locator('.imagine-article-body').is_visible()
        checks['sans_JS:navigation_visible'] = page.locator('.imagine-shell > header').is_visible()
        checks['sans_JS:aucune_vue_active'] = 'imagine-reading' not in (page.locator('html').get_attribute('class') or '').split()
        nojs.close()
        checks['aucune_erreur_JS'] = not errors
        version = browser.version
        browser.close()
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'browser': version,
               'python': sys.executable, 'checks': checks, 'samples': samples, 'errors': errors,
               'failures': [k for k, v in checks.items() if not v],
               'source_sha256': {name: hashlib.sha256((ROOT / 'wp/themes/imagine/assets' / name).read_bytes()).hexdigest() for name in ['reading.css', 'reading.js']}}
    (PROOF / ('browser-colors-' + phase + '.json')).write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checks': len(checks), 'failures': receipt['failures'], 'ratios': sorted(set(round(r['ratio'], 3) for r in samples))}))
    if receipt['failures']:
        raise SystemExit(1)
    return receipt


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'corrections')
