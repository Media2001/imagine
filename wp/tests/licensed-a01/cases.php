<?php
declare(strict_types=1);
$phase = getenv('A01_PHASE') ?: 'snapshot';
function output_a01(array $v): void { echo 'E2E_JSON=' . json_encode($v, JSON_THROW_ON_ERROR) . "\n"; }
if ($phase === 'seed') {
    // Disposable process-only mail short circuit; absent from post-clean verification.
    add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
    $product = new WC_Product_Simple(); $product->set_name('Invented monthly item'); $product->set_regular_price('12.50'); $product->save();
    $users=[]; $members=[]; $subs=[];
    foreach (['active','expired','cancelled','paused','none'] as $i=>$status) {
        $uid=wp_insert_user(['user_login'=>'a01-fictif-'.$i, 'user_email'=>'a01-fictif-'.$i.'@invented.invalid', 'user_pass'=>wp_generate_password(40), 'role'=>'subscriber']);
        if (is_wp_error($uid)) throw new RuntimeException('SYNTHETIC_USER_CREATE');
        $users[$status]=$uid;
    }
    $post=wp_insert_post(['post_type'=>'post','post_status'=>'publish','post_title'=>'Fiction only','post_content'=>'A01_PRIVATE_CANARY']);
    $public=wp_insert_post(['post_type'=>'post','post_status'=>'publish','post_title'=>'Public fiction','post_content'=>'A01_PUBLIC_CANARY']);
    $plan=wp_insert_post(['post_type'=>'wc_membership_plan','post_status'=>'publish','post_title'=>'Fiction plan','post_name'=>'a01-fiction-plan']);
    update_post_meta($plan,'_access_method','manual-only'); update_post_meta($plan,'_access_length','unlimited');
    wc_memberships()->get_rules_instance()->set_rules(['add'=>[['membership_plan_id'=>$plan,'active'=>'yes','rule_type'=>'content_restriction','content_type'=>'post_type','content_type_name'=>'post','object_ids'=>[$post],'access_schedule'=>'immediate']]]);
    foreach ($users as $status=>$uid) {
        if ($status==='none') continue;
        $m=wc_memberships_create_user_membership(['plan_id'=>$plan,'user_id'=>$uid]);
        $m->set_start_date(gmdate('Y-m-d H:i:s',time()-86400));
        if ($status==='expired') $m->set_end_date(gmdate('Y-m-d H:i:s',time()-3600));
        $m->update_status($status); $members[$status]=$m->get_id();
    }
    update_option('a01_paid_fixture',['users'=>$users,'members'=>$members,'post'=>$post,'public'=>$public,'plan'=>$plan,'subs'=>[]]);
    output_a01(['memberships_seeded'=>count($members),'subscriptions_available'=>function_exists('wcs_create_subscription')]); return;
}
$f=get_option('a01_paid_fixture');
if ($phase==='seed-subscriptions') {
    add_filter('pre_wp_mail','__return_false',PHP_INT_MAX);
    $product=new WC_Product_Simple();$product->set_name('Invented recurring item');$product->set_regular_price('12.50');$product->save();
    foreach (['active','on-hold','pending-cancel','active','on-hold','pending-cancel'] as $i=>$status) {
        $s=wcs_create_subscription(['customer_id'=>$f['users']['active'],'status'=>'pending','billing_period'=>'month','billing_interval'=>($i%2)+1,'start_date'=>gmdate('Y-m-d H:i:s',time()-86400*40)]);
        if(is_wp_error($s))throw new RuntimeException('SYNTHETIC_SUBSCRIPTION_CREATE');
        $s->set_address(['first_name'=>'Invented','last_name'=>'Person','company'=>'Invented Co','address_1'=>'100 Fiction Avenue','address_2'=>'Unit Fiction','city'=>'Fiction','state'=>'','postcode'=>'1000','country'=>'BE','email'=>'subscription-'.$i.'@invented.invalid','phone'=>'+32123456789'],'billing');
        $s->set_address(['first_name'=>'Invented','last_name'=>'Person','address_1'=>'100 Fiction Avenue','city'=>'Fiction','postcode'=>'1000','country'=>'BE'],'shipping');
        $s->set_payment_method('bacs');$s->set_requires_manual_renewal(true);$s->set_currency('EUR');
        $s->add_product($product,$i%3+1);$s->calculate_totals();
        $s->update_dates(['next_payment'=>gmdate('Y-m-d H:i:s',time()+86400*35),'end'=>gmdate('Y-m-d H:i:s',time()+86400*370)]);
        $s->save();$s->update_status('active');if($status!=='active')$s->update_status($status);$f['subs'][]=$s->get_id();
    }
    update_option('a01_paid_fixture',$f);
    output_a01(['created'=>count($f['subs'])]);return;
}
if ($phase==='rights') {
    $rights=[]; $shortcodes=[];
    foreach (array_merge(['guest'=>0],$f['users']) as $status=>$uid) {
        wp_set_current_user($uid);
        $rights[$status]=['private'=>(bool)wc_memberships_user_can($uid,'view',['post'=>$f['post']]),'public'=>!wc_memberships_is_post_content_restricted($f['public'])];
        $text=do_shortcode('[wcm_restrict plans="a01-fiction-plan"]A01_PRIVATE_CANARY[/wcm_restrict]');
        $shortcodes[$status]=str_contains($text,'A01_PRIVATE_CANARY');
    }
    output_a01(['restricted'=>wc_memberships_is_post_content_restricted($f['post']),'rights'=>$rights,'shortcodes'=>$shortcodes]);return;
}
if ($phase==='snapshot') {
    $business=[];$personal=[];
    foreach ($f['subs'] as $id) {
        $s=wcs_get_subscription($id);$items=[];
        foreach($s->get_items() as $item)$items[]=['product'=>$item->get_product_id(),'quantity'=>$item->get_quantity(),'subtotal'=>$item->get_subtotal(),'total'=>$item->get_total(),'taxes'=>$item->get_taxes()];
        $business[]=['id'=>$s->get_id(),'status'=>$s->get_status(),'customer'=>$s->get_customer_id(),'interval'=>$s->get_billing_interval(),'period'=>$s->get_billing_period(),'start'=>$s->get_date('start'),'next'=>$s->get_date('next_payment'),'end'=>$s->get_date('end'),'currency'=>$s->get_currency(),'total'=>$s->get_total(),'method'=>$s->get_payment_method(),'billing_country'=>$s->get_billing_country(),'shipping_country'=>$s->get_shipping_country(),'items'=>$items];
        $personal[]=['id'=>$id,'email_safe'=>(bool)preg_match('/@example\.org$/D',$s->get_billing_email()),'first_clean'=>!str_contains($s->get_billing_first_name(),'Invented'),'address_clean'=>!str_contains($s->get_billing_address_1(),'Fiction'),'phone_clean'=>!str_contains($s->get_billing_phone(),'123456789')];
    }
    $membership=[]; foreach($f['members'] as $k=>$id){$m=wc_memberships_get_user_membership($id);$membership[$k]=['id'=>$id,'user'=>$m->get_user_id(),'plan'=>$m->get_plan_id(),'status'=>$m->get_status(),'start'=>$m->get_start_date(),'end'=>$m->get_end_date()];}
    output_a01(['business'=>$business,'personal'=>$personal,'membership'=>$membership,'rules_sha256'=>hash('sha256',serialize(get_option('wc_memberships_rules'))),'versions'=>['wp'=>get_bloginfo('version'),'woo'=>WC()->version,'subscriptions'=>class_exists('WC_Subscriptions')?WC_Subscriptions::$version:null,'memberships'=>wc_memberships()->get_version(),'hpos'=>Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled()]]);return;
}
if ($phase==='subscription-email-residue') {
    $s=wcs_get_subscription($f['subs'][0]);$s->set_billing_email('a01-residue@invented.invalid');$s->save();
    output_a01(['subscription_id'=>$s->get_id(),'external_email_written'=>str_ends_with(wcs_get_subscription($s->get_id())->get_billing_email(),'@invented.invalid')]);return;
}
if ($phase==='runtime') {
    require_once '/subject/runtime-probe.php';output_a01(Imagine\Staging\runtimeProbe());return;
}
if ($phase==='live-mode-mutation') {
    // Subject negative canary only, still network-none/no gateway/no server.
    remove_all_filters('woocommerce_subscriptions_is_duplicate_site');
    update_option('wc_subscriptions_siteurl','_[wc_subscriptions_siteurl]_'.get_option('siteurl'));
    require_once '/subject/runtime-probe.php';output_a01(Imagine\Staging\runtimeProbe());return;
}
if ($phase==='renewal') {
    // A single named synthetic AS action, never the global queue.
    add_filter('pre_wp_mail','__return_false',PHP_INT_MAX);
    $sub=wcs_get_subscription($f['subs'][0]);
    $before=count($sub->get_related_orders('ids','renewal'));
    $calls=0;add_action('woocommerce_scheduled_subscription_payment',function()use(&$calls){$calls++;},PHP_INT_MIN);
    $action=as_schedule_single_action(time()-5,'woocommerce_scheduled_subscription_payment',['subscription_id'=>$sub->get_id()],'a01-synthetic-renewal');
    ActionScheduler::runner()->process_action($action,'A01-disposable-only');
    $after=count(wcs_get_subscription($sub->get_id())->get_related_orders('ids','renewal'));
    output_a01(['action_id'=>$action,'status'=>ActionScheduler::store()->get_status($action),'callback_calls'=>$calls,'renewals_before'=>$before,'renewals_after'=>$after,'duplicate_site'=>WCS_Staging::is_duplicate_site(),'manual_renewal'=>$sub->is_manual(),'cron_empty'=>wp_get_ready_cron_jobs()===[],'async_disabled'=>apply_filters('action_scheduler_allow_async_request_runner',true)===false,'runner_removed'=>has_action('action_scheduler_run_queue')===false]);return;
}
throw new RuntimeException('UNKNOWN_A01_PHASE');
