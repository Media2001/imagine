import sys
sys.dont_write_bytecode=True
import json
import b16 as o
import b13
baseline=json.loads((o.OUT/'native-corrections-profils-V2.json').read_text(encoding='utf-8'))['before']
r=o.wp('''global $wpdb;$ids=[9111,9112,9113,9355];foreach($ids as $id){$row=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=%d",$id),ARRAY_A);if(!$row||$row['hook']!=='wcs_report_update_cache'||$row['status']!=='canceled'){throw new RuntimeException('précondition');}$wpdb->update($wpdb->prefix.'actionscheduler_actions',['status'=>'pending'],['action_id'=>$id]);}$logIds=[17843,17845,17847,17849];foreach($logIds as $log){$row=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}actionscheduler_logs WHERE log_id=%d",$log),ARRAY_A);if(!$row||!in_array((int)$row['action_id'],$ids,true)||$row['message']!=='action canceled'){throw new RuntimeException('précondition journal');}$wpdb->delete($wpdb->prefix.'actionscheduler_logs',['log_id'=>$log]);}echo wp_json_encode(true);''')
after=b13.c29.state()
b13.save(o,'recovery-actions-final-V2',{'restored':baseline==after,'before':baseline,'after':after,'exact_actions':[9111,9112,9113,9355],'exact_logs':[17843,17845,17847,17849]})
print('baseline exacte rétablie',baseline==after)
assert r and baseline==after
