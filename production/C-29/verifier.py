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
sys.path.insert(0,str(ROOT/'wp/tests/demo'))
import lot_reception_contract as contract
OUT=ROOT/'production/C-29'

def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def section():return (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## C-29 — la fiche du contact pour Brevo, sans Brevo\n',1)[1].split('## B-12 — aucun appel sortant depuis le corps',1)[0]

def native_receipt(r, expected=51):
    assert r['business_preserved'] and r['strict_before']==r['strict_after'], 'NATIVE_RESTORATION'
    n=r['native'];assert n['code']==0 and not n['stderr'], 'NATIVE_EXECUTION'
    d=json.loads(n['stdout'])
    assert d['total']==len(d['checks'])==expected and all(d['checks'].values()), 'NATIVE_CHECKS'
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

def historical_verify(live=False,manifest=None,require_pret=True):
    m=manifest or load('reception-contrat-V2.json')
    assert m['scope']=='imagine-test-demo' and m['ready'] is True
    contract.integrity('C29',m,OUT)
    assert m['evidence'] and all(digest(OUT/n)==sha for n,sha in m['evidence'].items()), 'EVIDENCE'
    p=load(m['pure']);assert p['exit']==0 and not p['stderr'] and contract.tested_sources('C29',p['sources'])
    pd=json.loads(p['stdout']);assert len(pd['checks'])==21 and all(pd['checks'].values())
    nr=load(m['native']);nd=native_receipt(nr)
    hr=http_receipt(load(m['http']))
    assert contract.tested_sources('C29',nr['sources']) and contract.tested_sources('C29',hr['sources']), 'TESTED_FINAL_BYTES'
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
    # Neighbor complements remain sealed historical evidence, never live gates.
    lint=load('lint-final-V2.json');assert lint['exit']==0 and not lint['stderr'] and len(lint['files'])==len(lint['stdout'].splitlines())
    assert load('demo-tarifs-idempotent-V2.json')['idempotent'] is True
    if require_pret:assert 'reception-contrat-V2.json' in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        import b11
        import b06
        b11.guard()
        owned=[n for n in c29.FILES if 'wp/'+n!=contract.BOOT]
        assert b06.hashes(owned)=={n:digest(ROOT/'wp'/n) for n in owned}, 'LIVE_CODE'
        contract.live_registration('C29',b11.wp,b11.php)
        result=b11.wp('''$f=get_option('imagine_c09_fixture');$map=[];foreach($f['tariffs'] as $code=>$id){$map[(string)$id]=$code;}echo wp_json_encode(['probe_absent'=>!file_exists(WP_CONTENT_DIR.'/mu-plugins/c29-observer.php'),'tarifs_fictifs'=>get_option(Imagine\\Site\\ContactBrevo::TARIFS)===$map,'payload_absent'=>get_option('imagine_c29_interdit',null)===null]);''')
        assert all(result.values()), 'LIVE_RESTORED'
    result={'C29':'PASS','receipt':'reception-contrat-V2.json','contract':'owned-files + unique exact own block + bounded own README','mode':'live-readonly' if live else 'offline','pure_checks':len(pd['checks']),'native_checks':nd['total'],'http_checks':hr['total'],'profiles':len(nd['profils']),'phpunit_tests':len(tests),'phpunit_assertions':sum(int(t.get('assertions')) for t in tests),'global_tests':counts['tests'],'global_assertions':counts['assertions'],'tool_checks':counts['tools']['checks'],'foreign_packet_failures':counts['packets']['failures']}
    print(json.dumps(result,ensure_ascii=False));return result
def verify(live=False, manifest=None, require_pret=True):
    m = manifest or load('reception-corrections-V2.json')
    assert m['scope'] == 'imagine-test-demo' and m['ready'] is True
    contract.integrity('C29', m, OUT)
    pure = load(m['pure'])
    assert pure['exit'] == 0 and not pure['stderr']
    checks = json.loads(pure['stdout'])['checks']
    assert len(checks) == 23 and all(checks.values())
    assert checks['refus_hors_catalogue'] and checks['suppression_choix_positif_sans_retrait']
    native = load(m['native'])
    nd = native_receipt(native, 57)
    assert all(nd['checks'][key] for key in [
        'groupe_etat_natif_relu_active', 'groupe_lien_natif_relu_active', 'beneficiaire_groupe_inconnu_active',
        'groupe_etat_natif_relu_paused', 'groupe_lien_natif_relu_paused', 'beneficiaire_groupe_inconnu_paused'])
    http = http_receipt(load(m['http']))
    current = c29.sources()
    for receipt in [pure, native, http]:
        assert receipt['sources'] == current, 'TESTED_FINAL_BYTES'
    assert all(row['fiche'] == nd['profils'][row['code']]['fiche'] for row in http['surfaces'])
    red = load('red-corrections-refus-V2.json')
    assert red['exit'] == 1 and 'refus_hors_catalogue' in red['stderr']
    red = load('red-corrections-groupe-cache-V2.json')
    assert red['business_preserved'] and red['native']['code'] == 1 and 'beneficiaire_groupe_inconnu_paused' in red['native']['stderr']
    image = load(m['image'])
    assert image['exit'] == 0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay = load(m['replay'])
    text = (OUT/replay['log']).read_text(encoding='utf-8')
    counts = json.loads(re.search(r'^T01_RESULT (.+)$', text, re.M)[1])
    assert counts['pass'] and counts['failures'] == counts['errors'] == counts['skipped'] == 0
    assert counts['tools']['failures'] == 0
    assert all(row['lot'] in ['A-31', 'A-32', 'A-33'] for row in counts['packets']['failures']), 'OWNED_PACKET_FAILURE'
    # A33 : paquet en cours sans PRET constaté au rejeu, aucune lecture V1.
    assert load('paquets-etrangers-V2.json') == {'A-33': {'pret_exists': False}}, 'FOREIGN_PACKET_STATE'
    assert re.search(r'REJEU .*PASS', text) and re.search(r'OUTILS .*', text)
    tests = []
    for _, xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END', text, re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class') == 'Imagine\\Site\\Tests\\ContactBrevoC29Test')
    assert len(tests) == 3 and all(t.find('failure') is None and t.find('error') is None for t in tests)
    if require_pret:
        assert 'reception-corrections-V2.json' in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        import b11, b06
        b11.guard()
        owned = [n for n in c29.FILES if 'wp/'+n != contract.BOOT]
        assert b06.hashes(owned) == {n: digest(ROOT/'wp'/n) for n in owned}
        contract.live_registration('C29', b11.wp, b11.php)
    result = {'C29': 'PASS', 'receipt': 'reception-corrections-V2.json', 'pure': len(checks), 'native': nd['total'], 'http': http['total'], 'profiles': len(nd['profils']), 'phpunit_tests': len(tests), 'foreign_packet_failures': counts['packets']['failures']}
    print(json.dumps(result, ensure_ascii=False))
    return result

if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
