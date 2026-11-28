<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\CodesSuivis;
use Imagine\Site\CodesSuivisConfidentialite;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class CodesSuivisC30AdapterTest extends TestCase
{
    protected function setUp():void
    {
        require __DIR__.'/CodesSuivisC30Stubs.php';
        $GLOBALS['c30_options']=[CodesSuivis::OPTION=>['fictif'=>'FICTIF \\ Test','autre'=>'AUTRE']];
        $GLOBALS['c30_orders']=[];$GLOBALS['c30_queries']=[];$GLOBALS['c30_hooks']=[];
        $GLOBALS['c30_read_fail']=false;$GLOBALS['c30_save_fail']=false;
        $GLOBALS['c30_woo']=new class {
            public ?object $session=null;
            public function initialize_session():void{$this->session=new class {
                public array $data=[];public int $cookies=0;
                public function set(string $k,mixed $v):void{$this->data[$k]=$v;}
                public function get(string $k):mixed{return $this->data[$k]??null;}
                public function set_customer_session_cookie(bool $set):void{$this->cookies+=(int)$set;}
            };}
        };
        $GLOBALS['wpdb']=new class {
            public string $last_error='';public string $prefix='fictif_';public bool $locked=true;public array $calls=[];
            public function prepare(string $q,mixed ...$args):array{return [$q,$args];}
            public function get_var(array $q):int{$this->calls[]=$q;return str_contains($q[0],'GET_LOCK')?(int)$this->locked:1;}
        };
    }
    private function order(int $id,int $customer=28,string $email='lecteur@example.org'): \WC_Order
    {
        $o=new \WC_Order($id,$customer,$email);$o->meta[CodesSuivis::META]=['code'=>'fictif','libelle'=>'FICTIF \\ Test'];
        return $GLOBALS['c30_orders'][$id]=$o;
    }
    public function testUnionCompteInviteEtTiersPreserve():void
    {
        $this->order(1);$this->order(2,0);$third=$this->order(3,0,'tiers@example.org');
        $expected=$third->meta;
        $export=CodesSuivisConfidentialite::exporter('lecteur@example.org');
        self::assertCount(2,$export['data']);self::assertTrue($export['done']);
        self::assertSame('FICTIF \\ Test',$export['data'][1]['data'][1]['value']);
        $erase=CodesSuivisConfidentialite::effacer('lecteur@example.org');
        self::assertTrue($erase['done']);self::assertTrue($erase['items_removed']);self::assertFalse($erase['items_retained']);
        self::assertArrayNotHasKey(CodesSuivis::META,$GLOBALS['c30_orders'][1]->meta);
        self::assertArrayNotHasKey(CodesSuivis::META,$GLOBALS['c30_orders'][2]->meta);
        self::assertSame($expected,$GLOBALS['c30_orders'][3]->meta);
    }
}
