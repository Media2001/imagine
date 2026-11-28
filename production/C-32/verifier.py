import sys
sys.dont_write_bytecode=True
import importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import c32 as owner
s=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    c.integrity(owner,manifest or load(RECEIPT))
    n=load('native-final-V2.json');d=json.loads(n['native']['stdout'])
    assert n['sources']==owner.sources(owner) and n['restored'] and n['before']==n['after'] and n['native']['code']==0 and not n['native']['stderr']
    assert d['total']==len(d['checks'])==21 and all(d['checks'].values())
    b=load('browser-final-V2.json')
    assert b['sources']==owner.sources(owner) and b['total']==len(b['checks'])==151 and all(b['checks'].values())
    assert len(b['rows'])==50 and b['error'] is None and b['restored'] and b['sessions_restored'] and b['probe_removed'] and not b['external']
    regular=[r for r in b['rows'] if not r['kind'].startswith('mutation_')]
    assert all(not r['unknown'] for r in regular)
    reading=[r for r in regular if r['kind']=='lecture'];assert len(reading)==44 and not b['zero_cookie_reading']
    assert all(not r['header_names'] and len(r['browser'])==7 and not r['zero_cookie_pass'] for r in reading)
    assert {r['kind'] for r in b['rows'] if r['unknown']}=={'mutation_header','mutation_script'}
    strict=load('strict-reading-V2.json');assert strict['status']=='FAIL' and strict['expected']==0 and strict['pages']==44
    assert load('red-V2.json')['native']['code']!=0 and load('recovery-essai-V2.json')['restored_exact_initial_state']
    st=load('standard-V2.json');assert len(st['official'])==3 and st['native']['attribution']=='yes'
    i=load('image-V2.json');assert i['exit']==0 and 'image verifiee sha256:' in (OUT/i['log']).read_text(encoding='utf-8')
    rr=load('replay-V2.json');text=(OUT/rr['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0 and 'CookiesC32Test' in text
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard();import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('C32',owner.wp,owner.php)
    answer={'C32':'PASS_INVENTAIRE','simple_lecture_zero_cookie':'FAIL_CONSTATE_NON_CORRIGE','native':21,'browser':151,'pages':44,'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
