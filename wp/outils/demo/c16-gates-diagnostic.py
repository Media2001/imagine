"""Bounded read-only diagnosis of the existing C09 A-PAPIER fixture."""
from datetime import datetime, timezone
import json
import sys
sys.dont_write_bytecode = True
import c16

CODE = r'''$f=get_option('imagine_c09_fixture');$id=(int)$f['subscriptions']['A-PAPIER'];$s=wcs_get_subscription($id);if(!$s||$s->get_meta('_imagine_c09_fixture')!=='A-PAPIER')throw new RuntimeException('Foreign fixture');$out=['at'=>gmdate('c'),'seeded_at'=>get_option('imagine_c09_seeded_at'),'id'=>$id,'status'=>$s->get_status(),'manual'=>$s->get_requires_manual_renewal(),'gateway'=>$s->get_payment_method(),'next_payment'=>$s->get_date('next_payment'),'scheduled'=>as_next_scheduled_action('woocommerce_scheduled_subscription_payment',['subscription_id'=>$id]),'related_renewals'=>array_values($s->get_related_orders('ids','renewal')),'actions'=>[]];foreach(['pending','complete','failed','canceled','in-progress'] as $status){$actions=as_get_scheduled_actions(['hook'=>'woocommerce_scheduled_subscription_payment','args'=>['subscription_id'=>$id],'status'=>$status,'date'=>time(),'date_compare'=>'<=','per_page'=>10,'orderby'=>'date','order'=>'DESC'],'OBJECT');foreach($actions as $aid=>$a){$logs=[];foreach(ActionScheduler::logger()->get_logs($aid) as $log){$logs[]=['date'=>$log->get_date()->format('Y-m-d H:i:s'),'message'=>$log->get_message()];}$out['actions'][]=['id'=>$aid,'status'=>$status,'scheduled'=>$a->get_schedule()->get_date()->format('Y-m-d H:i:s'),'logs'=>$logs];}}$out['native_sources']=[];foreach(['WCS_Action_Scheduler','WC_Subscriptions_Manager'] as $class){$r=new ReflectionClass($class);$out['native_sources'][$class]=['file'=>$r->getFileName(),'sha256'=>hash_file('sha256',$r->getFileName())];}echo wp_json_encode($out);'''

if __name__ == '__main__':
    c16.profils.guard('imagine-test-demo')
    result = c16.wp(CODE)
    c16.save(sys.argv[1] if len(sys.argv) > 1 else 'gates-c09-diagnostic', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
