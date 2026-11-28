"""Réception finale réservée au parent, après les gates natifs/image/rejeu."""
import sys
sys.dont_write_bytecode = True
import json
import reception_c32 as v

if sys.argv[1:] != ['--live']:
    raise SystemExit('Usage : python -B production/C-32/finaliser.py --live (démo libre requise)')
assert not (v.OUT/'PRET').exists(), 'PRET existe déjà ; ne pas écraser une réception'
assert not (v.OUT/v.RECEIPT).exists(), 'Réception immuable déjà présente'
browser = v.load(v.BROWSER)
reading = v.verify_browser(browser)
strict = {'status':'PASS' if reading['strict_pass'] else 'FAIL', 'expected':0, 'pages':reading['pages'], 'observed_cookie_names':reading['observed_names'], 'native_order_attribution_unchanged':True, 'browser_receipt':v.BROWSER}
if (v.OUT/v.STRICT).exists():
    assert v.load(v.STRICT) == strict, 'Preuve stricte divergente'
else:
    with (v.OUT/v.STRICT).open('x', encoding='utf-8') as f:
        json.dump(strict, f, ensure_ascii=False, indent=2)
evidence = ['A-VOIR.md', 'verifier.py', 'reception_c32.py', 'finaliser.py', 'test-local.py', v.LOCAL, v.NATIVE, v.BROWSER, v.BROWSER.replace('.json','.png'), v.STANDARD, v.OFFICIAL, v.STRICT, v.IMAGE, v.REPLAY]
for name in [v.LOCAL, v.IMAGE, v.REPLAY]:
    receipt = v.load(name)
    evidence.extend(r['log'] for r in receipt['runs']) if 'runs' in receipt else evidence.append(receipt['log'])
historical = [p for p in v.OUT.glob('*.json') if p.name not in evidence and p.name != v.RECEIPT]
manifest = v.c.seal(v.owner, [v.OUT/name for name in evidence], historical)
# Vérifier aussi le readback distant AVANT de déposer le marqueur.
v.verify(True, manifest, False)
with (v.OUT/v.RECEIPT).open('x', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
with (v.OUT/'PRET').open('x', encoding='utf-8') as f:
    f.write('C-32 prêt à relire — inventaire autorisé PASS ; '+v.RECEIPT+' ; zéro cookie strict '+strict['status']+' ; attribution native non désactivée.\n')
v.verify(True)

