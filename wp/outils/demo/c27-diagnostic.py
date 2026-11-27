"""Diagnostic ponctuel C27, fiction uniquement, toutes les inverses relues."""
import sys
sys.dont_write_bytecode=True
import importlib.util,re,urllib.request,json
import c27
spec=importlib.util.spec_from_file_location('native',c27.ROOT/'wp/outils/demo/c27-native.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
c27.guard();saved=c27.snapshot();before=c27.state();c27.private('c27-diagnostic',{'database':saved})
row=None
try:
    c27.wp('update_option(Imagine\\Site\\Acquisition::OPTION,["lune"=>"Radio fictive"],false);echo wp_json_encode(true);')
    row=c27.wp('$o=wc_create_order(["customer_id"=>28,"status"=>"pending","created_via"=>"checkout"]);$o->set_total(1);$o->set_status("processing");$o->set_date_paid(time());$o->save();$token=WP_Session_Tokens::get_instance(28)->create(time()+600);echo wp_json_encode(["id"=>$o->get_id(),"url"=>$o->get_checkout_order_received_url(),"eligible"=>Imagine\\Site\\Acquisition::eligible($o,28),"paid"=>$o->is_paid(),"cookie"=>LOGGED_IN_COOKIE."=".wp_generate_auth_cookie(28,time()+600,"logged_in",$token)]);')
    with urllib.request.urlopen(urllib.request.Request(row['url'],headers={'Cookie':row['cookie']}),timeout=40) as r:body=r.read().decode()
    print({k:v for k,v in row.items() if k not in ['url','cookie']})
    visible=re.sub(r'<(script|style)\b.*?</\1>','',body,flags=re.S)
    print(re.sub('<[^>]+>',' ',visible).strip()[-9000:])
    print(c27.wp('echo wp_json_encode(["seen"=>get_option(Imagine\\Site\\Acquisition::VUE . '+str(row['id'])+',null),"hooks"=>has_action("woocommerce_thankyou",[Imagine\\Site\\Acquisition::class,"question"]),"content"=>get_post(wc_get_page_id("checkout"))->post_content]);'))
finally:
    if row:c27.wp('wc_get_order('+str(row['id'])+')->delete(true);echo wp_json_encode(true);')
    native.restore_options(saved);native.restore_users(saved,{28})
    result=native.compare(saved,c27.snapshot());print(result);assert all(result.values()) and before==c27.state()
