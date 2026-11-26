"""Reprise bornée du premier HTTP : ne prétend PAS restaurer le snapshot perdu."""
import sys
sys.dont_write_bytecode=True
import json
import c24

def run(label):
    c24.guard()
    assert not (c24.PROOF/(label+'.json')).exists()
    before=c24.state()
    # Coordonnées observées par c24-recovery-plan.py, aucun reset ni réensemencement.
    result=c24.wp(r'''global $wpdb;$removed=[];
foreach([[12988,13,'imagine_personnalisation_consentement'],[12989,13,'imagine_newsletters_preferences'],[12990,19,'imagine_personnalisation_reponses']] as [$mid,$uid,$key]){
$r=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE umeta_id=%d",$mid),ARRAY_A);if(!$r||(int)$r['user_id']!==$uid||$r['meta_key']!==$key)throw new RuntimeException('Coordonnée de reprise divergente');
if($wpdb->delete($wpdb->usermeta,['umeta_id'=>$mid])!==1)throw new RuntimeException('Suppression témoin refusée');$removed[]=$mid;wp_cache_delete($uid,'user_meta');}
$sessions=[];foreach([13,10,19,30] as $id){$values=get_user_meta($id,'session_tokens',true);$count=0;foreach($values as $token=>$session){if(($session['login']??0)===1795714988&&($session['expiration']??0)===1795718588){unset($values[$token]);$count++;}}if($count!==1)throw new RuntimeException('Session propre non identifiée');update_user_meta($id,'session_tokens',$values);$sessions[$id]=$count;}
$first=8721;$last=8791;$rows=$wpdb->get_results($wpdb->prepare("SELECT option_id,option_name FROM {$wpdb->options} WHERE option_id BETWEEN %d AND %d ORDER BY option_id",$first,$last),ARRAY_A);$names=[];
foreach($rows as $r){$n=$r['option_name'];if(!str_starts_with($n,'imagine_c24_observation_')&&!str_starts_with($n,'imagine_reglages_journal_')&&!str_starts_with($n,'imagine_newsletters_reserve_')&&!in_array($n,['imagine_decouverte_reglages','imagine_decouverte_relecture','imagine_solidaire_categories','imagine_newsletters_creation','imagine_personnalisation_reserve_q_cinquieme-c24-1ebeafab32','imagine_personnalisation_reserve_c_choix-cinquieme-c24-1ebeafab32'],true))throw new RuntimeException('Option hors reprise');$names[]=$n;}
foreach($names as $n){if($wpdb->delete($wpdb->options,['option_name'=>$n])!==1)throw new RuntimeException('Inverse option refusé');wp_cache_delete($n,'options');}wp_cache_delete('alloptions','options');wp_cache_delete('notoptions','options');
echo wp_json_encode(['owned_meta_removed'=>$removed,'owned_sessions_removed'=>$sessions,'owned_new_options_removed'=>$names]);''')
    expected=json.loads((c24.PROOF/'baseline-V2.json').read_text(encoding='utf-8'))['state']
    after=c24.state()
    absent=c24.wp(r'''global $wpdb;echo wp_json_encode(['metas'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE umeta_id IN (12988,12989,12990)"),'observations'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_c24_observation_%'"),'sessions'=>array_map(static fn($id)=>count(array_filter(get_user_meta($id,'session_tokens',true)?:[],static fn($s)=>($s['login']??0)===1795714988)),[13,10,19,30])]);''')
    assert absent=={'metas':0,'observations':0,'sessions':[0,0,0,0]}
    data={'result':result,'readback':absent,'baseline_native_equal':after==expected,'native_comparison':{k:expected['native'][k]==after['native'][k] for k in expected['native']},'business_actions_equal':expected['schedule_business']==after['schedule_business'],'exact_initial_snapshot_restored':False,'blocker':'Premier inverse HTTP refusé avant restauration ; ancien snapshot uniquement en mémoire perdu. Les sessions antérieures, le verrou natif action_scheduler_lock_async-request-runner et les caches ne peuvent plus être prouvés octet pour octet. Aucun PRET.'}
    c24.save(label,data);print(json.dumps(data,ensure_ascii=False))

if __name__=='__main__':run(sys.argv[1])
