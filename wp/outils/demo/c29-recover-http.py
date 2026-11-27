"""Undo only C29 HTTP fixture's additional options, with exact before/after hashes."""
import sys
sys.dont_write_bytecode=True
import json
import b11
import c19
import c29

def run():
    b11.guard()
    m=json.loads((c29.OUT/'http-first-V2.json').read_text(encoding='utf-8'))
    old,new=m['strict_before']['option_fingerprints'],m['strict_after']['option_fingerprints']
    added={k:v for k,v in new.items() if k not in old}
    assert set(added)=={'imagine_personnalisation_reserve_c_a','imagine_personnalisation_reserve_q_fictif','imagine_reglages_journal_a14f916402254fc19cde16e3e4338b91','imagine_reglages_journal_6005491c83554d3f91a0f06a7a8056e4','_transient_settings_errors','_transient_timeout_settings_errors'}
    result=b11.wp('global $wpdb;$keys='+b11.php(added)+''';$wpdb->query('START TRANSACTION');try{foreach($keys as $n=>$sha){$row=$wpdb->get_row($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name=%s",$n),ARRAY_A);if(hash('sha256',serialize($row))!==$sha){throw new RuntimeException('CAS option changed');}$wpdb->delete($wpdb->options,['option_name'=>$n]);}$wpdb->query('COMMIT');wp_cache_flush();echo wp_json_encode(true);}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}''')
    current=c19.state()
    remaining={k for k in set(old)|set(current['option_fingerprints']) if old.get(k)!=current['option_fingerprints'].get(k)}
    allowed={'_transient_timeout_novamira_update_info','_transient_timeout_as_is_ensure_recurring_actions_scheduled','_transient_timeout_woocommerce_admin_settings_payments_has_providers_with_incentive'}
    assert remaining<=allowed and current['native_fingerprints']==m['strict_before']['native_fingerprints']
    c29.save('recovery-HTTP-fixture-V2',{'options_removed':list(added),'native_exact':True,'remaining_only_evidenced_cache_timeouts':sorted(remaining)})
    print(result, sorted(remaining))
if __name__=='__main__':run()
