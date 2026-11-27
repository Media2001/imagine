"""B10, site unique fictif ; transport existant, lecture après chaque écriture."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
from pathlib import Path
import b09
ROOT=b09.ROOT
OUT=ROOT/'production/B-10'
wp,php=b09.wp,b09.php
guard=b09.b08.c25.b06.guard
upload=b09.b08.c25.b06.profils.b00.upload
state=b09.b08.c25.b06.state
BLOCK="// B10 — points de vente locaux, sans fournisseur de carte.\nrequire_once __DIR__ . '/PointsVenteRegles.php';\nrequire_once __DIR__ . '/PointsVente.php';\nPointsVente::register();\n\n"
FILES=['plugins/imagine-site/PointsVenteRegles.php','plugins/imagine-site/PointsVente.php','plugins/imagine-site/imagine-site.php']


def save(label,data):
    p=OUT/(label+'.json')
    assert not p.exists(),p
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def deploy(label):
    identity=guard();before=state()
    old=wp('$r=[];foreach('+php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$r[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($r);')
    local={n:(ROOT/'wp'/n).read_text(encoding='utf-8') for n in FILES}
    assert old[FILES[-1]] in [local[FILES[-1]],local[FILES[-1]].replace(BLOCK,'')], 'Bootstrap divergent'
    save(label+'-avant',{'identity':identity,'files':old})
    for n in FILES: upload(n,(ROOT/'wp'/n).read_bytes())
    actual=b09.b08.c25.b06.hashes(FILES)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert before==state()
    save(label,{'readback':actual,'business_preserved':True})
    print('B10 code relu :',len(actual),'fichiers')


def runtime(label):
    guard();name='imagine-demo-build/b10-runtime.php'
    before=wp('echo wp_json_encode([get_option("imagine_vente_actifs",null),get_posts(["post_type"=>"imagine_vente","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"])]);')
    assert before==[None,[]], 'Recette initiale seulement, liste déjà présente'
    assert wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+name+'"));') is False
    result={}
    try:
        upload(name,(ROOT/'wp/tests/demo/b10-runtime.php').read_bytes())
        raw=b09.b08.c25.b06.profils.b00.wp('eval','require WP_CONTENT_DIR."/'+name+'";',check=False)
        result=raw
    finally:
        b09.remove_remote([name])
        wp('foreach(get_posts(["post_type"=>"imagine_vente","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]) as $id){wp_delete_post($id,true);}delete_option("imagine_vente_actifs");echo wp_json_encode(true);')
        restored=wp('echo wp_json_encode([get_option("imagine_vente_actifs",null),get_posts(["post_type"=>"imagine_vente","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"])]);')==before
        save(label,{**result,'restored':restored})
    print(json.dumps(result,ensure_ascii=False))
    assert restored and result['code']==0

if __name__=='__main__': globals()[sys.argv[1]](sys.argv[2])
