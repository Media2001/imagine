"""C16 bounded read-only final status; exit 2 if qualification gates stay red."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c16

def run():
    c16.profils.guard('imagine-test-demo')
    p=c16.PROOF
    installation=json.loads((p/'installation.json').read_text(encoding='utf-8'))
    payload={}
    for name,digest in installation['sha256_readback'].items():
        source=c16.ROOT/('wp/outils/demo' if name in ['c09-seed.php','c16-reset.php'] else 'wp/plugins/imagine-site')/name
        target=('imagine-demo-build/' if name in ['c09-seed.php','c16-reset.php'] else 'plugins/imagine-site/')+name
        actual=c16.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.'+json.dumps('/'+target)+'));')
        assert actual==digest==hashlib.sha256(source.read_bytes()).hexdigest(), 'Payload changed: '+name
        payload[str(source.relative_to(c16.ROOT)).replace('\\','/')]=digest
    http=json.loads((p/'http-final.json').read_text(encoding='utf-8'))
    assert http['total']==len(http['checks']) and not http['failures'] and all(v is True for v in http['checks'].values())
    focused=json.loads((p/'unit-final.json').read_text(encoding='utf-8'))
    root=json.loads((p/'unit-root-final.json').read_text(encoding='utf-8'))
    assert focused['exit']==root['exit']==0 and focused['removed'] and root['removed']
    log=(p/'rejouer-t01.log').read_text(encoding='utf-8')
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',log,re.M)
    assert len(markers)==1
    canonical=json.loads(markers[0])
    preparation=(p/'preparer-image.log').read_text(encoding='utf-8')
    assert 'T01 IMAGE READY' in preparation and 'T01 IMAGE PACKAGE : imagine-site' in preparation
    raw=c16.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";',check=False)
    assert not raw['stderr']
    c09=json.loads(raw['stdout'])
    c16.save('c09-non-regression',c09)
    assert c09['total']==len(c09['checks'])
    rest=c16.wp('$o=[];foreach(["shop_order","shop_subscription"] as $type){foreach(wc_get_orders(["type"=>$type,"limit"=>-1,"status"=>"any","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"]) as $v){$o[]=$v->get_id();}}echo wp_json_encode(["objects"=>$o,"users"=>get_users(["fields"=>"ID","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"])]);')
    assert rest=={'objects':[],'users':[]}
    blocks=[]
    if not canonical['pass']: blocks.append('canonical_T01: CatalogueStatusTest / missing copied theme source; see rejouer-t01.log')
    if c09['failures']: blocks.extend('native_C09: '+k for k in c09['failures'])
    if blocks: assert not (p/'PRET').exists()
    result={'at':datetime.now(timezone.utc).isoformat(),'status':'BLOQUE_QUALIFICATION_GLOBALE' if blocks else 'GATES_TECHNIQUES_VERTS',
        'PRET_present':(p/'PRET').exists(),'payload_sha256_readback':payload,'c16_unit_exit':focused['exit'],
        'root_unit_exit':root['exit'],'http_checks':http['total'],'http_failures':http['failures'],
        'preparation_verified':True,'canonical_T01':canonical,'C09_checks':c09['total'],'C09_failures':c09['failures'],
        'native_cleanup_readback':rest,'blockers':blocks}
    c16.save('final',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 2 if blocks else 0
if __name__=='__main__':sys.exit(run())
