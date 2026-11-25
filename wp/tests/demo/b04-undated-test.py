"""B01 native release-date publication guard is preserved; exact owned cleanup."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
s=importlib.util.spec_from_file_location('w',Path(__file__).with_name('b04-work.py'));w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard();phase=sys.argv[1]
id=w.wp(r'''
if(get_page_by_path('b04-numero-sans-date',OBJECT,'imagine_numero')){throw new RuntimeException('B04 slug collision.');}
$id=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'publish','post_title'=>'FICTIF B04 — numéro temporaire sans date','post_name'=>'b04-numero-sans-date','meta_input'=>['_imagine_b04_fixture'=>'undated-v1']],true);
if(is_wp_error($id)){throw new RuntimeException('B04 witness creation failed.');}echo wp_json_encode($id);
''')
try:
    native=w.wp(r'''
$old=$GLOBALS['wp_the_query'];$q=new WP_Query();$GLOBALS['wp_the_query']=$q;
$q->query(['post_type'=>'imagine_numero','post_status'=>'publish','posts_per_page'=>-1]);
$ids=wp_list_pluck($q->posts,'ID');$GLOBALS['wp_the_query']=$old;echo wp_json_encode($ids);
''')
    checks={'native_B01_guard_keeps_undated_issue_draft':w.wp('echo wp_json_encode(get_post_status('+str(id)+'));')=='draft', 'draft_not_in_public_archive':id not in native}
finally:
    removed=w.wp('$id='+str(id)+';if(get_post_meta($id,"_imagine_b04_fixture",true)!=="undated-v1"){throw new RuntimeException("B04 ownership refused");}wp_delete_post($id,true);echo wp_json_encode(get_post($id)===null&&get_post_meta($id)===[]);')
    checks['exact_own_object_removed']=removed
result={'scope':'imagine-test-demo','total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],'native_ids':native,'temporary_owned_id':id}
(w.PROOF/('undated-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if result['failures']:raise SystemExit(1)
