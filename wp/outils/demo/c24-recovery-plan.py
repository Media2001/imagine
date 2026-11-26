"""Inventaire de reprise C24, sans valeurs de session ni secrets."""
import sys
sys.dont_write_bytecode=True
import json
import c24
c24.guard()
old=json.loads((c24.PROOF/'baseline-V2.json').read_text(encoding='utf-8'))['state'];new=c24.state()
print(json.dumps({'option_differences':{k:{'before':v,'after':new['native']['options'].get(k)} for k,v in old['native']['options'].items() if v!=new['native']['options'].get(k)},'fingerprint_differences':{k:{'before':v,'after':new['native']['native_fingerprints'].get(k)} for k,v in old['native']['native_fingerprints'].items() if v!=new['native']['native_fingerprints'].get(k)}},ensure_ascii=False))
print(json.dumps(c24.wp(r'''global $wpdb;$out=[];$first=(int)$wpdb->get_var("SELECT MIN(option_id) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_c24_observation_%'");$out['first_observation']=$first;$out['new_options']=[];foreach($wpdb->get_results($wpdb->prepare("SELECT option_id,option_name,option_value FROM {$wpdb->options} WHERE option_id>=%d ORDER BY option_id",$first),ARRAY_A) as $r){$v=maybe_unserialize($r['option_value']);$out['new_options'][]=['id'=>$r['option_id'],'name'=>$r['option_name'],'event'=>str_starts_with($r['option_name'],'imagine_reglages_journal_')?$v:null];}$out['meta_coordinates']=$wpdb->get_results("SELECT umeta_id,user_id,meta_key FROM {$wpdb->usermeta} WHERE user_id IN (13,10,19,30) AND (meta_key LIKE 'imagine_personnalisation_%' OR meta_key IN ('imagine_newsletters_preferences','_woocommerce_tracks_anon_id','session_tokens')) ORDER BY umeta_id",ARRAY_A);echo wp_json_encode($out);'''),ensure_ascii=False))
