"""Réception B16 par contrat commun inchangé, preuve finale bornée."""
import sys
sys.dont_write_bytecode=True
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import b16 as owner
spec=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    m=manifest or load(RECEIPT);c.integrity(owner,m)
    native=load('native-final5-V2.json');d=json.loads(native['native']['stdout'])
    assert native['native']['code']==0 and not native['native']['stderr'] and native['restored'] and native['before']==native['after']
    assert native['sources']==owner.sources(owner) and len(d['checks'])==d['total']==10 and all(d['checks'].values())
    browser=load('browser-final5-V2.json')
    assert browser['sources']==owner.sources(owner) and browser['restored'] and browser['error'] is None
    assert browser['total']==len(browser['checks'])==79 and all(browser['checks'].values()) and len(browser['rows'])==9 and browser['markers_count']>10 and not browser['external']
    assert load('red-V2.json')['native']['code']!=0
    image=load('image2-V2.json');assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay=load('replay2-V2.json');text=(OUT/replay['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0
    assert 'PageArticleB16Test' in text and re.search(r'REJEU .*PASS',text)
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('B16',owner.wp,owner.php)
    answer={'B16':'PASS','native':d['total'],'browser':browser['total'],'responses':9,'replay':{'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
