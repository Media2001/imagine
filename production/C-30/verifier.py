import sys
sys.dont_write_bytecode=True
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import c30 as owner
spec=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-corrections-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    c.integrity(owner,manifest or load(RECEIPT))
    n=load('correction-native-final-V2.json');d=json.loads(n['native']['stdout'])
    assert n['native']['code']==0 and not n['native']['stderr'] and n['restored'] and n['before']==n['after'] and n['sources']==owner.sources(owner)
    assert d['total']==len(d['checks'])==32 and all(d['checks'].values())
    prices=d['price_comparison'];assert prices['quantity']==2 and prices['with']==prices['without'] and prices['with']['coupons']==[] and float(prices['with']['total'])>0 and float(prices['mutant']['total'])<float(prices['without']['total'])
    u=load('correction-unit-final-V2.json');assert u['exit']==0 and not u['stderr'] and u['sources']==owner.sources(owner) and 'OK (9 tests, 165 assertions)' in u['stdout']
    assert load('correction-recovery-essai2-V2.json')['restored_initial_exact']
    assert load('correction-red-invite-V2.json')['exit']!=0 and load('correction-red-store-api-V2.json')['exit']!=0
    b=load('correction-browser-final-V2.json');s=load('correction-browser-final-V2-sessions.json')
    assert b['sources']==s['sources']==owner.sources(owner) and b['total']==len(b['checks'])==99 and all(b['checks'].values())
    assert len(b['rows'])==10 and b['restored'] and b['session_restored'] and b['probe_removed'] and b['error'] is None and not b['external'] and s['restored']
    assert load('red-V2.json')['native']['code']!=0 and load('seed-V2.json')['idempotent']
    i=load('correction-image-V2.json');assert i['exit']==0 and 'image verifiee sha256:' in (OUT/i['log']).read_text(encoding='utf-8')
    rr=load('correction-replay-V2.json');text=(OUT/rr['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0 and 'CodesSuivisC30AdapterTest' in text
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('C30',owner.wp,owner.php)
    answer={'C30_corrections':'PASS','native':32,'adapter_tests':9,'adapter_assertions':165,'price_without':prices['without']['total'],'price_with':prices['with']['total'],'price_mutant':prices['mutant']['total'],'browser':99,'responses':10,'sessions_restored':True,'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
