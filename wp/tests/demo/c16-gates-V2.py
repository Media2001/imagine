"""Fresh C16 gates: no historical C09 exception, no successor bootstrap overwrite."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c16


def run():
    c16.profils.guard('imagine-test-demo')
    p=c16.PROOF
    load=lambda name:json.loads((p/name).read_text(encoding='utf-8'))
    installation=load('installation-V2.json')
    payload={}
    for name,digest in installation['sha256_readback'].items():
        demo=name=='c16-reset.php'
        source=c16.ROOT/('wp/outils/demo' if demo else 'wp/plugins/imagine-site')/name
        target=('imagine-demo-build/' if demo else 'plugins/imagine-site/')+name
        actual=c16.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.'+json.dumps('/'+target)+'));')
        assert actual==digest==hashlib.sha256(source.read_bytes()).hexdigest(), 'C16 payload drift: '+name
        payload[name]=actual
    shared=c16.shared_contract() # Current loaded registrations/classes, not old cross-lot seals.
    counts={}
    for label in ['unit-focused-V2','unit-root-V2']:
        unit=load(label+'.json')
        assert unit['exit']==0 and unit['removed'] and unit['network']=='none' and not unit['stderr']
        tree=ET.fromstring(unit['stdout'].split('C16_JUNIT',1)[1].strip())
        assert not list(tree.iter('failure'))+list(tree.iter('error'))+list(tree.iter('skipped'))
        cases=list(tree.iter('testcase'))
        counts[label]={'tests':len(cases),'assertions':sum(int(t.get('assertions',0)) for t in cases)}
    http={}
    for label in ['http-base-V2','http-corrections-V2']:
        receipt=load(label+'.json')
        assert receipt['total']==len(receipt['checks']) and not receipt['failures'] and all(v is True for v in receipt['checks'].values())
        http[label]={'total':receipt['total'],'failures':receipt['failures']}
    corrections=load('http-corrections-V2.json')
    race=corrections['evidence']['concurrence']
    assert len(race['responses'])==2 and len(race['before_lock'])==2
    assert race['responses'][0]['id']==race['responses'][1]['id']
    assert len(race['native_reread']['shop_order'])==len(race['native_reread']['shop_subscription'])==1
    log=(p/'rejouer-t01-V2.log').read_text(encoding='utf-8')
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',log,re.M)
    assert len(markers)==1
    canonical=json.loads(markers[0])
    assert canonical['pass'] and canonical['errors']==canonical['failures']==canonical['skipped']==0
    assert log.rstrip().endswith('PASS') and 'NETTOYAGE EN ECHEC' not in log
    preparation=(p/'preparer-image-V2.log').read_text(encoding='utf-8')
    assert 'T01 IMAGE READY' in preparation and 'T01 IMAGE PACKAGE : imagine-site' in preparation
    execution=load('execution-V2.json')
    assert all(step['exit']==0 for step in execution['steps']) and all(any(s['name']==name for s in execution['steps']) for name in ['preparer-image-V2','rejouer-t01-V2','unit-focused-V2','unit-root-V2','http-base-V2','http-corrections-V2'])
    raw=c16.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";',check=False)
    assert raw['code']==0 and not raw['stderr']
    c09=json.loads(raw['stdout']);c16.save('c09-final-V2',c09)
    assert c09['total']==len(c09['checks'])==382 and not c09['failures'] and all(v is True for v in c09['checks'].values())
    spec=importlib.util.spec_from_file_location('c16_corrections_recipe',Path(__file__).with_name('c16-corrections-http.py'))
    recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)
    native=c16.wp(recipe.STATE)
    assert native==corrections['evidence']['C09_before']==corrections['evidence']['C09_after']
    assert native['id']==101 and native['status']=='active' and native['action']['status']=='pending' and native['action']['args']=={'subscription_id':101}
    rest=c16.wp('$o=[];foreach(["shop_order","shop_subscription"] as $type){foreach(wc_get_orders(["type"=>$type,"limit"=>-1,"status"=>"any","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"]) as $v){$o[]=$v->get_id();}}echo wp_json_encode(["objects"=>$o,"users"=>get_users(["fields"=>"ID","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"]),"probe_absent"=>!file_exists(WP_CONTENT_DIR."/mu-plugins/imagine-c16-recette-v2.php"),"probe_state_absent"=>get_option("imagine_c16_recette_v2",null)===null]);')
    assert rest=={'objects':[],'users':[],'probe_absent':True,'probe_state_absent':True}
    evidence=['installation-V2.json','execution-V2.json','http-base-V2.json','http-corrections-V2.json','unit-focused-V2.json','unit-root-V2.json','preparer-image-V2.log','rejouer-t01-V2.log','c09-final-V2.json','red-concurrence-V2.json','red-adresse-apostrophes-V2.json']
    result={'at':datetime.now(timezone.utc).isoformat(),'status':'GATES_TECHNIQUES_VERTS','scope':'imagine-test-demo','C16_payload_sha256_readback':payload,'shared_current_contract':shared,'unit':counts,'http':http,'canonical_T01':canonical,'C09':{'checks':c09['total'],'failures':c09['failures'],'native_exit':raw['code'],'A_PAPIER':native},'strict_global_exit':0,'historical_C09_exception':False,'native_cleanup_readback':rest,'blockers':[],'evidence_sha256':{name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in evidence}}
    c16.save('final-V2',result)
    print(json.dumps({'status':result['status'],'unit':counts,'http':http,'canonical':canonical,'C09':c09['total'],'action':native['action'],'strict_global_exit':0},ensure_ascii=False))
    return 0

if __name__=='__main__':sys.exit(run())
