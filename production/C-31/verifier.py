import sys
sys.dont_write_bytecode=True
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import c31 as owner
s=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    c.integrity(owner,manifest or load(RECEIPT))
    n=load('native-final-V2.json');d=json.loads(n['native']['stdout'])
    assert n['sources']==owner.sources(owner) and n['restored'] and n['before']==n['after'] and n['native']['code']==0 and not n['native']['stderr']
    assert d['total']==len(d['checks'])==32 and all(d['checks'].values())
    b=load('browser-final-V2.json')
    assert b['sources']==owner.sources(owner) and b['total']==len(b['checks'])==16 and all(b['checks'].values())
    assert len(b['rows'])==2 and b['error'] is None and b['restored'] and b['sessions_restored'] and b['probe_removed'] and not b['external']
    wp,woo=b['rows'];assert wp['kind']=='wp' and woo['kind']=='woo'
    assert wp['observation']['mail']==[] and len(wp['observation']['http'])==2 and all('translations_api' in x['trace'] for x in wp['observation']['http'])
    assert woo['observation']=={'http':[],'mail':[]}
    assert load('red-V2.json')['native']['code']!=0 and load('seed-V2.json')['idempotent']
    st=load('standard-V2.json');assert st['register_new_user']['hooks']==['registration_errors'] and st['wc_create_new_customer']['hooks']==['woocommerce_registration_errors'] and st['WC_Checkout::process_customer']['calls_native_customer']
    i=load('image-V2.json');assert i['exit']==0 and 'image verifiee sha256:' in (OUT/i['log']).read_text(encoding='utf-8')
    rr=load('replay-V2.json');text=(OUT/rr['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0 and 'DomainesRefusesC31Test' in text
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard();import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('C31',owner.wp,owner.php)
    answer={'C31':'PASS','native':32,'browser':16,'forms':2,'wp_core_translation_attempts_blocked':2,'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
