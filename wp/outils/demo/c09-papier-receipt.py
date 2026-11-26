"""Read-only completion after WCS report-cache invalidation tripped the narrow guard."""
import importlib
import json
from datetime import datetime, timezone
m = importlib.import_module('c09-papier')
m.c18.c17.profils.guard('imagine-test-demo')
before = json.loads((m.PROOF / 'papier-before-V2.json').read_text(encoding='utf-8'))
red = json.loads((m.PROOF / 'papier-native-before-V2.json').read_text(encoding='utf-8'))
observed = json.loads((m.PROOF / 'papier-after-diagnostic-V2.json').read_text(encoding='utf-8'))
# Recompute the actual historical aggregate from current rows by reversing ONLY
# the three observed scheduler deltas. It must equal the pre-write stored digest.
# No database row or historical receipt is written by this probe.
probe = m.c18.wp(r'''global $wpdb;$out=['reverted_fingerprints'=>[]];
foreach(['actionscheduler_actions','actionscheduler_logs'] as $suffix){
$rows=$wpdb->get_results("SELECT * FROM `{$wpdb->prefix}$suffix`",ARRAY_A);$hashes=[];
foreach($rows as $r){
if($suffix==='actionscheduler_actions'){
if(in_array((int)$r['action_id'],[8793,8794],true))continue;
if((int)$r['action_id']===8789)$r['status']='pending';
}elseif((int)$r['log_id']>16858)continue;
$hashes[]=hash('sha256',serialize($r));}
sort($hashes);$out['reverted_fingerprints'][$suffix]=['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))];}
$out['affected_actions']=$wpdb->get_results("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id IN (8789,8793,8794) ORDER BY action_id",ARRAY_A);
$out['new_logs']=$wpdb->get_results("SELECT * FROM {$wpdb->prefix}actionscheduler_logs WHERE log_id>16858 ORDER BY log_id",ARRAY_A);
echo wp_json_encode($out);''')
for name, fingerprint in probe['reverted_fingerprints'].items():
    assert fingerprint == before['native_fingerprints'][name], name
assert len(probe['affected_actions']) == 3 and len(probe['new_logs']) == 3
assert probe['affected_actions'][0]['hook'] == probe['affected_actions'][2]['hook'] == 'wcs_report_update_cache'
assert probe['affected_actions'][0]['args'] == probe['affected_actions'][2]['args']
assert probe['affected_actions'][1]['hook'] == 'woocommerce_scheduled_subscription_payment'
assert probe['affected_actions'][1]['args'] == '{"subscription_id":101}'
after = m.c18.state()
assert after == observed['state']
target = m.snapshot()
assert target == observed['target']
native = m.native()
assert native['exit'] == 0 and native['total'] == 382 and not native['failures']
receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'status': 'VERIFIED',
 'authorization': 'A-FAIRE-2.md consigne 1 du 2026-11-26 01:30', 'global_seed_replayed': False,
 'source_sha256': {name: m.digest(m.ROOT/name) for name in ['wp/outils/demo/c09-papier.php','wp/outils/demo/c09-calendar.php','wp/outils/demo/c09-papier.py']},
 'before': before, 'after': after, 'target_before': {'native_profile': red['native']['proof']['A-PAPIER']}, 'target_after': target,
 'native_before': {'exit':red['exit'], **red['native']}, 'native_after':native,
 'scheduler_delta_verified_against_before_sha256': True, 'scheduler_delta_proof': probe,
 'execution_note': 'Target replay succeeded once at 01:13:28 UTC. Initial wrapper then rejected WCS native report-cache invalidation (8789 canceled, 8794 created). No second replay. Read-only aggregate inversion exactly matches both stored pre-write scheduler fingerprints; native/commercial snapshots and all old receipts preserved.'}
m.validate_receipt(receipt)
m.save_new(m.RECEIPT,receipt)
m.readback()
