"""C20 native evidence only; fixed fictitious target; no services."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import profils
ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-20'


def wp(code):
    return json.loads(profils.b00.wp('eval', code)['stdout'])


def save(name, data):
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / (name + '-V2.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def inspect():
    profils.guard('imagine-test-demo')
    data = wp(r'''$f=get_option('imagine_c09_fixture');$out=[];foreach(['A-CARTE','A-SEPA4','A-VIR','A-PAPIER'] as $code){$s=wcs_get_subscription($f['subscriptions'][$code]);$out[$code]=['id'=>$s->get_id(),'status'=>$s->get_status(),'method'=>$s->get_payment_method(),'manual'=>$s->get_requires_manual_renewal(),'dates'=>array_combine(['start','end','next_payment','cancelled','trial_end'],array_map(fn($d)=>$s->get_date($d,'gmt'),['start','end','next_payment','cancelled','trial_end'])),'period'=>$s->get_billing_period(),'interval'=>$s->get_billing_interval(),'term'=>$s->calculate_date('end_of_prepaid_term'),'actions'=>array_keys(wcs_get_all_user_actions_for_subscription($s,$s->get_customer_id()))];}echo wp_json_encode($out);''')
    save('native-baseline', data)
    print(json.dumps(data, ensure_ascii=False))
    data = wp(r'''$out=[];foreach(['WC_Subscription'=>['update_status','calculate_date','update_dates'],'WC_Subscriptions_Change_Status_Handler'=>['change_users_subscription']] as $class=>$methods){foreach($methods as $method){if(!method_exists($class,$method)){continue;}$r=new ReflectionMethod($class,$method);$lines=file($r->getFileName());$out[$class.'::'.$method]=['file'=>$r->getFileName(),'line'=>$r->getStartLine(),'source'=>implode('',array_slice($lines,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1))];}}echo wp_json_encode($out);''')
    save('native-source', data)
    print(json.dumps(data, ensure_ascii=False))


def probe():
    profils.guard('imagine-test-demo')
    import hashlib
    source = ROOT / 'wp/tests/demo/c20-native.php'
    target = 'imagine-demo-build/c20-native.php'
    profils.b00.upload(target, source.read_bytes())
    actual = wp('echo wp_json_encode(hash_file("sha256", WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php"));')
    assert actual == hashlib.sha256(source.read_bytes()).hexdigest()
    read_only = 'define("IMAGINE_C20_READ_ONLY", true); require WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php";'
    before = wp(read_only)
    save('before', before)
    data = wp('token_get_all(file_get_contents(WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php"), TOKEN_PARSE); require WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php";')
    data['source_sha256'] = actual
    save('native-acceptance-red', data)
    after = wp(read_only)
    save('after', after)
    restored = {'profiles_exact': before['profiles'] == after['profiles'],
                'tables_exact': before['fingerprints'] == after['fingerprints'],
                'table_count': len(before['fingerprints']),
                'A-PAPIER_payment': [a for a in after['profiles']['A-PAPIER']['actions'] if a['hook'] == 'woocommerce_scheduled_subscription_payment']}
    save('restoration', restored)
    print(json.dumps({'restoration': restored}, ensure_ascii=False))
    assert restored['profiles_exact'], 'Targeted profiles/actions drift after rollback'
    print(json.dumps({'verdict': data['verdict'], 'total': data['acceptance_total'], 'passed': data['acceptance_passed'], 'failures': data['failures'], 'effects_blocked': data['effects_blocked'], 'rollback': {k: v['identical'] for k, v in data['rollback'].items()}}, ensure_ascii=False))
    return 2 if data['failures'] else 0


if __name__ == '__main__':
    if '--verify' in sys.argv:
        profils.guard('imagine-test-demo')
        before = json.loads((PROOF / 'before-V2.json').read_text(encoding='utf-8'))
        after = wp('define("IMAGINE_C20_READ_ONLY", true); require WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php";')
        baseline_after = json.loads((PROOF / 'after-V2.json').read_text(encoding='utf-8'))
        c09 = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php";')
        acceptance = json.loads((PROOF / 'native-acceptance-red-V2.json').read_text(encoding='utf-8'))
        changed = [t for t, v in before['fingerprints'].items() if v != baseline_after['fingerprints'][t]]
        allowed = ['wp_actionscheduler_actions', 'wp_actionscheduler_logs', 'wp_options', 'wp_woocommerce_sessions']
        import hashlib
        source_hash = hashlib.sha256((ROOT / 'wp/tests/demo/c20-native.php').read_bytes()).hexdigest()
        remote_hash = wp('echo wp_json_encode(hash_file("sha256", WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php"));')
        checks = {'probe_source_exact': source_hash == remote_hash == acceptance['source_sha256'],
                  'profiles_actions_exact_fresh_process': before['profiles'] == after['profiles'],
                  'rollback_tables_exact_each_case': all(v['identical'] for v in acceptance['rollback'].values()),
                  'external_drift_limited_to_cache_session_tables': set(changed) <= set(allowed),
                  'c09_green': c09['total'] == 382 and c09['failures'] == [],
                  'no_mail_or_http_attempt': acceptance['effects_blocked'] == [],
                  'no_pret': not (PROOF / 'PRET').exists()}
        save('fresh-readback', after)
        save('c09-native-final', c09)
        save('verification', {'checks': checks, 'changed_tables_after_shutdown': changed,
             'acceptance_total': acceptance['acceptance_total'], 'acceptance_passed': acceptance['acceptance_passed'],
             'acceptance_failures': acceptance['failures'], 'verdict': acceptance['verdict']})
        print(json.dumps({'checks': checks, 'c09_total': c09['total'], 'c09_failures': c09['failures'], 'acceptance_failures': acceptance['failures'], 'changed_tables_after_shutdown': changed}, ensure_ascii=False))
        assert all(checks.values())
        sys.exit(0)
    if '--probe' in sys.argv:
        sys.exit(probe())
    inspect()
