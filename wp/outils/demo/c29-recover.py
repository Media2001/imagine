"""Restore only the exact native WCS shutdown delta witnessed in C29 test setup."""
import sys
sys.dont_write_bytecode=True
import json
import b11
import c19
import c29

def run():
    b11.guard()
    receipt=json.loads((c29.OUT/'native-special-V2.json').read_text(encoding='utf-8'))
    expected=receipt['strict_before']
    current=c19.state()
    assert {k:v for k,v in current.items() if k!='native_fingerprints'}=={k:v for k,v in expected.items() if k!='native_fingerprints'}
    code='''global $wpdb;$expected='''+b11.php({k:expected['native_fingerprints'][k] for k in ['actionscheduler_actions','actionscheduler_logs']})+''';$wpdb->query('START TRANSACTION');try{
$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';
$r=$wpdb->get_row("SELECT * FROM $a WHERE action_id=9356",ARRAY_A);if(!$r||$r['hook']!=='wcs_report_update_cache'||$r['status']!=='pending'||$r['scheduled_date_gmt']!=='2026-11-27 14:50:33'){throw new RuntimeException('Foreign action');}
$wpdb->query("DELETE FROM $a WHERE action_id=9356");$wpdb->query("UPDATE $a SET status='pending' WHERE action_id=9355 AND hook='wcs_report_update_cache' AND status='canceled'");
$wpdb->query("DELETE FROM $l WHERE (log_id=17821 AND action_id=9355 AND message='action canceled') OR (log_id=17822 AND action_id=9356 AND message='action created')");
foreach($expected as $suffix=>$want){$rows=$wpdb->get_results('SELECT * FROM '.$wpdb->prefix.$suffix,ARRAY_A);$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$rows);sort($hashes);if(['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))]!==$want){throw new RuntimeException('Exact prior checksum not restored');}}
$wpdb->query('COMMIT');echo wp_json_encode(['exact_prior_actions_and_logs'=>true]);
}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}'''
    result=b11.wp(code)
    restored=c19.state()==expected
    c29.save('recovery-setup-shutdown-V2',{'result':result,'strict_restoration':restored,'removed_action':9356,'removed_logs':[17821,17822],'restored_action':9355})
    print(result,restored);assert restored
if __name__=='__main__':run()
