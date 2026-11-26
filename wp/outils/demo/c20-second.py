"""C20 second pass, guarded offline native evidence and scoped code."""
from pathlib import Path
import json, sys, hashlib
sys.dont_write_bytecode = True
import c20
ROOT = c20.ROOT
PROOF = ROOT / 'production/C-20'
wp = c20.wp

def save(name, data):
    path = PROOF / (name + '-second-V2.json')
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def inspect():
    c20.profils.guard('imagine-test-demo')
    data = wp(r'''$out=[];foreach(['WC_Subscription'=>['can_be_updated_to','update_dates','calculate_date','payment_method_supports'],'WC_Subscriptions_Change_Status_Handler'=>['change_users_subscription']] as $c=>$ms){foreach($ms as $m){if(!method_exists($c,$m)){continue;}$r=new ReflectionMethod($c,$m);$ls=file($r->getFileName());$out[$c.'::'.$m]=['file'=>$r->getFileName(),'line'=>$r->getStartLine(),'source'=>implode('',array_slice($ls,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1))];}}$out['memberships_files']=glob(WP_PLUGIN_DIR.'/woocommerce-memberships/includes/integrations/subscriptions/*.php');$out['echeancier_files']=[];foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator(WP_PLUGIN_DIR.'/imagine-pilotage/src/Echeancier')) as $file){if($file->isFile()&&$file->getExtension()==='php'){$out['echeancier_files'][$file->getFilename()]=file_get_contents($file->getPathname());}}echo wp_json_encode($out);''')
    save('native-source', data)
    print(json.dumps(data, ensure_ascii=False))

def inspect_more():
    c20.profils.guard('imagine-test-demo')
    data = wp(r'''$out=[];$i=wc_memberships()->get_integrations_instance()->get_subscriptions_instance();$r=new ReflectionClass($i);$path=dirname($r->getFileName());$out['integration_class']=$r->getName();foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path)) as $f){if($f->isFile()&&$f->getExtension()==='php'){$text=file_get_contents($f->getPathname());if(str_contains($text,"'pending-cancel'")||str_contains($text,"'pending'")){$out['integration_sources'][$f->getPathname()]=$text;}}}foreach(['WC_Subscription'=>['contains_unavailable_product','is_manual','calculate_next_payment_date'],'WCS_User_Change_Status_Handler'=>['change_users_subscription','can_user_change_status']] as $c=>$ms){foreach($ms as $m){if(!method_exists($c,$m)){continue;}$r=new ReflectionMethod($c,$m);$ls=file($r->getFileName());$out[$c.'::'.$m]=['file'=>$r->getFileName(),'line'=>$r->getStartLine(),'source'=>implode('',array_slice($ls,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1))];}}$f=get_option('imagine_c09_fixture');foreach(['A-CARTE','A-SEPA4','A-VIR','A-PAPIER'] as $who){$s=wcs_get_subscription($f['subscriptions'][$who]);wp_set_current_user($s->get_customer_id());$out['profiles'][$who]=['id'=>$s->get_id(),'manual'=>$s->is_manual(),'method'=>$s->get_payment_method(),'products_unavailable'=>$s->contains_unavailable_product(),'status'=>$s->get_status(),'dates'=>['start'=>$s->get_date('start'),'end'=>$s->get_date('end'),'next_payment'=>$s->get_date('next_payment')],'actions'=>array_keys(wcs_get_all_user_actions_for_subscription($s,$s->get_customer_id())),'items'=>[]];foreach($s->get_items() as $item){$p=$item->get_product();$out['profiles'][$who]['items'][]=['id'=>$item->get_product_id(),'variation'=>$item->get_variation_id(),'exists'=>(bool)$p,'status'=>$p?$p->get_status():null,'purchasable'=>$p?$p->is_purchasable():null];}}echo wp_json_encode($out);''')
    save('native-details', data)
    print(json.dumps({k:v for k,v in data.items() if k!='integration_sources'}, ensure_ascii=False))
    print('integration source files:', list(data.get('integration_sources',{})))

if __name__ == '__main__':
    if '--details' in sys.argv:
        inspect_more()
    else:
        inspect()
