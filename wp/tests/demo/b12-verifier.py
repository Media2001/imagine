"""B12 offline acceptance; --live only reads the guarded fictitious demo."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import b12
OUT=b12.OUT

def load(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def native(receipt, mutant):
    assert receipt['business_preserved'] and receipt['probe_removed'], 'RESTORATION'
    result=receipt['native'];assert result['code']==0 and not result['stderr'], 'NATIVE_EXECUTION'
    data=json.loads(result['stdout'])
    assert data['mutant'] is mutant and data['checks'] and data['total']==len(data['checks']) and all(data['checks'].values()), 'CHECKS'
    assert len(data['ids_removed'])==2 and len(set(data['ids_removed']))==2, 'TWO_POSTS'
    assert data['transport']==0, 'TRANSPORT'
    if mutant:
        assert len(data['events'])>0 and all(e['blocked'] for e in data['events']), 'B00'
        assert {'save','render','preview'}<={e['phase'].split('_')[0] for e in data['events']}, 'MUTATION_SURFACES'
    else:
        assert data['events']==[], 'ZERO_ATTEMPTS'
        required={'zero_tentative_save_render_preview','zero_tentative_tous_settings','interne_handler_delegue','interne_resolution_identique','interne_bloc_identique','interne_proxy_natif_identique','cache_ancien_ne_sort_pas','bloc_enregistre_ancien_ne_sort_pas','proxy_cache_ancien_ne_sort_pas','lien_ordinaire_inchange','proxy_permissions_natives_conservees'}
        required|={'matrix_'+surface+'_'+mode+'_'+i for surface in ['corps_exact','rendu_lien','apercu_lien'] for mode in ['0','1'] for i in ['0','1']}
        assert required<=set(data['checks']), 'MATRIX_INCOMPLETE'
    return data

def verify(live=False,manifest=None,require_pret=True):
    m=manifest or load('reception-V2.json')
    assert m['scope']=='imagine-test-demo' and m['ready'] is True
    assert m['sources']==b12.sources(), 'SOURCES'
    assert m['evidence'] and all(digest(OUT/name)==sha for name,sha in m['evidence'].items()), 'EVIDENCE'
    assert m['readme_section']==hashlib.sha256((ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## B-12 — aucun appel sortant depuis le corps',1)[1].strip().encode()).hexdigest()
    green=load(m['green']);mutation=load(m['mutation'])
    a=native(green,False);b=native(mutation,True)
    assert green['sources']==mutation['sources']==m['sources'], 'FINAL_TESTED_BYTES'
    red=load('red-verrou-absent-V2.json'); assert red['native']['code']!=0 and 'apercu_0_lien' in red['native']['stderr'] and red['business_preserved'] and red['probe_removed'], 'TDD_RED'
    first=native(load('red-mutation-native-V2.json'),True)
    image=load('image-rebuilt-V2.json');assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay=load('replay-corrected-V2.json'); text=(OUT/replay['log']).read_text(encoding='utf-8')
    totals=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert replay['exit']==0 and totals['pass'] and totals['tests']>1100 and totals['failures']==totals['errors']==totals['skipped']==0
    assert totals['tools']['failures']==0 and all(f['lot'] in ['A-31','A-32'] for f in totals['packets']['failures'])
    unit=[]
    for _,xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END',text,re.S):
        unit.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class')=='Imagine\\Site\\Tests\\IntegrationsCorpsB12Test')
    assert len(unit)==5 and all(t.find('failure') is None and t.find('error') is None for t in unit), 'PHPUNIT_DISCOVERED'
    neighbors=load(m['neighbors'])
    assert neighbors['status']=='PASS' and neighbors['business_preserved'] and neighbors['all_other_component_bytes_exact'] and neighbors['UI_save_verified'] is False
    assert neighbors['checks']=={'C27':628,'B11_offline':32,'B11_live':35,'C28_offline':31,'C28_live':37}
    assert all(digest(ROOT/n)==sha for n,sha in neighbors['historical_receipts_unchanged'].items()), 'NEIGHBOR_HISTORY'
    lint=load('lint-final-V2.json');assert lint['exit']==0 and not lint['stderr'] and lint['files'] and len(lint['files'])==len(lint['stdout'].splitlines())
    if require_pret:assert (OUT/'PRET').is_file() and 'reception-V2.json' in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        b12.guard()
        assert b12.b11.b10.b09.b08.c25.b06.hashes(b12.FILES)=={n:digest(ROOT/'wp'/n) for n in b12.FILES}
        ids=a['ids_removed']+b['ids_removed']
        check=b12.wp('$o=["probes_absent"=>!file_exists(WP_CONTENT_DIR."/imagine-demo-build/b12-runtime.php"),"posts_absent"=>true,"test_titles_absent"=>count(get_posts(["post_type"=>"post","post_status"=>"any","s"=>"B12 ESSAI FICTIF TEMPORAIRE","numberposts"=>-1]))===0];foreach('+b12.php(ids)+' as $id){$o["posts_absent"]=$o["posts_absent"]&&get_post($id)===null;}echo wp_json_encode($o);')
        assert check and all(check.values()), 'LIVE_RESTORATION'
    result={'B12':'PASS','mode':'live-readonly' if live else 'offline','native_checks':a['total'],'mutation_checks':b['total'],'mutation_attempts':len(b['events']),'attempts_with_lock':len(a['events']),'phpunit_tests':len(unit),'phpunit_assertions':sum(int(t.get('assertions')) for t in unit),'global_tests':totals['tests'],'global_assertions':totals['assertions'],'foreign_packet_failures':totals['packets']['failures']}
    print(json.dumps(result,ensure_ascii=False));return result

# Historical reader retained unchanged above; current correction is a new receipt,
# not a rewritten fingerprint or a SOURCES exception.
verify_historical = verify
BOOT = 'wp/plugins/imagine-site/imagine-site.php'
C29_BLOCK = "// C29 — projection en lecture seule, aucun connecteur.\nrequire_once __DIR__ . '/ContactBrevoRegles.php';\nrequire_once __DIR__ . '/ContactBrevo.php';\nContactBrevo::register();\n\n"

def bootstrap(raw=None):
    raw = (ROOT/BOOT).read_bytes() if raw is None else raw
    cdir = ROOT/'production/C-29'
    cm = json.loads((cdir/'reception-V2.json').read_text(encoding='utf-8'))
    companion = json.loads((cdir/'reception-complement-voisins-V2.json').read_text(encoding='utf-8'))
    assert digest(cdir/'reception-complement-voisins-V2.json') == cm['evidence']['reception-complement-voisins-V2.json'], 'C29_COMPANION_SEAL'
    assert companion['status']=='PASS' and companion['business_preserved'] and companion['all_other_component_bytes_exact'] and companion['unrelated_bootstrap_tamper_rejected'], 'C29_COMPANION'
    assert companion['exact_owned_block'] == C29_BLOCK and raw.count(C29_BLOCK.encode())==1, 'C29_EXACT_BLOCK'
    assert raw.count(b12.BLOCK.encode())==1, 'B12_EXACT_REGISTRATION'
    stripped = raw.replace(C29_BLOCK.encode(), b'', 1)
    legacy = load('reception-V2.json')['sources'][BOOT]
    assert hashlib.sha256(raw).hexdigest() == companion['bootstrap_current'] == cm['sources'][BOOT], 'CURRENT_BOOTSTRAP'
    assert hashlib.sha256(stripped).hexdigest() == companion['bootstrap_without_only_C29'] == legacy, 'ONLY_C29_DELTA'
    # Predecessor B12 registration is therefore exact, byte for byte, as are all
    # other bootstrap bytes. No canonical source dictionary is substituted.
    for name, expected in companion['historical_receipts_and_PRET_unchanged'].items():
        target = OUT/'PRET-avant-corrections-V2' if name=='production/B-12/PRET' else ROOT/name
        assert digest(target)==expected, 'HISTORICAL_RECEIPTS'
    import c29
    assert cm['sources']==c29.sources(), 'C29_SOURCES'
    section=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## C-29 — la fiche du contact pour Brevo, sans Brevo\n',1)[1].split('## B-12 — aucun appel sortant depuis le corps',1)[0]
    assert hashlib.sha256(section.encode()).hexdigest()==cm['readme_section'], 'C29_README'
    assert all(digest(cdir/n)==s for n,s in cm['evidence'].items()), 'C29_EVIDENCE'
    import c28
    for owner, receipt in [(b12.b11,'production/B-11/reception-politique1330-V2.json'),(c28,'production/C-28/reception-corrections.json')]:
        old=json.loads((ROOT/receipt).read_text(encoding='utf-8'))['sources']
        actual=owner.sources()
        assert set(old)==set(actual) and {n for n in old if old[n]!=actual[n]}=={BOOT}, 'NEIGHBOR_COMPONENT_BYTES'
        assert hashlib.sha256(stripped.replace(b12.BLOCK.encode(),b'',1)).hexdigest()==old[BOOT], 'NEIGHBOR_BOOTSTRAP_PORTION'
    return {'bootstrap_current': hashlib.sha256(raw).hexdigest(), 'without_only_C29': legacy, 'C29_exact_block': True, 'B12_registration_exact': True, 'C29_sources_and_evidence_exact': True, 'historical_B12_PRET_archive': 'PRET-avant-corrections-V2', 'C29_complement_sha256': digest(cdir/'reception-complement-voisins-V2.json'), 'C29_functional_bootstrap_untouched': True}

def routes(receipt, red=False):
    assert receipt['business_preserved'] and receipt['probe_removed'], 'ROUTE_RESTORATION'
    n=receipt['native'];d=json.loads(n['stdout'])
    assert d['checks'] and d['total']==len(d['checks'])==52 and d['transport']==0, 'ROUTE_CHECKS'
    assert {(c['route'],c['cache']) for c in d['cases']}=={(r,c) for r in ['/oembed/1.0/proxy','/oembed/1.0/PROXY','/oembed/1.0/PrOxY'] for c in ['absent','ancien']} and len(d['cases'])==6, 'ROUTE_MATRIX'
    required={f'{i}_{cache}_{suffix}' for i in range(3) for cache in ['absent','ancien'] for suffix in ['route_native','lien_seul','jamais_iframe_vignette','zero_tentative','anonyme_refuse','edit_posts_revoque_refuse','transient_retire']}
    required|={f'{i}_ancien_temoin_cache_natif' for i in range(3)}
    assert required<=set(d['checks']), 'ROUTE_REQUIRED'
    assert len(d['transients_removed'])==len(set(d['transients_removed']))==6, 'ROUTE_CLEANUP'
    if red:
        assert n['code']!=0 and 'B12_ROUTE_CASE' in n['stderr'] and not all(d['checks'].values()), 'ROUTE_RED'
        assert len(d['events'])==2 and all(e['blocked'] for e in d['events']), 'ROUTE_RED_ATTEMPTS'
        assert all(c['attempts']>0 for c in d['cases'] if c['route']!='/oembed/1.0/proxy' and c['cache']=='absent'), 'ROUTE_RED_UNCACHED'
        assert all('<iframe' in c['data'].get('html','') and 'thumbnail_url' in c['data'] for c in d['cases'] if c['route']!='/oembed/1.0/proxy' and c['cache']=='ancien'), 'ROUTE_RED_CACHE'
    else:
        assert n['code']==0 and not n['stderr'] and all(d['checks'].values()), 'ROUTE_GREEN'
        assert d['events']==[] and all(c['attempts']==0 for c in d['cases']), 'ROUTE_ZERO'
        assert all(c['status']==200 and list(c['data'])==['version','type','html'] and c['data']['type']=='link' and '<a href=' in c['data']['html'] and not re.search(r'<(?:iframe|img|script)\b',c['data']['html'],re.I) for c in d['cases']), 'ROUTE_LINK_ONLY'
    return d

def verify_correction(live=False,manifest=None,require_pret=True):
    m=manifest or load('reception-corrections-V2.json')
    assert m['scope']=='imagine-test-demo' and m['ready'] is True
    assert m['sources']==b12.sources(), 'SOURCES'
    assert m['evidence'] and all(digest(OUT/n)==s for n,s in m['evidence'].items()), 'EVIDENCE'
    assert m['readme_section']==hashlib.sha256((ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## B-12 — aucun appel sortant depuis le corps',1)[1].strip().encode()).hexdigest(), 'README'
    assert bootstrap()==load(m['bootstrap']), 'BOOTSTRAP_COMPLEMENT'
    r=routes(load(m['routes']));routes(load('correction-red-route-V2.json'),True)
    routes(load('correction-mutation-case-V2-rejet.json'),True)
    restore=load('correction-mutation-case-V2.json');assert restore['source_restored'] and restore['business_preserved'], 'SOURCE_MUTATION_RESTORED'
    a=native(load(m['green']),False);b=native(load(m['mutation']),True)
    for name in [m['routes'],m['green'],m['mutation']]:assert load(name)['sources']==m['sources'], 'FINAL_TESTED_BYTES'
    image=load(m['image']);assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8'), 'IMAGE'
    replay=load(m['replay']);text=(OUT/replay['log']).read_text(encoding='utf-8')
    totals=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert replay['exit']==0 and totals['pass'] and totals['tests']>1203 and totals['failures']==totals['errors']==totals['skipped']==0, 'REPLAY'
    assert totals['tools']['failures']==0 and all(f['lot'] in ['A-31','A-32'] for f in totals['packets']['failures']), 'FOREIGN_PACKETS'
    tests=[]
    for _,xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END',text,re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class')=='Imagine\\Site\\Tests\\IntegrationsCorpsB12Test')
    assert len(tests)==6 and all(t.find('failure') is None and t.find('error') is None for t in tests), 'PHPUNIT_CASE_TEST'
    lint=load(m['lint']);assert lint['exit']==0 and not lint['stderr'] and len(lint['files'])==len(lint['stdout'].splitlines()), 'LINT'
    if require_pret:assert 'reception-corrections-V2.json' in (OUT/'PRET').read_text(encoding='utf-8'), 'CURRENT_PRET'
    if live:
        b12.guard()
        assert b12.b11.b10.b09.b08.c25.b06.hashes(b12.FILES)=={n:digest(ROOT/'wp'/n) for n in b12.FILES}, 'LIVE_SOURCES'
        ids=a['ids_removed']+b['ids_removed'];keys=r['transients_removed']
        restored=b12.wp('$o=["probes_absent"=>!file_exists(WP_CONTENT_DIR."/imagine-demo-build/b12-runtime.php")&&!file_exists(WP_CONTENT_DIR."/imagine-demo-build/b12-routes-runtime.php"),"posts_absent"=>true,"transients_absent"=>true,"titles_absent"=>count(get_posts(["post_type"=>"post","post_status"=>"any","s"=>"B12 ESSAI FICTIF TEMPORAIRE","numberposts"=>-1]))===0];foreach('+b12.php(ids)+' as $id){$o["posts_absent"]=$o["posts_absent"]&&get_post($id)===null;}foreach('+b12.php(keys)+' as $key){$o["transients_absent"]=$o["transients_absent"]&&get_transient($key)===false;}echo wp_json_encode($o);')
        assert all(restored.values()), 'LIVE_RESTORATION'
    result={'B12':'PASS','mode':'live-readonly' if live else 'offline','native_checks':a['total'],'route_checks':r['total'],'route_cases':len(r['cases']),'attempts_with_lock':len(a['events'])+len(r['events']),'mutation_checks':b['total'],'mutation_attempts':len(b['events']),'phpunit_tests':len(tests),'phpunit_assertions':sum(int(t.get('assertions')) for t in tests),'global_tests':totals['tests'],'global_assertions':totals['assertions'],'foreign_packet_failures':totals['packets']['failures']}
    print(json.dumps(result,ensure_ascii=False));return result

def verify_contract(live=False,manifest=None,require_pret=True):
    m=manifest or load('reception-contrat-V2.json')
    assert m['scope']=='imagine-test-demo' and m['ready'] is True
    assert m['sources']==b12.contract_sources(), 'SOURCES'
    assert m['bootstrap_contract']==b12.contract_block(), 'BOOTSTRAP_CONTRACT'
    assert m['readme_section']==hashlib.sha256(b12.readme_section().encode()).hexdigest(), 'README_SECTION'
    assert m['evidence'] and all(digest(OUT/n)==s for n,s in m['evidence'].items()), 'EVIDENCE'
    r=routes(load(m['routes']));a=native(load(m['green']),False);b=native(load(m['mutation']),True)
    routes(load('correction-red-route-V2.json'),True)
    routes(load('correction-mutation-case-V2-rejet.json'),True)
    inverse=load('correction-mutation-case-V2.json');assert inverse['source_restored'] and inverse['business_preserved'], 'SOURCE_MUTATION_RESTORED'
    for name in [m['routes'],m['green'],m['mutation']]:
        n=load(name)
        owned={k:v for k,v in n['sources'].items() if k!=BOOT}
        assert owned==m['sources'], 'FINAL_TESTED_OWNED_BYTES'
        assert n['bootstrap_contract']==m['bootstrap_contract'], 'TESTED_BOOTSTRAP_BLOCK'
    image=load(m['image']);assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8'), 'IMAGE'
    replay=load(m['replay']);text=(OUT/replay['log']).read_text(encoding='utf-8')
    totals=json.loads(re.search(r'^T01_RESULT (.+)$',text,re.M)[1])
    assert replay['exit']==0 and totals['pass'] and totals['failures']==totals['errors']==totals['skipped']==0, 'REPLAY'
    assert totals['tools']['failures']==0 and all(f['lot'] in ['A-31','A-32'] for f in totals['packets']['failures']), 'FOREIGN_PACKETS'
    tests=[]
    for _,xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END',text,re.S):
        tests.extend(t for t in ET.fromstring(xml.strip()).iter('testcase') if t.get('class')=='Imagine\\Site\\Tests\\IntegrationsCorpsB12Test')
    assert len(tests)==6 and all(t.find('failure') is None and t.find('error') is None for t in tests), 'PHPUNIT_CASE_TEST'
    lint=load(m['lint']);assert lint['exit']==0 and not lint['stderr'] and len(lint['files'])==len(lint['stdout'].splitlines()), 'LINT'
    if require_pret:assert 'reception-contrat-V2.json' in (OUT/'PRET').read_text(encoding='utf-8'), 'CURRENT_PRET'
    if live:
        b12.guard()
        assert b12.b11.b10.b09.b08.c25.b06.hashes([b12.FILES[0]])[b12.FILES[0]]==digest(ROOT/'wp'/b12.FILES[0]), 'LIVE_SOURCE'
        restored=b12.wp('$raw=file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php");$o=["own_block_exact"=>substr_count($raw,'+b12.php(b12.BLOCK)+')===1,"probes_absent"=>!file_exists(WP_CONTENT_DIR."/imagine-demo-build/b12-runtime.php")&&!file_exists(WP_CONTENT_DIR."/imagine-demo-build/b12-routes-runtime.php"),"posts_absent"=>true,"transients_absent"=>true,"titles_absent"=>count(get_posts(["post_type"=>"post","post_status"=>"any","s"=>"B12 ESSAI FICTIF TEMPORAIRE","numberposts"=>-1]))===0];foreach('+b12.php(a['ids_removed']+b['ids_removed'])+' as $id){$o["posts_absent"]=$o["posts_absent"]&&get_post($id)===null;}foreach('+b12.php(r['transients_removed'])+' as $key){$o["transients_absent"]=$o["transients_absent"]&&get_transient($key)===false;}echo wp_json_encode($o);')
        assert all(restored.values()), 'LIVE_CONTRACT_AND_RESTORATION'
    result={'B12':'PASS','contract':'owned-files + exact unique B12 bootstrap block + bounded B12 README section','mode':'live-readonly' if live else 'offline','native_checks':a['total'],'route_checks':r['total'],'route_cases':len(r['cases']),'attempts_with_lock':len(a['events'])+len(r['events']),'mutation_attempts':len(b['events']),'phpunit_tests':len(tests),'phpunit_assertions':sum(int(t.get('assertions')) for t in tests),'global_tests':totals['tests'],'global_assertions':totals['assertions'],'foreign_packet_failures':totals['packets']['failures']}
    print(json.dumps(result,ensure_ascii=False));return result

def verify(live=False,manifest=None,require_pret=True):
    if manifest is not None:
        if 'contract_version' in manifest:return verify_contract(live,manifest,require_pret)
        if 'correction_version' in manifest:return verify_correction(live,manifest,require_pret)
        return verify_historical(live,manifest,require_pret)
    return verify_contract(live,None,require_pret)

if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
