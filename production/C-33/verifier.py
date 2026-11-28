import sys
sys.dont_write_bytecode=True
import importlib.util,json,re,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'wp/outils/demo'),str(ROOT/'wp/tests/demo')]
import c33 as owner
import c33_control as controller
s=importlib.util.spec_from_file_location('contract',ROOT/'wp/tests/demo/b13-contract.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
OUT=owner.OUT
RECEIPT='reception-corrections-V2.json'
def load(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def verify(live=False,manifest=None,require_pret=True):
    c.integrity(owner,manifest or load(RECEIPT))
    n=load('native-corrections-V2.json');d=json.loads(n['native']['stdout'])
    assert n['sources']==owner.sources(owner) and n['restored'] and n['before']==n['after'] and n['native']['code']==0 and not n['native']['stderr']
    assert d['total']==len(d['checks'])==14 and all(d['checks'].values())
    b=load('browser-corrections-V2.json')
    assert b['sources']==owner.sources(owner) and b['total']==len(b['checks'])==89 and all(b['checks'].values())
    assert len(b['rows'])==20 and b['error'] is None and b['restored'] and b['fixture_removed'] and b['probe_removed'] and not b['external']
    assert len([r for r in b['rows'] if r['mutant']])==6 and all(r['ok']!=r['mutant'] for r in b['rows'])
    assert not b['private_sitemap_findings'] and set(b['sitemap_types'])=={'post','page','product','imagine_numero','imagine_evenement','imagine_partenaire'} and b['baseline_sitemap_disabled']
    proofs=b['proof_mutations']
    assert len(proofs)==5 and all(p['detected'] for p in proofs)
    assert {p['name'] for p in proofs}=={'P1-entete-hors-trois-noms',*['P2-auteur-absent-'+name for name in ['rss2','atom','rss2-repli','atom-repli']]}
    assert next(p for p in proofs if p['name'].startswith('P1'))['leak']
    assert all(p['present'] and p['author_fields']==0 for p in proofs if p['name'].startswith('P2'))
    feed_names=set()
    for row in b['rows']:
        raw=(OUT/row['response']).read_text(encoding='utf-8');archived,body=raw.split('\n\n',1);metadata=json.loads(archived)
        assert hashlib.sha256(body.encode()).hexdigest()==row['body_sha256']
        # Pas d'affirmation « aucun Set-Cookie » sur un dictionnaire qui le filtre.
        assert row['all_headers_inspected'] and row['headers_inspected']==len(row['header_names'])>0
        assert row['other_values_redacted'] is metadata['other_values_redacted'] is True
        assert metadata['header_names']==row['header_names'] and metadata['headers']==row['headers']
        assert set(row['headers']) <= controller.SAFE_HEADERS
        assert set(metadata)=={'status','headers','header_names','other_values_redacted'}
        assert metadata['status']==row['status']
        if row['kind']=='feed' and not row['mutant']:
            feed_names.add(row['name'])
            expected=b['site_name'] if row['name'].endswith('-repli') else 'SIGNATURE_FICTIVE_C33'
            assert isinstance(expected,str) and expected and row['expected_signature']==expected
            details=controller.feed_author(body,b['fixture_path'])
            assert details['present'] and details['author_fields']==1 and details['author']==expected and details['account_uri_absent']
            assert row['author']==expected and row['account_uri_absent'] and row['author_fields']==1
    assert feed_names=={'rss2','atom','rss2-repli','atom-repli'}
    redgreen=load('controleurs-red-green-corrections-V2.json')
    assert len(redgreen)==2 and redgreen[0]['exit']!=0 and redgreen[1]['exit']==0 and 'Ran 7 tests' in redgreen[1]['stderr']
    targeted=load('cible-corrections-V2.json');assert targeted['exit']==0 and 'OK (5 tests, 26 assertions)' in (OUT/targeted['log']).read_text(encoding='utf-8')
    assert load('red-V2.json')['native']['code']!=0
    st=load('standard-V2.json');assert len(st['official'])==5 and st['native']['blog_public']=='0'
    i=load('image-corrections-V2.json');assert i['exit']==0 and 'image verifiee sha256:' in (OUT/i['log']).read_text(encoding='utf-8')
    rr=load('replay-corrections-V2.json');text=(OUT/rr['log']).read_text(encoding='utf-8');r=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert r['pass'] and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0 and 'ComptesPublicsC33AdapterTest' in text
    assert all(x['lot'] in ['A-32','A-33','A-34'] for x in r['packets']['failures'])
    if require_pret:assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    regression=subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo/c33-control-tests.py')],cwd=ROOT,capture_output=True,encoding='utf-8')
    assert regression.returncode==0,regression.stderr
    if live:
        owner.guard();import b06
        assert b06.hashes(owner.FILES)=={n:c.core.digest(ROOT/'wp'/n) for n in owner.FILES}
        with c.bound(owner):c.core.live_registration('C33',owner.wp,owner.php)
    answer={'C33':'PASS','native':14,'browser':b['total'],'responses':len(b['rows']),'native_mutations':6,'proof_mutations':len(proofs),'control_tests':7,'tests':r['tests'],'assertions':r['assertions'],'tools':r['tools'],'packets':r['packets']}
    print(json.dumps(answer,ensure_ascii=False));return answer
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))

