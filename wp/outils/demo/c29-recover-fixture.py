"""Emergency C29-only restoration from existing demo snapshot, checksum-gated before COMMIT."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
from pathlib import Path
import b11
import c19
import c29

def run():
    b11.guard()
    baseline=json.loads((c29.OUT/'http-first-V2.json').read_text(encoding='utf-8'))['strict_before']
    p=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/c25-private-im2rijcu/snapshot.json')
    stored=json.loads(p.read_text(encoding='utf-8'));assert stored['scope']=='imagine-test-demo'
    db=stored['payload']['database'];ids=list(baseline['manifeste']['users'].values())
    keys=['imagine_newsletters_preferences','imagine_personnalisation_reponses','imagine_personnalisation_consentement','imagine_cooperateur','imagine_sans_email','session_tokens']
    rows=[r for r in db['usermeta'] if int(r['user_id']) in ids and r['meta_key'] in keys]
    names=['imagine_newsletters_catalogue','imagine_personnalisation_questions','imagine_brevo_tarifs']
    options=[r for r in db['options'] if r['option_name'] in names]
    targets=names+['imagine_personnalisation_reserve_c_a','imagine_personnalisation_reserve_q_fictif','_transient_settings_errors','_transient_timeout_settings_errors']
    current=c19.state();added=[k for k in current['option_fingerprints'] if k not in baseline['option_fingerprints'] and k.startswith('imagine_reglages_journal_')]
    targets+=added
    volatile=['_transient_timeout_wcs_woocommerce_active_version','_transient_timeout_novamira-pro_update_checker','action_scheduler_lock_async-request-runner','_transient_timeout_novamira_update_info','_transient_timeout_as_is_ensure_recurring_actions_scheduled','_transient_timeout_woocommerce_admin_settings_payments_has_providers_with_incentive']
    stable={k:v for k,v in baseline['option_fingerprints'].items() if k not in volatile}
    expected_hash=hashlib.sha256(json.dumps(stable,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    code='global $wpdb;$rows='+b11.php(rows)+';$ids='+b11.php(ids)+';$keys='+b11.php(keys)+';$options='+b11.php(options)+';$targets='+b11.php(targets)+';$expectedMeta='+b11.php(baseline['native_fingerprints']['usermeta'])+';$expectedOptions='+b11.php(expected_hash)+''';$wpdb->query('START TRANSACTION');try{
foreach($ids as $id){foreach($keys as $key){$wpdb->delete($wpdb->usermeta,['user_id'=>$id,'meta_key'=>$key]);}}foreach($rows as $row){if($wpdb->insert($wpdb->usermeta,$row)!==1){throw new RuntimeException('Meta insert');}}
$native=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key NOT IN ('session_tokens','_woocommerce_persistent_cart_1','_last_update','wc_last_active')",ARRAY_A);$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$native);sort($hashes);if(['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))]!==$expectedMeta){throw new RuntimeException('Original metadata checksum not restored : ROLLBACK');}
foreach($targets as $n){$wpdb->delete($wpdb->options,['option_name'=>$n]);}foreach($options as $row){$wpdb->insert($wpdb->options,$row);}
$volatile=['_transient_timeout_wcs_woocommerce_active_version','_transient_timeout_novamira-pro_update_checker','action_scheduler_lock_async-request-runner','_transient_timeout_novamira_update_info','_transient_timeout_as_is_ensure_recurring_actions_scheduled','_transient_timeout_woocommerce_admin_settings_payments_has_providers_with_incentive'];$actual=[];foreach($wpdb->get_results("SELECT option_name,option_value,autoload FROM {$wpdb->options}",ARRAY_A) as $r){if(!in_array($r['option_name'],$volatile,true)){$actual[$r['option_name']]=hash('sha256',serialize($r));}}ksort($actual);if(hash('sha256',wp_json_encode($actual,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES))!==$expectedOptions){throw new RuntimeException('Original business option checksum not restored : ROLLBACK');}
$wpdb->query('COMMIT');wp_cache_flush();echo wp_json_encode(['original_metadata_exact'=>true,'original_business_options_exact'=>true]);
}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}'''
    result=b11.wp(code)
    b11.b10.b09.remove_remote(['mu-plugins/c29-observer.php'])
    after=c19.state()
    assert after['native_fingerprints']==baseline['native_fingerprints']
    c29.save('recovery-HTTP-finally-interrupted-V2',{'result':result,'source_snapshot':p.name,'source_directory':p.parent.name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_all_tables_exact':True,'scope':'imagine-test-demo','session_source':'Existing private C27 snapshot; no original C29 session fingerprint was saved.','probe_removed':b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/c29-observer.php"));')})
    print(result,'all native tables original checksum exact')
if __name__=='__main__':run()
