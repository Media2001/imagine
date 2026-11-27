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
    receipt=json.loads((OUT/'reception.json').read_text(encoding='utf-8'))
    checked=0
    for relative,expected in receipt['sha256'].items():
        path=ROOT/relative
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected,relative
        checked+=1
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(receipt['bootstrap_block'])==1,'Raccord B10 absent ou dupliqué'
    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    assert receipt['readme_section'] in readme,'Section B10 du README divergente'
    recipe=json.loads((OUT/'recette-finale.json').read_text(encoding='utf-8'))
    assert recipe['checks'] and all(v is True for v in recipe['checks'].values())
    assert len(recipe['fixture_ids'])==len(set(recipe['fixture_ids']))==30
    assert set(recipe['map_observations'])=={'0','1'}
    for value,observation in recipe['map_observations'].items():
        assert observation['placeholder']==int(value) and observation['requests'] and observation['third_party']==[]
    native=json.loads((OUT/'natif-final.json').read_text(encoding='utf-8'))
    assert native['code']==0 and native['stderr']=='' and native['restored'] and native['transaction_rollback']
    native_checks=json.loads(native['stdout'])['checks']
    assert native_checks and all(v is True for v in native_checks.values())
    unit=(OUT/'unitaire-final.log').read_text(encoding='utf-8')
    assert 'OK (5 tests, 26 assertions)' in unit
    prep=(OUT/'preparation-image.log').read_text(encoding='utf-8-sig')
    assert 'T01 IMAGE READY' in prep and 'PREPARATION T01 : image verifiee sha256:' in prep
    global_log=(OUT/'regression-globale.log').read_text(encoding='utf-8-sig')
    global_result=json.loads(re.search(r'^T01_RESULT (.+)$',global_log,re.M)[1])
    assert global_result['pass'] and global_result['tests']>0 and global_result['failures']==global_result['errors']==0
    cleanup=json.loads((OUT/'recette-finale-nettoyage.json').read_text(encoding='utf-8'))
    assert cleanup=={'observer_removed':True,'sessions_restored':True}
    if live:
        sys.path.insert(0,str(ROOT/'wp/outils/demo'))
        import b10
        identity=b10.guard()
        remote=b10.b09.b08.c25.b06.hashes(b10.FILES[:-1])
        assert remote=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in b10.FILES[:-1]}
        data=b10.wp('echo wp_json_encode(["ids"=>get_option(Imagine\\Site\\PointsVente::ACTIFS),"rows"=>Imagine\\Site\\PointsVente::lignes(),"config"=>Imagine\\Site\\PointsVente::configuration(),"page"=>get_permalink((int)get_option("imagine_b10_page")),"temporary"=>file_exists(WP_CONTENT_DIR."/mu-plugins/b10-observer.php")||file_exists(WP_CONTENT_DIR."/imagine-demo-build/b10-runtime.php")||file_exists(WP_CONTENT_DIR."/imagine-demo-build/b10-seed.php")]);')
        assert data['ids']==recipe['fixture_ids'] and len(data['rows'])==30
        assert all(set(r)=={'nom','adresse','localite','postal'} for r in data['rows'])
        assert data['config']=={'mapping':json.loads((OUT/'mapping-exemple.json').read_text(encoding='utf-8')),'separateur':';','carte':'0'}
        assert data['page']==identity['url']+'/points-de-vente/' and data['temporary'] is False
        seed=json.loads((OUT/'page-navigation.json').read_text(encoding='utf-8'))
        assert b10.navigation()==seed['after']
        print('B10 LIVE PASS : 30 commerces fictifs, carte OFF, fichiers et navigation relus')
    print('B10 PASS :',checked,'empreintes ; 5 tests unitaires ;',len(native_checks),'contrôles natifs ;',len(recipe['checks']),'contrôles navigateur')
    print('GLOBAL :',global_result['tests'],'tests ;',global_result['tools']['checks'],'contrôles outils ; paquets hors B10 :',global_result['packets']['failures'])


if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
