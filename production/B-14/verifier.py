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

def load(name): return json.loads((OUT/name).read_text(encoding='utf-8'))

def verify(live=False, manifest=None, require_pret=True):
    m = manifest or load('reception-V2.json')
    c.integrity(owner, m)
    native = load('native-final-V2.json')
    assert native['restored'] and native['before'] == native['after']
    assert native['sources'] == owner.sources(owner), 'TESTED_NATIVE_BYTES'
    assert native['native']['code'] == 0 and not native['native']['stderr']
    nd = json.loads(native['native']['stdout'])
    assert nd['total'] == len(nd['checks']) == 17 and all(nd['checks'].values())
    browser = load('browser-final-V2.json')
    assert browser['total'] == len(browser['checks']) == 37 and all(browser['checks'].values())
    assert browser['sources'] == owner.sources(owner), 'TESTED_BROWSER_BYTES'
    assert browser['restored'] and browser['session_restored'] and browser['probe_removed'] and browser['error'] is None
    assert browser['markers_count'] > 10 and len(browser['rows']) == 2
    want = ['numero','conversion','reportage','newsletter','thematiques','evenements','soutenir','cooperative','partenaire']
    assert all(row['sections'] == want and row['observation'] == {'http': [], 'mail': []} and row['buy'] == 0 for row in browser['rows'])
    assert browser['external'] == []
    red = load('red-V2.json')
    assert red['restored'] and red['native']['code'] != 0 and 'B14 accueil absent' in red['native']['stderr']
    image = load('image-V2.json')
    assert image['exit'] == 0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay = load('replay-V2.json')
    text = (OUT/replay['log']).read_text(encoding='utf-8')
    result = json.loads(re.search(r'^T01_RESULT (.+)$', text, re.M)[1])
    assert result['pass'] and result['failures'] == result['errors'] == result['skipped'] == result['tools']['failures'] == 0
    assert re.search('REJEU .*PASS', text) and 'OUTILS :' in text
    assert all(r['lot'] in ['A-31','A-32','A-33'] for r in result['packets']['failures'])
    tests = []
    for _, xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END', text, re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class') == 'Imagine\\Site\\Tests\\AccueilB14Test')
    assert len(tests) == 1 and all(t.find('failure') is None and t.find('error') is None for t in tests)
    if require_pret:
        assert 'reception-V2.json' in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES) == {n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):
            c.core.live_registration('B14', owner.wp, owner.php)
    answer = {'B14':'PASS','native':nd['total'],'browser':browser['total'],'surfaces':len(browser['rows']),'phpunit':len(tests),'replay_tests':result['tests'],'replay_assertions':result['assertions'],'tools':result['tools'],'foreign_packets':result['packets']['failures']}
    print(json.dumps(answer, ensure_ascii=False))
    return answer

if __name__ == '__main__':
    assert sys.argv[1:] in [[], ['--live']]
    verify(bool(sys.argv[1:]))
