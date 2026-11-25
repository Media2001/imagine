"""Audit lecture seule des effets C13 des premiers diagnostics C11."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c14
c14.c10.guard()
created = datetime.fromtimestamp((ROOT / 'wp/tests/demo/c14-corrections-fixture.php').stat().st_ctime, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
data = c14.wp(r'''global $wpdb;$out=[];
foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_envoi_releve_%' ORDER BY option_id",ARRAY_A) as $row){
$v=maybe_unserialize($row['option_value']);if(in_array((string)($v['donnees']['id']??''),['77','79'],true)){
$out[]=['option'=>$row['option_name'],'observe_utc'=>$v['observe_utc'],'origine'=>$v['donnees']['origine']??null];}}
echo wp_json_encode($out);''')
record = {'test_created_utc': created, 'observations_after_test_creation': [r for r in data if r['observe_utc'] >= created]}
(Path(__file__).parent / 'incident-observations-c13.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False, indent=2))
