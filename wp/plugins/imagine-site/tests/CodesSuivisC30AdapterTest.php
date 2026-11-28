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
    public function testStoreApiCandidatSurHookNatifPuisScelle():void
    {
        CodesSuivis::register();CodesSuivis::retenir('fictif');
        $o=new \WC_Order(id:9,via:'store-api',paid:false);
        CodesSuivis::candidat($o,[]);
        self::assertSame('fictif',$o->get_meta(CodesSuivis::CANDIDAT)['code']??null);
        self::assertArrayHasKey('woocommerce_store_api_checkout_order_processed',$GLOBALS['c30_hooks']);
        $o->meta=[];
        foreach($GLOBALS['c30_hooks']['woocommerce_store_api_checkout_order_processed'] as [$callback]){$callback($o);}
        self::assertSame('fictif',$GLOBALS['c30_orders'][9]->get_meta(CodesSuivis::CANDIDAT)['code']);
        $GLOBALS['c30_orders'][9]->paid=true;CodesSuivis::payer(9);
        self::assertSame('fictif',$GLOBALS['c30_orders'][9]->get_meta(CodesSuivis::META)['code']);
    }
    public function testSessionEtCandidatRevalidationSansEcrasement():void
    {
        CodesSuivis::retenir('inconnu');self::assertNull($GLOBALS['c30_woo']->session);
        CodesSuivis::retenir('fictif');self::assertSame(1,$GLOBALS['c30_woo']->session->cookies);
        CodesSuivis::retenir('inconnu');self::assertSame('fictif',$GLOBALS['c30_woo']->session->get(CodesSuivis::SESSION)['code']);
        $o=new \WC_Order();CodesSuivis::candidat($o,[]);self::assertSame('FICTIF \\ Test',$o->get_meta(CodesSuivis::CANDIDAT)['libelle']);
        CodesSuivis::retenir('autre');CodesSuivis::candidat($o,[]);self::assertSame('fictif',$o->get_meta(CodesSuivis::CANDIDAT)['code']);
        $new=new \WC_Order(id:2);$GLOBALS['c30_options'][CodesSuivis::OPTION]=[];CodesSuivis::candidat($new,[]);self::assertSame([],$new->meta);
        $admin=new \WC_Order(via:'imagine-c16');CodesSuivis::candidat($admin,[]);self::assertSame([],$admin->meta);
    }
    public function testPaiementScelleUniqueVerrouEtEffacementNonRecree():void
    {
        CodesSuivis::retenir('fictif');$o=new \WC_Order(paid:false);CodesSuivis::candidat($o,[]);$GLOBALS['c30_orders'][1]=clone $o;
        CodesSuivis::payer(1);self::assertFalse($GLOBALS['c30_orders'][1]->meta_exists(CodesSuivis::META));
        $GLOBALS['c30_orders'][1]->paid=true;$GLOBALS['wpdb']->locked=false;CodesSuivis::payer(1);self::assertFalse($GLOBALS['c30_orders'][1]->meta_exists(CodesSuivis::META));
        $GLOBALS['wpdb']->locked=true;CodesSuivis::payer(1);self::assertSame('fictif',$GLOBALS['c30_orders'][1]->get_meta(CodesSuivis::META)['code']);self::assertSame('1',$GLOBALS['c30_orders'][1]->get_meta(CodesSuivis::SCELLE));
        self::assertFalse($GLOBALS['c30_orders'][1]->meta_exists(CodesSuivis::CANDIDAT));
        CodesSuivis::retenir('autre');CodesSuivis::payer(1);self::assertSame(1,$GLOBALS['c30_orders'][1]->saves);
        CodesSuivisConfidentialite::effacer('lecteur@example.org');CodesSuivis::payer(1);self::assertFalse($GLOBALS['c30_orders'][1]->meta_exists(CodesSuivis::META));
        self::assertStringContainsString('RELEASE_LOCK',end($GLOBALS['wpdb']->calls)[0]);
    }
    public function testCompteurHistoriqueDatesEtLectureEnEchec():void
    {
        $this->order(1);$this->order(2)->day='2026-11-29';$this->order(3)->paid=false;
        $GLOBALS['c30_options'][CodesSuivis::OPTION]=[];
        self::assertSame(['fictif'=>1],CodesSuivis::compter('2026-11-28','2026-11-28'));
        self::assertInstanceOf(\WP_Error::class,CodesSuivis::compter('2026-02-30','2026-03-01'));
        $GLOBALS['c30_read_fail']=true;self::assertInstanceOf(\WP_Error::class,CodesSuivis::compter('2026-11-28','2026-11-28'));
    }
    public function testPaginationStableUnionPuisEffacementSansSaut():void
    {
        for($id=1;$id<=102;$id++){$this->order($id,$id%2?28:0);}
        $this->order(103,29);$third=$GLOBALS['c30_orders'][103]->meta;
        $ids=[];
        foreach([1,2,3] as $page){$r=CodesSuivisConfidentialite::exporter('lecteur@example.org',$page);self::assertCount($page===3?2:50,$r['data']);self::assertSame($page===3,$r['done']);foreach($r['data'] as $row){$ids[]=$row['item_id'];}}
        self::assertCount(102,array_unique($ids));
        foreach([1,2,3] as $page){$r=CodesSuivisConfidentialite::effacer('lecteur@example.org',$page);self::assertSame($page===3,$r['done']);self::assertFalse($r['items_retained']);}
        for($id=1;$id<=102;$id++){self::assertFalse($GLOBALS['c30_orders'][$id]->meta_exists(CodesSuivis::META));}
        self::assertSame($third,$GLOBALS['c30_orders'][103]->meta);
    }
    public function testPannesLectureVerrouEtPersistanceRestentIncompletes():void
    {
        $this->order(1);$GLOBALS['c30_read_fail']=true;
        self::assertInstanceOf(\WP_Error::class,CodesSuivisConfidentialite::exporter('lecteur@example.org'));
        $r=CodesSuivisConfidentialite::effacer('lecteur@example.org');self::assertTrue($r['items_retained']);self::assertFalse($r['done']);
        $GLOBALS['c30_read_fail']=false;$GLOBALS['wpdb']->locked=false;$r=CodesSuivisConfidentialite::effacer('lecteur@example.org');self::assertTrue($r['items_retained']);self::assertFalse($r['done']);
        $GLOBALS['wpdb']->locked=true;$GLOBALS['c30_save_fail']=true;$r=CodesSuivisConfidentialite::effacer('lecteur@example.org');self::assertTrue($r['items_retained']);self::assertFalse($r['done']);self::assertFalse($r['items_removed']);
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
