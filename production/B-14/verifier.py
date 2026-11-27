"""Réception B14 bornée ; aucune empreinte entière du bootstrap partagé."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'wp/outils/demo'), str(ROOT/'wp/tests/demo')]
import b14 as owner
spec = importlib.util.spec_from_file_location('b13_contract', ROOT/'wp/tests/demo/b13-contract.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
OUT = owner.OUT
RECEIPT = 'reception-corrections-V2.json'

def load(name): return json.loads((OUT/name).read_text(encoding='utf-8'))

def verify(live=False, manifest=None, require_pret=True):
    m = manifest or load(RECEIPT)
    c.integrity(owner, m)
    native = load('native-corrections-final-V2.json')
    assert native['restored'] and native['before'] == native['after']
    assert native['sources'] == owner.sources(owner), 'TESTED_NATIVE_BYTES'
    assert native['native']['code'] == 0 and not native['native']['stderr']
    nd = json.loads(native['native']['stdout'])
    assert nd['total'] == len(nd['checks']) == 22 and all(nd['checks'].values())
    assert all(nd['checks'][key] for key in ['ancre_abonnement_paywall_contrat','b04_appelle_helper_unique','deux_libres_ordre_distinct_identite_b04','deux_libres_departage_id_identite_b04'])
    browser = load('browser-corrections-final-V2.json')
    assert browser['total'] == len(browser['checks']) == 52 and all(browser['checks'].values())
    assert browser['sources'] == owner.sources(owner), 'TESTED_BROWSER_BYTES'
    assert browser['restored'] and browser['session_restored'] and browser['probe_removed'] and browser['error'] is None
    assert browser['markers_count'] > 10 and len(browser['rows']) == 2
    want = ['numero','conversion','reportage','newsletter','thematiques','evenements','soutenir','cooperative','partenaire']
    assert all(row['sections'] == want and row['observation'] == {'http': [], 'mail': []} and row['buy'] == 0 for row in browser['rows'])
    assert browser['external'] == []
    assert browser['checks']['paywall_atteint_conversion_avec_cta']
    companion = load('complement-B11-corrections-V2.json')
    assert companion['business_preserved'] and companion['native']['code'] == 0 and not companion['native']['stderr']
    checks = json.loads(companion['native']['stdout'])
    assert checks['total'] == len(checks['checks']) == 23 and all(checks['checks'].values())
    assert companion['sources']['wp/themes/imagine/single-imagine_numero.php'] == c.core.digest(ROOT/'wp/themes/imagine/single-imagine_numero.php')
    assert load('complement-B11-corrections-V2-source.json')['only_approved_free_selection_change'] is True
    legacy = load('legacy-B01-corrections-V2.json')
    assert [row['exit'] for row in legacy['legacy_runs']] == [1,1] and legacy['all_legacy_pass'] is False
    assert 'Published article inventory differs' in legacy['legacy_runs'][1]['error']
    drift = load('derive-comptage-V2.json')
    assert drift['added_assertions'] == 5 and len(drift['added']) == 2 and not drift['removed']
    assert all(row['class'] == 'Imagine\\Site\\Tests\\PiedPageB15Test' for row in drift['added'])
    red = load('red-V2.json')
    assert red['restored'] and red['native']['code'] != 0 and 'B14 accueil absent' in red['native']['stderr']
    image = load('image-corrections-V2.json')
    assert image['exit'] == 0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay = load('replay-corrections-V2.json')
    text = (OUT/replay['log']).read_text(encoding='utf-8')
    result = json.loads(re.search(r'^T01_RESULT (.+)$', text, re.M)[1])
    assert result['pass'] and result['failures'] == result['errors'] == result['skipped'] == result['tools']['failures'] == 0
    assert re.search('REJEU .*PASS', text) and 'OUTILS :' in text
    assert all(r['lot'] in ['A-31','A-32','A-33'] for r in result['packets']['failures'])
    tests = []
    for _, xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END', text, re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class') == 'Imagine\\Site\\Tests\\AccueilB14Test')
    assert len(tests) == 2 and all(t.find('failure') is None and t.find('error') is None for t in tests)
    assert any(t.get('name') == 'testStructureReelleRendueAvecBouchonsMinimaux' for t in tests)
    if require_pret:
        assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES) == {n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):
            c.core.live_registration('B14', owner.wp, owner.php)
    answer = {'B14':'PASS','native':nd['total'],'browser':browser['total'],'surfaces':len(browser['rows']),'phpunit':len(tests),'replay_tests':result['tests'],'replay_assertions':result['assertions'],'tools':result['tools'],'foreign_packets':result['packets']['failures'], 'legacy_B01':'2 legacy commands failed on prior contracts; current anchor HTTP PASS', 'B11_native_complement':23}
    print(json.dumps(answer, ensure_ascii=False))
    return answer

if __name__ == '__main__':
    assert sys.argv[1:] in [[], ['--live']]
    verify(bool(sys.argv[1:]))
