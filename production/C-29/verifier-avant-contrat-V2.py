"""C29 offline evidence reader. --live reads only the unique guarded fictional demo."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import c29
OUT=ROOT/'production/C-29'

def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def section():return (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## C-29 — la fiche du contact pour Brevo, sans Brevo\n',1)[1].split('## B-12 — aucun appel sortant depuis le corps',1)[0]

def native_receipt(r):
    assert r['business_preserved'] and r['strict_before']==r['strict_after'], 'NATIVE_RESTORATION'
    n=r['native'];assert n['code']==0 and not n['stderr'], 'NATIVE_EXECUTION'
    d=json.loads(n['stdout'])
    assert d['total']==len(d['checks'])==51 and all(d['checks'].values()), 'NATIVE_CHECKS'
    assert len(d['profils'])==27 and sum(k.startswith('profil_') for k in d['checks'])==27, 'PROFILES'
    assert d['writes']==[] and d['outgoing']==[], 'NATIVE_ZERO'
    assert d['mutation']['positive'] and d['mutation']['negative']==[] and d['mutation']['leak_mutant'], 'CONSENT_WITNESS'
    assert d['checks']['mutation_temoin_absence_refusee'] and d['checks']['beneficiaire_offert_inconnu'] and d['checks']['beneficiaire_groupe_inconnu']
    return d

def http_receipt(r):
    assert r['business_preserved'] and r['sessions_restored'] and r['probe_removed'] and r['strict_before']==r['strict_after'], 'HTTP_RESTORATION'
    assert r['error'] is None and r['total']==len(r['checks'])==73 and all(r['checks'].values()), 'HTTP_CHECKS'
    assert len(r['observations'])==len(r['surfaces'])==27, 'HTTP_PROFILES'
    assert all({k:v for k,v in o.items() if k!='code'}=={'entered':True,'finished':True,'sql':[],'http':[],'mail':[]} for o in r['observations']), 'HTTP_ZERO'
    assert r['witness']=={'entered':True,'finished':True,'sql':['INSERT'],'http':['blocked'],'mail':['blocked']}, 'HTTP_WITNESS'
    assert all(e['blocked_before_transport'] and e['url'].startswith('https://secure.gravatar.com/') for e in r['external_browser']), 'BROWSER_NETWORK'
    return r

def verify(live=False,manifest=None,require_pret=True):
    m=manifest or load('reception-V2.json')
    assert m['scope']=='imagine-test-demo' and m['ready'] is True
    assert m['sources']==c29.sources(), 'FINAL_SOURCE_BYTES'
    assert m['readme_section']==hashlib.sha256(section().encode()).hexdigest(), 'README_SECTION'
    assert m['evidence'] and all(digest(OUT/n)==sha for n,sha in m['evidence'].items()), 'EVIDENCE'
    p=load(m['pure']);assert p['exit']==0 and not p['stderr'] and p['sources']==m['sources']
    pd=json.loads(p['stdout']);assert len(pd['checks'])==21 and all(pd['checks'].values())
    nr=load(m['native']);nd=native_receipt(nr)
    hr=http_receipt(load(m['http']))
    assert nr['sources']==hr['sources']==m['sources'], 'TESTED_FINAL_BYTES'
    assert all(row['fiche']==nd['profils'][row['code']]['fiche'] for row in hr['surfaces'])
    red=load('red-slice1-V2.json');assert red['exit']!=0 and 'C29 calcul pur absent' in red['stderr']
    red=load('red-native-V2.json');assert red['native']['code']!=0 and 'C29 adaptateur absent' in red['native']['stderr'] and red['business_preserved']
    red=load('red-native-matrix-V2.json');assert red['native']['code']!=0 and 'profil_A-CARTE' in red['native']['stderr'] and red['business_preserved']
    image=load(m['image']);assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay=load(m['replay']);text=(OUT/replay['log']).read_text(encoding='utf-8')
    counts=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert replay['exit']==0 and counts['pass'] and counts['failures']==counts['errors']==counts['skipped']==0
    assert counts['tools']['failures']==0 and all(f['lot'] in ['A-31','A-32'] for f in counts['packets']['failures'])
    tests=[]
    for _,xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END',text,re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class')=='Imagine\\Site\\Tests\\ContactBrevoC29Test')
    assert len(tests)==3 and all(t.find('failure') is None and t.find('error') is None for t in tests), 'PHPUNIT_DISCOVERED'
    neighbors=load(m['neighbors']);assert neighbors['status']=='PASS' and neighbors['business_preserved'] and neighbors['all_other_component_bytes_exact'] and neighbors['unrelated_bootstrap_tamper_rejected']
    assert all(digest(ROOT/n)==sha for n,sha in neighbors['historical_receipts_and_PRET_unchanged'].items()), 'HISTORICAL_PACKETS'
    assert neighbors['bootstrap_current']==digest(ROOT/'wp/plugins/imagine-site/imagine-site.php')
    assert {k:neighbors['checks'][k] for k in ['C27','B11_offline','B11_live','C28_offline','C28_live']}=={'C27':628,'B11_offline':32,'B11_live':35,'C28_offline':31,'C28_live':37}
    lint=load('lint-final-V2.json');assert lint['exit']==0 and not lint['stderr'] and len(lint['files'])==len(lint['stdout'].splitlines())
    assert load('demo-tarifs-idempotent-V2.json')['idempotent'] is True
    if require_pret:assert 'reception-V2.json' in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        import b11
        import b06
        b11.guard()
        assert b06.hashes(c29.FILES)=={n:digest(ROOT/'wp'/n) for n in c29.FILES}, 'LIVE_CODE'
        result=b11.wp('''$f=get_option('imagine_c09_fixture');$map=[];foreach($f['tariffs'] as $code=>$id){$map[(string)$id]=$code;}echo wp_json_encode(['probe_absent'=>!file_exists(WP_CONTENT_DIR.'/mu-plugins/c29-observer.php'),'tarifs_fictifs'=>get_option(Imagine\\Site\\ContactBrevo::TARIFS)===$map,'payload_absent'=>get_option('imagine_c29_interdit',null)===null]);''')
        assert all(result.values()), 'LIVE_RESTORED'
    result={'C29':'PASS','mode':'live-readonly' if live else 'offline','pure_checks':len(pd['checks']),'native_checks':nd['total'],'http_checks':hr['total'],'profiles':len(nd['profils']),'phpunit_tests':len(tests),'phpunit_assertions':sum(int(t.get('assertions')) for t in tests),'global_tests':counts['tests'],'global_assertions':counts['assertions'],'tool_checks':counts['tools']['checks'],'foreign_packet_failures':counts['packets']['failures']}
    print(json.dumps(result,ensure_ascii=False));return result
if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
