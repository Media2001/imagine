import sys
sys.dont_write_bytecode=True
import c30 as o
import b13
o.guard()
r=o.wp('''$out=[];foreach(['includes/class-wc-session-handler.php','src/Internal/Orders/OrderAttributionController.php'] as $n){$p=WP_PLUGIN_DIR.'/woocommerce/'.$n;if(!is_file($p)){throw new RuntimeException('Source native absente');}$lines=file($p);$hits=[];foreach($lines as $i=>$line){if(preg_match('/session_expiration|session_expiring|default_expiration|default_expiring|wc_order_attribution|sbjs|sourcebuster/i',$line)){$hits[]=['line'=>$i+1,'text'=>trim($line)];}}$out[$n]=['sha256'=>hash_file('sha256',$p),'hits'=>$hits];}echo wp_json_encode($out);''')
b13.save(o,sys.argv[1],r)
print(r)
