"""Twenty distinct native articles under one owned, ungranted issue."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
s=importlib.util.spec_from_file_location('w',Path(__file__).with_name('b04-work.py'))
w=importlib.util.module_from_spec(s);s.loader.exec_module(w);w.guard()
r=w.wp(r'''
$f=get_option('imagine_b04_fixture',[]);$id=(int)($f['witness']??0);
$posts=$id?get_posts(['post_type'=>'post','post_status'=>'publish','numberposts'=>-1,'meta_key'=>'imagine_numero_id','meta_value'=>$id,'orderby'=>['menu_order'=>'ASC','ID'=>'ASC']]):[];
$ids=wp_list_pluck($posts,'ID');$checks=['numero_temoin_existe'=>$id>0&&get_post_type($id)==='imagine_numero',
'vingt_articles_distincts'=>count($ids)===20&&count(array_unique($ids))===20,
'exactement_manifest'=>$ids===($f['articles']??[]),
'proprietaires_exacts'=>count(array_filter($posts,static fn($p)=>get_post_meta($p->ID,'_imagine_b04_fixture',true)==='article-v1'))===20];
echo wp_json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>array_keys(array_filter($checks,static fn($v)=>$v!==true)),'ids'=>$ids,'issue'=>$id]);
''')
(w.PROOF/('witness-'+sys.argv[1]+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(r))
if r['failures']:raise SystemExit(1)
