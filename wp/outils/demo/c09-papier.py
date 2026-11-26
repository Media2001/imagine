"""C09 A-PAPIER: targeted calendar replay, immutable receipt, read-only readback."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
import c18

ROOT = c18.ROOT
PROOF = ROOT / 'production/C-09'
RECEIPT = PROOF / 'papier-restauration-V2.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_new(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)


def native():
    result = c18.c17.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";', check=False)
    assert not result['stderr']
    return {'exit': result['code'], **json.loads(result['stdout'])}


def snapshot():
    return c18.wp(r'''global $wpdb;$f=get_option('imagine_c09_fixture');$id=(int)$f['subscriptions']['A-PAPIER'];$s=wcs_get_subscription($id);
if(!$s||$s->get_meta('_imagine_c09_fixture')!=='A-PAPIER')throw new RuntimeException('Foreign fixture');
$actionIds=$wpdb->get_col($wpdb->prepare("SELECT action_id FROM {$wpdb->prefix}actionscheduler_actions WHERE args=%s",wp_json_encode(['subscription_id'=>$id])));
$ids=$actionIds?implode(',',array_map('intval',$actionIds)):'0';$out=['id'=>$id,'status'=>$s->get_status(),'manual'=>$s->is_manual(),'gateway'=>$s->get_payment_method(),'transaction_id'=>$s->get_transaction_id(),'next_payment'=>$s->get_date('next_payment'),'next_payment_timestamp'=>$s->get_time('next_payment'),'scheduled'=>as_next_scheduled_action('woocommerce_scheduled_subscription_payment',['subscription_id'=>$id]),'actions'=>[],'unrelated'=>[]];
foreach($actionIds as $aid){$out['actions'][]=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=%d",$aid),ARRAY_A);}
foreach(['users','usermeta','posts','postmeta','actionscheduler_actions','actionscheduler_logs','woocommerce_order_items','woocommerce_order_itemmeta','wc_orders','wc_order_addresses','wc_orders_meta','wc_order_operational_data'] as $suffix){
$t=$wpdb->prefix.$suffix;if($wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($t)))!==$t)continue;
$where=match($suffix){'posts'=>' WHERE ID!='.$id,'postmeta'=>' WHERE post_id!='.$id,'wc_orders','wc_order_operational_data'=>' WHERE id!='.$id,'wc_orders_meta','wc_order_addresses'=>' WHERE order_id!='.$id,'actionscheduler_actions'=>' WHERE action_id NOT IN ('.$ids.')','actionscheduler_logs'=>' WHERE action_id NOT IN ('.$ids.')',default=>''};
$rows=$wpdb->get_results("SELECT * FROM `$t`".$where,ARRAY_A);$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$rows);sort($hashes);$out['unrelated'][$suffix]=['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))];}
$out['historical_action8103']=$wpdb->get_row("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=8103",ARRAY_A);
$out['historical_logs8103']=$wpdb->get_results("SELECT * FROM {$wpdb->prefix}actionscheduler_logs WHERE action_id=8103 ORDER BY log_id",ARRAY_A);
echo wp_json_encode($out);''')


def state_contract(before, after, subscription_id):
    """Only the target subscription and scheduler table fingerprints may differ."""
    import copy
    b, a = copy.deepcopy(before), copy.deepcopy(after)
    b['commandes'].pop(str(subscription_id))
    a['commandes'].pop(str(subscription_id))
    for key in ('posts', 'postmeta', 'wc_orders', 'wc_orders_meta', 'wc_order_addresses', 'wc_order_operational_data', 'actionscheduler_actions', 'actionscheduler_logs'):
        b['native_fingerprints'].pop(key, None)
        a['native_fingerprints'].pop(key, None)
    assert b == a, 'Unexpected non-target state delta'


def validate_receipt(receipt):
    assert receipt['scope'] == 'imagine-test-demo' and receipt['status'] == 'VERIFIED'
    assert receipt['global_seed_replayed'] is False
    assert receipt['native_after']['exit'] == 0 and receipt['native_after']['total'] == 382
    assert len(receipt['native_after']['checks']) == 382 and all(receipt['native_after']['checks'].values())
    assert receipt['native_after']['failures'] == []
    a, b = receipt['target_after'], receipt['target_before']
    assert a['status'] == 'active' and a['manual'] and a['gateway'] == a['transaction_id'] == ''
    assert a['scheduled'] == a['next_payment_timestamp'] and a['scheduled'] is not False
    assert a['unrelated'] == b['unrelated']
    assert a['historical_action8103'] == b['historical_action8103']
    assert a['historical_logs8103'] == b['historical_logs8103']
    state_contract(receipt['before'], receipt['after'], a['id'])
    for name, value in receipt['source_sha256'].items():
        assert digest(ROOT / name) == value, 'Restoration source drift: ' + name


def baseline_contract(baseline, current, receipt):
    """Bridge historical evidence without changing it or accepting arbitrary drift."""
    validate_receipt(receipt)
    old, new = receipt['before'], receipt['after']
    if 'native_fingerprints' not in baseline:
        old = {k: v for k, v in old.items() if k != 'native_fingerprints'}
        new = {k: v for k, v in new.items() if k != 'native_fingerprints'}
    assert baseline == old or baseline == new, 'Historical baseline does not match authorized repair'
    assert current == new, 'Current state differs from authorized post-repair baseline'
    return {'receipt': RECEIPT.relative_to(ROOT).as_posix(), 'sha256': digest(RECEIPT), 'historical_baseline_rewritten': False}


def readback():
    c18.c17.profils.guard('imagine-test-demo')
    receipt = json.loads(RECEIPT.read_text(encoding='utf-8'))
    validate_receipt(receipt)
    current = snapshot()
    assert current == receipt['target_after'], 'Target or unrelated data changed after restoration'
    result = native()
    assert result['exit'] == 0 and result['total'] == 382 and not result['failures']
    print(json.dumps({'scope': 'imagine-test-demo', 'C09': '382/382', 'subscription': current['id'],
        'next_payment': current['next_payment'], 'scheduled': current['scheduled'],
        'pending_actions': [a['action_id'] for a in current['actions'] if a['status'] == 'pending' and a['hook'] == 'woocommerce_scheduled_subscription_payment'],
        'receipt': str(RECEIPT.relative_to(ROOT)), 'receipt_sha256': digest(RECEIPT)}, ensure_ascii=False))


def restore():
    assert not RECEIPT.exists(), 'Immutable receipt already exists; use --readback'
    c18.c17.profils.guard('imagine-test-demo')
    before = c18.state()
    target_before = snapshot()
    native_before = native()
    assert native_before['failures'] == ['A-PAPIER:action_native_planifiee_ou_absente_selon_statut']
    names = ['wp/outils/demo/c09-papier.php', 'wp/outils/demo/c09-calendar.php', 'wp/outils/demo/c09-papier.py']
    hashes = {n: digest(ROOT / n) for n in names}
    for name in names[:2]:
        target = 'imagine-demo-build/' + Path(name).name
        c18.c17.profils.b00.upload(target, (ROOT / name).read_bytes())
        actual = c18.wp('$p=WP_CONTENT_DIR.' + json.dumps('/' + target) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo wp_json_encode(hash_file("sha256",$p));')
        assert actual == hashes[name]
    replay = c18.wp('require WP_CONTENT_DIR."/imagine-demo-build/c09-papier.php";')
    # Separate PHP processes: persisted objects/actions, not the return of save().
    target_after = snapshot()
    after = c18.state()
    native_after = native()
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'status': 'VERIFIED',
        'authorization': 'A-FAIRE-2.md consigne 1, 2026-11-26 01:30; docs/arbitrages-2026-11-26.md',
        'global_seed_replayed': False, 'source_sha256': hashes, 'replay': replay,
        'before': before, 'after': after, 'target_before': target_before, 'target_after': target_after,
        'native_before': native_before, 'native_after': native_after}
    validate_receipt(receipt)
    save_new(RECEIPT, receipt)
    readback()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--restore', action='store_true')
    mode.add_argument('--readback', action='store_true')
    args = parser.parse_args()
    restore() if args.restore else readback()
