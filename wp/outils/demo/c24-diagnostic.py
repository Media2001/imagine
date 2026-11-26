"""Diagnostic en lecture seule après un inverse HTTP refusé, sans contenu de session."""
import sys
sys.dont_write_bytecode=True
import json
import c24

def run(label):
    c24.guard()
    old=json.loads((c24.PROOF/'baseline-V2.json').read_text(encoding='utf-8'))['state'];new=c24.state()
    data={'native_comparison':{k:old['native'].get(k)==new['native'].get(k) for k in old['native']},'business_schedule_equal':old['schedule_business']==new['schedule_business']}
    data['profiles']=c24.wp(r'''$f=get_option('imagine_c09_fixture')['users'];$out=[];foreach(['A-PAPIER','A-SEPA4','A-SANSMAIL','E-ADMIN'] as $k){$id=$f[$k];$out[$k]=['id'=>$id,'sessions'=>array_values(array_map(static fn($s)=>['login'=>$s['login']??null,'expiration'=>$s['expiration']??null],get_user_meta($id,'session_tokens',true)?:[])),'c24_answers'=>Imagine\Site\Personnalisation::reponses($id),'c24_consent'=>Imagine\Site\Personnalisation::consentement($id),'newsletters'=>Imagine\Site\Newsletters::preferences($id)];}echo wp_json_encode($out);''')
    data['observation']=c24.wp(r'''global $wpdb;$rows=$wpdb->get_col("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_c24_observation_%'");$out=['requests'=>count($rows),'mail'=>0,'http'=>0,'blocked'=>0,'subject_http'=>0];foreach($rows as $r){$r=maybe_unserialize($r);$out['mail']+=$r['mail'];$out['http']+=$r['http'];$out['blocked']+=$r['http_blocked'];$out['subject_http']+=$r['personalisation_http'];}echo wp_json_encode($out);''')
    c24.save(label,data);print(json.dumps(data,ensure_ascii=False))

if __name__=='__main__':run(sys.argv[1])
