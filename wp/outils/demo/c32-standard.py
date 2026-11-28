import sys
sys.dont_write_bytecode=True
import hashlib,re,urllib.request
from html.parser import HTMLParser
import c32 as o
class Text(HTMLParser):
    def __init__(self):super().__init__();self.out=[]
    def handle_data(self,s):self.out.append(s)
refs=[]
for url,terms in [('https://woocommerce.com/document/woocommerce-cookies/',['sbjs_session','sbjs_migrations','wp_woocommerce_session_','woocommerce_cart_hash']),('https://woocommerce.com/document/order-attribution-tracking/',['Advanced','Order attribution','30 minutes']),('https://developer.wordpress.org/advanced-administration/wordpress/cookies/',['wordpress_logged_in_','wordpress_test_cookie','comment_author'])]:
    raw=urllib.request.urlopen(url,timeout=40).read();p=Text();p.feed(raw.decode());text=' '.join(' '.join(p.out).split());found={t:text.find(t) for t in terms};assert any(v>=0 for v in found.values());refs.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'terms_present':{k:v>=0 for k,v in found.items()}})
native=o.wp('$f=WC_ABSPATH."includes/class-wc-session-handler.php";$s=file_get_contents($f);$r=new ReflectionFunction("wp_set_auth_cookie");$lines=file($r->getFileName());$auth=implode("",array_slice($lines,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));echo wp_json_encode(["core"=>get_bloginfo("version"),"woo"=>WC_VERSION,"attribution"=>get_option("woocommerce_feature_order_attribution_enabled"),"session_sha256"=>hash_file("sha256",$f),"session_default_2_days"=>str_contains($s,"2 * DAY_IN_SECONDS"),"auth_default_2_days"=>str_contains($auth,"2 * DAY_IN_SECONDS"),"remember_14_days"=>str_contains($auth,"14 * DAY_IN_SECONDS"),"comment_registration"=>get_option("default_comment_status")]);')
assert native['session_default_2_days'] and native['auth_default_2_days'] and native['remember_14_days']
o.b13.save(o,sys.argv[1],{'official':refs,'native':native,'disable_attribution_option':'woocommerce_feature_order_attribution_enabled=no','sources':o.sources(o)})
print(native)
