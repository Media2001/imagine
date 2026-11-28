"""Sources officielles installées et chemins natifs, démo seule."""
import sys
sys.dont_write_bytecode=True
import c31 as o
import b13
o.guard()
r=o.wp('''$out=[];foreach(['register_new_user','wc_create_new_customer'] as $name){$r=new ReflectionFunction($name);$src=implode('',array_slice(file($r->getFileName()),$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));preg_match_all('/apply_filters\\(\\s*[\"\\\'](registration_errors|woocommerce_registration_errors)[\"\\\']/',$src,$m);$out[$name]=['file'=>str_replace(ABSPATH,'',$r->getFileName()),'start'=>$r->getStartLine(),'end'=>$r->getEndLine(),'sha256'=>hash('sha256',$src),'hooks'=>$m[1]];}$r=new ReflectionMethod('WC_Checkout','process_customer');$src=implode('',array_slice(file($r->getFileName()),$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));$out['WC_Checkout::process_customer']=['calls_native_customer'=>str_contains($src,'wc_create_new_customer('),'sha256'=>hash('sha256',$src)];echo wp_json_encode($out);''')
b13.save(o,sys.argv[1],r)
print(r)
