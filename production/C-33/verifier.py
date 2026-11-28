import sys
sys.dont_write_bytecode=True
import importlib.util,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import c33 as owner
s=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    c.integrity(owner,manifest or load(RECEIPT))
    n=load('native-final-V2.json');d=json.loads(n['native']['stdout'])
    assert n['sources']==owner.sources(owner) and n['restored'] and n['before']==n['after'] and n['native']['code']==0 and not n['native']['stderr']
    assert d['total']==len(d['checks'])==14 and all(d['checks'].values())
    b=load('browser-final-V2.json')
    assert b['sources']==owner.sources(owner) and b['total']==len(b['checks'])==53 and all(b['checks'].values())
    assert len(b['rows'])==19 and b['error'] is None and b['restored'] and b['fixture_removed'] and b['probe_removed'] and not b['external']
    assert len([r for r in b['rows'] if r['mutant']])==6 and all(r['ok']!=r['mutant'] for r in b['rows'])
    assert not b['private_sitemap_findings'] and set(b['sitemap_types'])=={'post','page','product','imagine_numero','imagine_evenement','imagine_partenaire'} and b['baseline_sitemap_disabled']
    for row in b['rows']:
        raw=(OUT/row['response']).read_text(encoding='utf-8');body=raw.split('\n\n',1)[1]
        assert hashlib.sha256(body.encode()).hexdigest()==row['body_sha256'] and 'set-cookie' not in json.dumps(row['headers']).lower()
    assert load('red-V2.json')['native']['code']!=0
    st=load('standard-V2.json');assert len(st['official'])==5 and st['native']['blog_public']=='0'
    i=load('image-V2.json');assert i['exit']==0 and 'image verifiee sha256:' in (OUT/i['log']).read_text(encoding='utf-8')
    rr=load('replay-V2.json');text=(OUT/rr['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0 and 'ComptesPublicsC33Test' in text
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard();import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('C33',owner.wp,owner.php)
    answer={'C33':'PASS','native':14,'browser':53,'responses':19,'mutations':6,'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
