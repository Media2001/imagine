"""Vérifications des corrections C31 ; aucun PRET avant image/rejeu globaux du parent."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'wp/outils/demo'), str(ROOT/'wp/tests/demo')]
import c31 as owner
spec = importlib.util.spec_from_file_location('c31_contract', ROOT/'wp/tests/demo/b13-contract.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
OUT = owner.OUT
RECEIPT = 'reception-corrections-V2.json'
def load(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))
def same_sources(receipt):
    assert receipt['sources'] == owner.sources(owner), 'Preuve périmée après modification de source'
def local(live=False):
    native = load('corrections-native-final-V2.json')
    same_sources(native)
    assert native['restored'] and native['before'] == native['after']
    assert native['native']['code'] == 0 and not native['native']['stderr']
    data = json.loads(native['native']['stdout'])
    assert data['total'] == len(data['checks']) == 46 and all(data['checks'].values())
    assert data['storage_tables'] >= 47 and data['storage_columns'] >= 187 and data['checkout_leaks'] == []
    for key in ['wp_options.option_value','wp_usermeta.meta_value','wp_wc_order_addresses.email','wp_wc_orders.billing_email','wp_woocommerce_sessions.session_value']:
        assert data['positive_detection'][key] > 0
    browser = load('corrections-browser-final-V2.json')
    compte = load('corrections-compte-final-V2.json')
    commande = load('corrections-commande-final-V2.json')
    for item, count in [(browser,16),(compte,29),(commande,13)]:
        same_sources(item)
        assert item['total'] == len(item['checks']) == count and all(item['checks'].values())
        assert item['error'] is None and item['restored'] and item['sessions_restored'] and item['probe_removed'] and not item['external']
    assert [r['kind'] for r in compte['rows']] == ['inchange','refuse','autorise']
    assert [r['post_status'] for r in compte['rows']] == [302,200,302]
    assert commande['cart_restored'] and commande['rows'][-1]['status'] == 400
    wp, woo = browser['rows']
    assert wp['kind'] == 'wp' and woo['kind'] == 'woo'
    assert wp['observation']['mail'] == [] and len(wp['observation']['http']) == 2 and all('translations_api' in x['trace'] for x in wp['observation']['http'])
    assert woo['observation'] == {'http':[], 'mail':[]}
    for name in ['corrections-suite-final-V2.json','corrections-cible-final-V2.json','corrections-style-final-V2.json']:
        proof = load(name)
        assert proof['exit'] == 0
        assert all(c.core.digest(ROOT/key) == value for key,value in proof['sources'].items()), name
    suite = load('corrections-suite-final-V2.json')
    text = (OUT/suite['log']).read_text(encoding='utf-8')
    match = re.search(r'OK \((\d+) tests, (\d+) assertions\)', text)
    assert match and int(match[1]) >= 265
    target = load('corrections-cible-final-V2.json')
    assert 'OK (9 tests, 64 assertions)' in (OUT/target['log']).read_text(encoding='utf-8')
    classic_red = load('corrections-native-red3-V2.json')
    store_red = load('corrections-store-red1-V2.json')
    assert classic_red['native']['code'] != 0 and 'wp_woocommerce_sessions.session_value' in classic_red['native']['stdout'] and classic_red['restored']
    assert store_red['native']['code'] != 0 and 'wp_woocommerce_sessions.session_value' in store_red['native']['stdout'] and store_red['restored']
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES) == {name:c.core.digest(ROOT/'wp'/name) for name in owner.FILES}
        with c.bound(owner):
            c.core.live_registration('C31', owner.wp, owner.php)
    return {'native':46,'browser_registration':16,'browser_compte':29,'browser_store_checkout':13,'offline_package_tests':int(match[1]),'offline_package_assertions':int(match[2]),'offline_c31_tests':9,'offline_c31_assertions':64,'style_psr12_errors':0}
def global_gates():
    image = load('corrections-image-V2.json')
    assert image['exit'] == 0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay = load('corrections-replay-V2.json')
    text = (OUT/replay['log']).read_text(encoding='utf-8')
    assert replay['exit'] == 0 and 'DomainesRefusesC31AdapterTest' in text
    result = json.loads(re.search(r'^T01_RESULT (.+)$', text, re.M)[1])
    assert result['pass'] and result['failures'] == result['errors'] == result['skipped'] == result['tools']['failures'] == 0
    assert all(item['lot'] in ['A-32','A-33','A-34'] for item in result['packets']['failures'])
    return result
def verify(live=False, manifest=None, require_pret=True):
    c.integrity(owner, manifest or load(RECEIPT))
    answer = local(live)
    result = global_gates()
    if require_pret:
        assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    answer.update(C31='PASS', global_tests=result['tests'], global_assertions=result['assertions'], tools=result['tools'])
    print(json.dumps(answer, ensure_ascii=False))
    return answer
if __name__ == '__main__':
    assert sys.argv[1:] in [[],['--live'],['--pre-final'],['--pre-final','--live']]
    if '--pre-final' in sys.argv:
        answer = local('--live' in sys.argv)
        answer.update(C31='CORRECTIONS_LOCALES_PASS', PRET=False, pending='Image et rejeu global uniques du parent après C32')
        assert not (OUT/'PRET').exists()
        print(json.dumps(answer, ensure_ascii=False))
    else:
        verify('--live' in sys.argv)
