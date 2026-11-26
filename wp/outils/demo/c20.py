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


if __name__ == '__main__':
    inspect()
