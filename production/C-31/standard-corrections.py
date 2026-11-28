"""Contrats officiels réellement installés : ordre des appels, signatures et empreintes."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'wp/outils/demo'))
import c31 as o
import b13
o.guard()
code = r'''$methods=[['WC_Checkout','process_checkout'],['WC_Checkout','get_posted_data'],['WC_Checkout','update_session'],['WC_Form_Handler','save_account_details'],['WP_REST_Server','respond_to_request']];$out=['versions'=>['wp'=>get_bloginfo('version'),'woocommerce'=>WC_VERSION],'methods'=>[]];foreach($methods as [$class,$method]){$r=new ReflectionMethod($class,$method);$src=implode('',array_slice(file($r->getFileName()),$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));$out['methods'][$class.'::'.$method]=['file'=>str_replace(ABSPATH,'',$r->getFileName()),'start'=>$r->getStartLine(),'sha256'=>hash('sha256',$src)];if($method==='process_checkout'){$out['checkout_get_posted_data_before_session']=strpos($src,'$this->get_posted_data()')<strpos($src,'$this->update_session(');}if($method==='get_posted_data'){$out['checkout_posted_data_filter_present']=str_contains($src,"'woocommerce_checkout_posted_data'");}if($method==='update_session'){$out['session_saves_customer']=str_contains($src,'WC()->customer->save()');}if($method==='save_account_details'){$out['account_errors_before_native_save']=strpos($src,'woocommerce_save_account_details_errors')<strpos($src,'wp_update_user(');}if($method==='respond_to_request'){$guard=strpos($src,"'rest_request_before_callbacks'");$callback=strrpos($src,'call_user_func(');$out['rest_guard_before_callback']=$guard!==false && $callback!==false && $guard<$callback;}}echo wp_json_encode($out);'''
result = o.wp(code)
for key in ['checkout_get_posted_data_before_session','checkout_posted_data_filter_present','session_saves_customer','account_errors_before_native_save','rest_guard_before_callback']:
    assert result[key], key
result['documentation'] = [
    'https://developer.wordpress.org/reference/hooks/rest_request_before_callbacks/',
    'https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/checkout/',
    'https://developer.wordpress.org/reference/hooks/registration_errors/',
]
b13.save(o, sys.argv[1], result)
print(result)
