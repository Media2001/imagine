<?php

declare(strict_types=1);

namespace {
    final class WP_Error { public function __construct(public string $code='',public string $message=''){} }
    final class WC_Order
    {
        public array $meta=[];
        public int $saves=0;
        public function __construct(public int $id=1,public int $customer=28,public string $email='lecteur@example.org',public string $via='checkout',public bool $paid=true,public string $day='2026-11-28'){}
        public function get_id():int{return $this->id;}
        public function get_type():string{return 'shop_order';}
        public function get_customer_id():int{return $this->customer;}
        public function get_created_via():string{return $this->via;}
        public function is_paid():bool{return $this->paid;}
        public function get_date_paid():?DateTimeImmutable{return $this->paid?new DateTimeImmutable($this->day.'T12:00:00Z'):null;}
        public function get_meta(string $k):mixed{return $this->meta[$k]??'';}
        public function meta_exists(string $k):bool{return array_key_exists($k,$this->meta);}
        public function update_meta_data(string $k,mixed $v):void{$this->meta[$k]=$v;}
        public function delete_meta_data(string $k):void{unset($this->meta[$k]);}
        public function save_meta_data():void{if($GLOBALS['c30_save_fail']){return;}$this->saves++;$GLOBALS['c30_orders'][$this->id]=clone $this;}
    }
}
namespace Imagine\Site {
    const DB_NAME='fictif';
    function __(string $s,string $domain=''):string{return $s;}
    function is_email(string $s):bool{return filter_var($s,FILTER_VALIDATE_EMAIL)!==false;}
    function get_option(string $k,mixed $d=false):mixed{return $GLOBALS['c30_options'][$k]??$d;}
    function get_user_by(string $field,string $email):object|false{return $email==='lecteur@example.org'?(object)['ID'=>28]:false;}
    function wc_get_order(int $id):\WC_Order|false{return isset($GLOBALS['c30_orders'][$id])?clone $GLOBALS['c30_orders'][$id]:false;}
    function wc_get_orders(array $args):array{
        global $wpdb;$GLOBALS['c30_queries'][]=$args;
        if($GLOBALS['c30_read_fail']){$wpdb->last_error='FICTIF';return [];}
        $out=array_filter($GLOBALS['c30_orders'],static function($o) use($args){
            return (!isset($args['customer_id']) || $o->customer===(int)$args['customer_id'])
                && (!isset($args['billing_email']) || $o->email===$args['billing_email'])
                && (!isset($args['status']) || $o->paid);
        });ksort($out,SORT_NUMERIC);$out=array_values(array_slice($out,(($args['page']??1)-1)*($args['limit']??50),$args['limit']??50));
        return ($args['return']??'objects')==='ids'?array_map(static fn($o)=>$o->id,$out):array_map(static fn($o)=>clone $o,$out);
    }
    function WC():object{return $GLOBALS['c30_woo'];}
    function add_action(string $name,mixed $cb,int $priority=10,int $args=1):void{$GLOBALS['c30_hooks'][$name][]=[$cb,$priority,$args];}
    function add_shortcode(string $name,mixed $cb):void{}
}
