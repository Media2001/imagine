"""Forensic check: reproduce frozen digest by ONLY two native activity timestamps.
No DB row is restored or changed. Original timestamps are bounded by WP's existing
native session login times; every other metadata byte/id must hash exactly.
"""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
s=importlib.util.spec_from_file_location('w',Path(__file__).with_name('b04-work.py'));w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard()
before=json.loads((w.PROOF/'preservation-resume-before.json').read_text(encoding='utf-8'))
code=r'''
global $wpdb;
$rows=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key <> 'session_tokens' ORDER BY umeta_id",ARRAY_A);
$expected=EXPECTED;$candidates=[];$indices=[];$current=[];
foreach([9,28] as $uid){
$sessions=get_user_meta($uid,'session_tokens',true);
$logins=array_values(array_filter(array_column(is_array($sessions)?$sessions:[],'login'),static fn($t)=>$t>=strtotime('2026-11-25 19:28:00 UTC')&&$t<=strtotime('2026-11-25 19:35:01 UTC')));
$candidates[$uid]=[];foreach($logins as $login){for($offset=0;$offset<=10;$offset++){$candidates[$uid][]=(string)($login+$offset);}}
foreach($rows as $i=>$row){if((int)$row['user_id']===$uid && $row['meta_key']==='wc_last_active'){$indices[$uid]=$i;$current[$uid]=$row['meta_value'];}}
}
$match=null;$tries=0;
foreach($candidates[9] as $a){foreach($candidates[28] as $b){$tries++;$copy=$rows;$copy[$indices[9]]['meta_value']=$a;$copy[$indices[28]]['meta_value']=$b;
if(hash('sha256',serialize($copy))===$expected){$match=['9'=>['before'=>$a,'after'=>$current[9]],'28'=>['before'=>$b,'after'=>$current[28]]];break 2;}}}
echo wp_json_encode(['scope'=>'imagine-test-demo','exact_frozen_digest_reproduced'=>$match!==null,'only_changed_key'=>'wc_last_active','only_changed_users'=>$match,'attempts'=>$tries,'no_database_write'=>true]);
'''.replace('EXPECTED',json.dumps(before['rights_usermeta']))
result=w.wp(code)
(w.PROOF/'native-activity-reconciliation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if not result['exact_frozen_digest_reproduced']:raise SystemExit(1)
