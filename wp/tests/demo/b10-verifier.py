"""B10 : vérification autonome des sources/preuves finales ; --live ajoute une lecture du site."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'production/B-10'


def verify(live=False):
    receipt=json.loads((OUT/'corrections-reception-V2.json').read_text(encoding='utf-8'))
    checked=0
    for relative,expected in receipt['sha256'].items():
        path=ROOT/relative
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        checked+=1
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(receipt['bootstrap_block'])==1,'Raccord B10 absent ou dupliqué'
    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    section='## B-10 — points de vente'+readme.split('## B-10 — points de vente',1)[1].split('\n## ',1)[0]
    assert receipt['readme_section']==section,'Section B10 du README divergente'
    refs=receipt['proofs']
    recipe=json.loads((OUT/refs['recipe']).read_text(encoding='utf-8'))
    assert recipe['checks'] and all(v is True for v in recipe['checks'].values())
    assert len(recipe['fixture_ids'])==len(set(recipe['fixture_ids']))==30
    assert recipe['restored_30_carte_off'] and recipe['private_snapshot']['private']
    assert len(recipe['checks'])==receipt['counts']['browser']
    assert set(recipe['map_observations'])=={'0','1'}
    for value,observation in recipe['map_observations'].items():
        assert observation['placeholder']==int(value) and observation['requests'] and observation['third_party']==[]
    native=json.loads((OUT/refs['native']).read_text(encoding='utf-8'))
    assert native['code']==0 and native['stderr']=='' and native['restored'] and native['transaction_rollback']
    native_checks=json.loads(native['stdout'])['checks']
    assert native_checks and all(v is True for v in native_checks.values())
    assert json.loads(native['stdout'])['normalizer_available'] is True
    assert len(native_checks)==receipt['counts']['native']
    for key in ['unit','fallback']:
        unit=(OUT/refs[key]).read_text(encoding='utf-8')
        assert f"OK ({receipt['counts']['unit_tests']} tests, {receipt['counts']['unit_assertions']} assertions)" in unit
        assert 'B10 NORMALIZER absent (repli latin)' in unit
    prep=(OUT/refs['image']).read_text(encoding='utf-8-sig')
    assert 'T01 IMAGE READY' in prep and 'PREPARATION T01 : image verifiee sha256:' in prep
    global_log=(OUT/refs['regression']).read_text(encoding='utf-8-sig')
    global_result=json.loads(re.search(r'^T01_RESULT (.+)$',global_log,re.M)[1])
    assert global_result['pass'] and global_result['tests']>0 and global_result['failures']==global_result['errors']==0
    assert global_result==receipt['global_result']
    assert sum(1 for line in global_log.splitlines() if '<testcase ' in line and 'PointsVente' in line)==receipt['counts']['unit_tests'], 'Tests B10 non découverts dans T01'
    cleanup=json.loads((OUT/refs['cleanup']).read_text(encoding='utf-8'))
    assert cleanup=={'observer_removed':True,'sessions_restored':True}
    if live:
        sys.path.insert(0,str(ROOT/'wp/outils/demo'))
        import b10
        identity=b10.guard()
        remote=b10.b09.b08.c25.b06.hashes(b10.FILES[:-1])
        assert remote=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in b10.FILES[:-1]}
        data=b10.wp('echo wp_json_encode(["ids"=>get_option(Imagine\\Site\\PointsVente::ACTIFS),"rows"=>Imagine\\Site\\PointsVente::lignes(),"config"=>Imagine\\Site\\PointsVente::configuration(),"pending"=>get_option(Imagine\\Site\\PointsVente::NETTOYAGE),"failure"=>get_option("imagine_b10_refus_suppression",null),"page"=>get_permalink((int)get_option("imagine_b10_page")),"temporary"=>file_exists(WP_CONTENT_DIR."/mu-plugins/b10-observer.php")||file_exists(WP_CONTENT_DIR."/imagine-demo-build/b10-runtime.php")||file_exists(WP_CONTENT_DIR."/imagine-demo-build/b10-seed.php")]);')
        assert data['ids']==recipe['fixture_ids'] and len(data['rows'])==30
        assert all(set(r)=={'nom','adresse','localite','postal'} for r in data['rows'])
        assert data['config']=={'mapping':json.loads((OUT/'mapping-exemple.json').read_text(encoding='utf-8')),'separateur':';','carte':'0'}
        assert data['page']==identity['url']+'/points-de-vente/' and data['temporary'] is False
        all_ids=b10.wp('echo wp_json_encode(get_posts(["post_type"=>Imagine\\Site\\PointsVente::TYPE,"post_status"=>"any","numberposts"=>-1,"fields"=>"ids","orderby"=>"ID","order"=>"ASC"]));')
        assert all_ids==sorted(data['ids']), 'Commerce B10 orphelin après reprise'
        assert data['pending']==[] and data['failure'] is None
        seed=json.loads((OUT/'page-navigation.json').read_text(encoding='utf-8'))
        assert b10.navigation()==seed['after']
        print('B10 LIVE PASS : 30 commerces fictifs, carte OFF, fichiers et navigation relus')
    print('B10 PASS :',checked,'empreintes ;',receipt['counts']['unit_tests'],'tests unitaires ;',receipt['counts']['unit_assertions'],'assertions ;',len(native_checks),'contrôles natifs ;',len(recipe['checks']),'contrôles navigateur')
    print('GLOBAL :',global_result['tests'],'tests ;',global_result['tools']['checks'],'contrôles outils ; paquets hors B10 :',global_result['packets']['failures'])


if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
