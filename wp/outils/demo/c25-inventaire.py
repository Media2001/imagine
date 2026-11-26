"""Inventaire C25 limité aux objets fictifs et lecture native du raccord."""
import sys
sys.dont_write_bytecode = True
import json
import c25

c25.b06.guard()
print(json.dumps(c25.wp('''$out=[];foreach(wc_get_orders(['limit'=>100,'orderby'=>'date','order'=>'DESC','type'=>'shop_order']) as $o){$uid=(int)$o->get_customer_id();if($uid>0){$out[]=['id'=>$o->get_id(),'user'=>$uid,'paid'=>$o->get_date_paid()?->format('Y-m-d'),'open'=>Imagine\\Site\\Retractation::ouverte($o),'status'=>$o->get_status()];}}$subs=[];foreach(wcs_get_subscriptions(['subscriptions_per_page'=>100]) as $s){$subs[]=['id'=>$s->get_id(),'parent'=>$s->get_parent_id(),'user'=>$s->get_customer_id()];}global $wpdb;echo wp_json_encode(['orders'=>$out,'subs'=>$subs,'engines'=>$wpdb->get_results("SHOW TABLE STATUS WHERE Name IN ('{$wpdb->comments}','{$wpdb->commentmeta}','{$wpdb->options}')",ARRAY_A)]);'''), ensure_ascii=False))
