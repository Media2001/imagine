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
    data['native_action_source'] = wp(r'''$out=[];foreach(['wcs_get_all_user_actions_for_subscription','wcs_can_user_change_status'] as $fn){if(function_exists($fn)){$r=new ReflectionFunction($fn);$ls=file($r->getFileName());$out[$fn]=implode('',array_slice($ls,$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));}}$r=new ReflectionClass('WCS_User_Change_Status_Handler');$out['handler']=file_get_contents($r->getFileName());echo wp_json_encode($out);''')
    save('native-details', data)
    print(json.dumps({k:v for k,v in data.items() if k not in ('integration_sources','native_action_source')}, ensure_ascii=False))
    print('integration source files:', list(data.get('integration_sources',{})))

def ui(label):
    c20.profils.guard('imagine-test-demo')
    source = ROOT / 'wp/tests/demo/c20-ui.php'
    target = 'imagine-demo-build/c20-ui.php'
    c20.profils.b00.upload(target, source.read_bytes())
    assert wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR . "/' + target + '"));') == hashlib.sha256(source.read_bytes()).hexdigest()
    before = snapshot()
    data = wp('require WP_CONTENT_DIR . "/' + target + '";')
    after = snapshot()
    data['profiles_actions_unchanged'] = before['profiles'] == after['profiles']
    save(label, data)
    print(json.dumps(data, ensure_ascii=False))
    assert data['profiles_actions_unchanged']
    return 1 if data['failures'] else 0

def deploy_adapter():
    c20.profils.guard('imagine-test-demo')
    name = 'plugins/imagine-site/Paywall.php'
    source = ROOT / 'wp' / name
    baseline = json.loads((PROOF / 'protected-baseline-second-V2.json').read_text(encoding='utf-8'))
    before = snapshot()
    prior = wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR . "/' + name + '"));')
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    assert prior in (baseline['wp/' + name], current), 'Refuse overwriting unknown live source'
    c20.profils.b00.upload(name, source.read_bytes())
    actual = wp('token_get_all(file_get_contents(WP_CONTENT_DIR . "/' + name + '"),TOKEN_PARSE);echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR . "/' + name + '"));')
    after = snapshot()
    checks = {'source_exact': actual == current, 'profiles_actions_exact': before['profiles'] == after['profiles']}
    save('adapter-installation', {'prior_sha256':prior, 'sha256':actual, 'checks':checks})
    print(json.dumps(checks))
    assert all(checks.values())

def snapshot():
    return wp('define("IMAGINE_C20_READ_ONLY",true); require WP_CONTENT_DIR . "/imagine-demo-build/c20-native.php";')

def probe(label):
    c20.profils.guard('imagine-test-demo')
    src = ROOT / 'wp/tests/demo/c20-second-native.php'
    target = 'imagine-demo-build/c20-second-native.php'
    c20.profils.b00.upload(target, src.read_bytes())
    actual = wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR . "/' + target + '"));')
    assert actual == hashlib.sha256(src.read_bytes()).hexdigest()
    before = snapshot()
    save(label + '-before', before)
    data = wp('token_get_all(file_get_contents(WP_CONTENT_DIR . "/' + target + '"),TOKEN_PARSE);require WP_CONTENT_DIR . "/' + target + '";')
    after = snapshot()
    data['source_sha256'] = actual
    data['fresh_profiles_actions_exact'] = before['profiles'] == after['profiles']
    save(label, data)
    save(label + '-after', after)
    print(json.dumps({'checks':data['checks'], 'failures':data['failures'], 'fresh_profiles_actions_exact':data['fresh_profiles_actions_exact'], 'four':data['four']['result']['checks'], 'four_supported':data['four']['result']['supported'], 'four_C05_end':data['four']['result']['C05_block_end'], 'four_C05_remaining':data['four']['result']['C05_remaining'], 'four_native_dates':data['four']['result']['native_pending_payment_dates'], 'resumption':data['carte']['result']['resumption']}, ensure_ascii=False))
    assert data['fresh_profiles_actions_exact'], 'STOP: profile/action drift'
    return 1 if data['failures'] else 0

if __name__ == '__main__':
    if '--ui' in sys.argv:
        sys.exit(ui(sys.argv[-1]))
    elif '--deploy-adapter' in sys.argv:
        deploy_adapter()
    elif '--probe' in sys.argv:
        sys.exit(probe(sys.argv[-1]))
    elif '--details' in sys.argv:
        inspect_more()
    else:
        inspect()
