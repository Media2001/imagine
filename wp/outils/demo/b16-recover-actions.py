import sys
sys.dont_write_bytecode=True
import json
import b16 as o
import b13
baseline=json.loads((o.OUT/'native-corrections-profils-V2.json').read_text(encoding='utf-8'))['before']
r=o.wp('''global $wpdb;$ids=[9371,9372,9373,9374];foreach($ids as $id){$row=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=%d",$id),ARRAY_A);if(!$row || $row['hook']!=='wcs_report_update_cache'){throw new RuntimeException('Action étrangère');}$wpdb->delete($wpdb->prefix.'actionscheduler_logs',['action_id'=>$id]);$wpdb->delete($wpdb->prefix.'actionscheduler_actions',['action_id'=>$id]);}echo wp_json_encode(true);''')
after=b13.c29.state()
b13.save(o,'restauration-actions-corrections-V2',{'ids':[9371,9372,9373,9374],'only_hook':'wcs_report_update_cache','restored':after==baseline,'before':baseline,'after':after})
print('Restauration exacte état métier et ordonnanceur',after==baseline)
assert r and after==baseline
