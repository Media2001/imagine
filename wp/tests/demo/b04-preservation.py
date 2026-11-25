"""Semantic preservation: exact existing editorial/rights rows, not volatile logs."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('b04_work',HERE/'b04-work.py')
w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard()
phase=sys.argv[1]
baseline=w.PROOF/'preservation-resume-before.json'
ids=None if phase=='before' else json.loads(baseline.read_text(encoding='utf-8'))['post_ids']
code=r'''
global $wpdb;
$ids=IDS;
if($ids===null){$ids=array_map('intval',$wpdb->get_col("SELECT ID FROM {$wpdb->posts} ORDER BY ID"));}
$out=['post_ids'=>$ids,'posts'=>[],'postmeta'=>[],'relations'=>[]];
foreach($ids as $id){
$out['posts'][(string)$id]=hash('sha256',serialize($wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",$id),ARRAY_A)));
$out['postmeta'][(string)$id]=hash('sha256',serialize($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id",$id),ARRAY_A)));
$out['relations'][(string)$id]=hash('sha256',serialize($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->term_relationships} WHERE object_id=%d ORDER BY term_taxonomy_id",$id),ARRAY_A)));}
$out['users']=hash('sha256',serialize($wpdb->get_results("SELECT * FROM {$wpdb->users} ORDER BY ID",ARRAY_A)));
$out['rights_usermeta']=hash('sha256',serialize($wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key <> 'session_tokens' ORDER BY umeta_id",ARRAY_A)));
$out['fixture_options']=[];
foreach(['imagine_demo_manifest','imagine_c09_fixture','imagine_c14_fixture','imagine_c12_fixture','imagine_c15_fixture','imagine_acces_reglages','imagine_acces_plans','imagine_decouverte_reglages','imagine_achat_remboursement'] as $key){$out['fixture_options'][$key]=hash('sha256',serialize(get_option($key,null)));}
$out['plugin_files']=[];$root=WP_CONTENT_DIR.'/plugins/imagine-site/';
foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS)) as $f){if($f->isFile()){$out['plugin_files'][substr($f->getPathname(),strlen($root))]=hash_file('sha256',$f->getPathname());}}ksort($out['plugin_files']);
echo wp_json_encode($out);
'''.replace('IDS','null' if ids is None else json.dumps(ids))
state=w.wp(code)
if phase=='before':
    assert not baseline.exists(), 'Baseline immutable'
    result=state
else:
    before=json.loads(baseline.read_text(encoding='utf-8'))
    checks={k:before[k]==state[k] for k in before}
    extras=w.wp('global $wpdb;echo wp_json_encode(array_map("intval",$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE ID NOT IN ('+','.join(map(str,ids))+') ORDER BY ID")));')
    product=w.wp('echo wp_json_encode((int)get_option("imagine_b04_fixture")["product"]);')
    checks['only_new_persistent_post_is_owned_product']=extras==[product]
    result={'checks':checks,'failures':[k for k,v in checks.items() if not v], 'known_owned_new_post_ids':extras, 'state':state}
(w.PROOF/('preservation-resume-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'phase':phase,'existing_posts':len(state['post_ids']),'failures':result.get('failures',[])}))
if result.get('failures'):raise SystemExit(1)
