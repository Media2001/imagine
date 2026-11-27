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

if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
