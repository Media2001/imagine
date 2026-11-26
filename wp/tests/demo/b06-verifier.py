"""Vérifie le paquet B06 final et relit la cible exacte, sans réécrire les preuves."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util, hashlib, json, re
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'outils/demo'))
import b06


def verify(label='recette-finale-V2'):
    p = b06.PROOF/(label+'.json')
    final=json.loads(p.read_text(encoding='utf-8'))
    assert final['scope']=='imagine-test-demo' and final['result']=='VERIFIED' and final['failures']==[]
    for name,expected in final['sources'].items():
        path=b06.ROOT/name
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected, 'Source B06 divergente : '+name
    bootstrap=(b06.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(b06.BLOCK)==1 and final['bootstrap_contract']
    total=0
    for name in final['normal_receipts']:
        r=json.loads((b06.PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert not r['failures'] and not r.get('error') and not r.get('exit') and not r.get('stderr')
        assert len(r['checks'])==r['total'] and all(v is True for v in r['checks'].values())
        total+=r['total']
    assert total==final['total'] and total>100
    assert len(final['mutation_receipts'])==final['mutation_count']==11
    for item in final['mutation_receipts']:
        r=json.loads((b06.PROOF/(item['receipt']+'.json')).read_text(encoding='utf-8'))
        assert r['exit']==1 and item['required_failure'] in r['failures'] and r['state_preserved'] and not r['stderr']
    image=json.loads((b06.PROOF/'image-final-V2.json').read_text(encoding='utf-8'))
    assert image['exit']==0 and 'T01 IMAGE READY' in image['stdout'] and 'image verifiee sha256:' in image['stdout']
    regression=json.loads((b06.PROOF/'regression-V2.json').read_text(encoding='utf-8'))
    matches=re.findall(r'^T01_RESULT (.+)$',regression['stdout'],re.M)
    assert regression['exit']==0 and len(matches)==1
    data=json.loads(matches[0]);assert data['pass'] and data['tests']>1000 and data['failures']==data['errors']==data['skipped']==0
    assert data['tools']['failures']==0
    assert (b06.PROOF/'A-VOIR.md').is_file() and (b06.PROOF/'standard-V2.md').is_file()
    b06.guard()
    live=b06.hashes(b06.NAMES)
    for n in b06.NAMES[:-1]:
        assert live[n]==hashlib.sha256((b06.ROOT/'wp'/n).read_bytes()).hexdigest()
    shared=b06.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php"));')
    assert shared.count(b06.BLOCK)==1, 'Bootstrap B06 absent de la cible'
    assert b06.hashes(list(final['closed_sources']))==final['closed_sources']
    own=b06.wp('''$ids=Imagine\\Site\\Cooperateurs::ids();$f=get_option('imagine_c09_fixture');$pages=[];foreach($ids as $id){$p=get_post($id);$pages[]=['id'=>$id,'content'=>$p->post_content,'parent'=>$p->post_parent];}echo wp_json_encode(['pages'=>$pages,'state'=>get_user_meta($f['users']['P-COOP'],'imagine_cooperateur',true)]);''')
    assert len(own['pages'])==5 and all(p['content']=='' for p in own['pages'])
    assert own['state']['cooperateur'] is True and own['state']['source']=='administration'
    result={'result':'VERIFIED','B06_checks':total,'mutations':11,'regression_tests':data['tests'],
            'regression_assertions':data['assertions'],'tool_checks':data['tools']['checks'],'pages':len(own['pages']),
            'P_COOP_retained':True,'closure':'Claude/Ced uniquement'}
    print(json.dumps(result,ensure_ascii=False))
    return result

if __name__=='__main__': verify(sys.argv[1] if len(sys.argv)>1 else 'recette-finale-V2')
