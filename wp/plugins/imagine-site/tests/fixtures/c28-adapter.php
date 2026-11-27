<?php

declare(strict_types=1);

// Isolated, persisted lightweight Woo doubles; no WordPress, site or network.
$GLOBALS['hooks'] = $GLOBALS['products'] = $GLOBALS['orders'] = $GLOBALS['posts'] = [];
$GLOBALS['notices'] = [];
function add_action($hook, $callback, $priority = 10, $accepted = 1) { $GLOBALS['hooks'][$hook][$priority][] = [$callback, $accepted]; }
function add_filter($hook, $callback, $priority = 10, $accepted = 1) { add_action($hook, $callback, $priority, $accepted); }
function do_action($hook, ...$args) { $ps = $GLOBALS['hooks'][$hook] ?? []; ksort($ps); foreach ($ps as $rows) { foreach ($rows as [$cb, $n]) { $cb(...array_slice($args, 0, $n)); } } }
function apply_filters($hook, $value, ...$args) { $ps = $GLOBALS['hooks'][$hook] ?? []; ksort($ps); foreach ($ps as $rows) { foreach ($rows as [$cb, $n]) { $value = $cb(...array_slice([$value, ...$args], 0, $n)); } } return $value; }
function get_post($id) { return $GLOBALS['posts'][$id] ?? null; }
function wc_get_product($id) { $GLOBALS['product_reads'] = ($GLOBALS['product_reads'] ?? 0) + 1; return isset($GLOBALS['products'][$id]) ? clone $GLOBALS['products'][$id] : false; }
function wc_add_notice($text, $type) { $GLOBALS['notices'][] = [$text, $type]; }
function __($text, $domain = '') { return $text; }
function current_user_can(...$args) { return true; }
function wp_unslash($v) { return is_array($v) ? array_map('wp_unslash', $v) : (is_string($v) ? stripslashes($v) : $v); }
function WC() { return $GLOBALS['wc']; }
class WC_Product {
    public array $meta = [];
    public function __construct(public int $id = 42) {}
    public function get_id() { return $this->id; }
    public function is_type($t) { return $t === 'simple'; }
    public function get_status() { return 'publish'; }
    public function get_meta($k, ...$args) { return $this->meta[$k] ?? ''; }
    public function meta_exists($k) { return array_key_exists($k, $this->meta); }
    public function add_meta_data($k, $v, $unique = false) { $this->meta[$k] = $v; }
    public function update_meta_data($k, $v) { $this->meta[$k] = $v; }
    public function delete_meta_data($k) { unset($this->meta[$k]); }
    public function save() { $GLOBALS['products'][$this->id] = clone $this; }
}
class WC_Order_Item_Product extends WC_Product {
    public static bool $fail = false;
    public function __construct(public int $id = 0, public int $product = 42, public int $order = 77) {}
    public function get_product() { return wc_get_product($this->product); }
    public function get_product_id() { return $this->product; }
    public function get_order_id() { return $this->order; }
    public function get_order() { return new WC_Order($this->order); }
    public function save() {
        do_action('woocommerce_before_order_item_object_save', $this);
        if (self::$fail) { throw new RuntimeException('post-payment item persistence failure'); }
        $this->id = $this->id ?: 101;
        $GLOBALS['orders'][$this->order]['items'][$this->id] = unserialize(serialize($this));
    }
}
class WC_Order {
    public bool $paid = false;
    public ?DateTimeImmutable $date = null;
    public array $items = [];
    public function __construct(public int $id = 77) {
        if (isset($GLOBALS['orders'][$id])) {
            $s = unserialize(serialize($GLOBALS['orders'][$id]));
            $this->paid = $s['paid'] ?? false; $this->date = $s['date'] ?? null; $this->items = $s['items'];
        }
    }
    public function get_id() { return $this->id; }
    public function get_type() { return 'shop_order'; }
    public function get_date_paid(...$args) { return $this->date; }
    public function is_paid() { return $this->paid; }
    public function get_items(...$args) { return $this->items; }
    public function add_order_note($note) { $GLOBALS['notes'][] = $note; }
    public function save() {
        do_action('woocommerce_before_order_object_save', $this);
        $GLOBALS['orders'][$this->id] = unserialize(serialize(['paid' => $this->paid, 'date' => $this->date, 'items' => $this->items]));
        do_action('woocommerce_after_order_object_save', $this);
    }
}
require dirname(__DIR__, 2) . '/PacksRegles.php';
require dirname(__DIR__, 2) . '/AchatsNumeros.php';
require dirname(__DIR__, 2) . '/PacksThematiques.php';
use Imagine\Site\PacksThematiques as P;
use Imagine\Site\AchatsNumeros as A;
P::register();
$checks = [];
$check = static function ($name, $ok) use (&$checks) { $checks[$name] = (bool) $ok; };
foreach ([11, 18, 25, 32] as $id) { $GLOBALS['posts'][$id] = (object) ['post_type' => 'imagine_numero', 'post_status' => 'publish']; }
$p = new WC_Product(); $p->update_meta_data(P::PRODUIT, [11, 18, 25]); $p->save();
$i = new WC_Order_Item_Product(); P::candidat($i);
$check('candidate_new_pack', (string) $i->get_meta(P::CANDIDAT) === '1');
$old = new WC_Order_Item_Product(999); P::candidat($old);
$check('candidate_legacy_not_retroactive', !$old->meta_exists(P::CANDIDAT));
$check('valid_pack_purchasable', apply_filters('woocommerce_is_purchasable', true, $p) === true);
$GLOBALS['posts'][18]->post_status = 'draft';
$check('direct_add_invalid_refused', apply_filters('woocommerce_add_to_cart_validation', true, 42, 1) === false);
$check('native_product_not_purchasable', apply_filters('woocommerce_is_purchasable', true, $p) === false);
$GLOBALS['wc'] = (object) ['cart' => new class($p) {
    public function __construct(public $p) {}
    public function get_cart() { return [['product_id' => 42, 'data' => $this->p]]; }
}];
$GLOBALS['notices'] = []; do_action('woocommerce_check_cart_items');
$check('existing_cart_checkout_refused', count($GLOBALS['notices']) > 0);
$invalid = new WC_Order(90); $invalidLine = new WC_Order_Item_Product(0, 42, 90); $invalidLine->save();
$invalid->items = [101 => $invalidLine]; $invalid->save();
$invalid->paid = true; $invalid->date = new DateTimeImmutable('@1234567880');
$refused = false;
try { $invalid->save(); } catch (RuntimeException $e) { $refused = str_contains($e->getMessage(), 'pack indisponible'); }
$check('invalid_payment_persistence_refused', $refused && !(new WC_Order(90))->is_paid());
$check('upstream_refusal_preserved', apply_filters('woocommerce_add_to_cart_validation', false, 42, 1) === false);
$GLOBALS['posts'][18]->post_status = 'publish';
$check('valid_direct_add_allowed', apply_filters('woocommerce_add_to_cart_validation', true, 42, 1) === true);
$ordinary = new WC_Product(43); $ordinary->save();
$check('ordinary_product_unchanged', apply_filters('woocommerce_is_purchasable', true, $ordinary) === true);
$i->save(); $o = new WC_Order(); $o->items = [101 => $i]; $o->save();
$check('pending_no_snapshot', !$o->items[101]->meta_exists(P::LIGNE));
$p->update_meta_data(P::PRODUIT, [11, 18, 32]); $p->save();
$o->paid = true; $o->date = new DateTimeImmutable('@1234567890'); $o->save();
$o = new WC_Order(); $i = $o->items[101]; $snapshot = $i->get_meta(P::LIGNE);
$check('first_payment_not_cart_composition', ($snapshot['numeros'] ?? null) === [11, 18, 32]);
$check('payment_timestamp', ($snapshot['paye_le'] ?? null) === 1234567890);
$check('expansion_same_line', P::instantanes([0], $i) === [11, 18, 32]);
$p->update_meta_data(P::PRODUIT, [18, 25, 32]); $p->save(); $o->save();
$o = new WC_Order(); $i = $o->items[101];
$check('reloaded_paid_immutable', $i->get_meta(P::LIGNE) === $snapshot);
$check('expansion_does_not_read_live_product', P::instantanes([0], $i) === [11, 18, 32]);
// Exact fault window: order paid state persisted, but line save throws.
$o2 = new WC_Order(78); $i2 = new WC_Order_Item_Product(0, 42, 78); $i2->save(); $o2->items = [101 => $i2]; $o2->save();
WC_Order_Item_Product::$fail = true; $o2->paid = true; $o2->date = new DateTimeImmutable('@1234567891');
try { $o2->save(); } catch (RuntimeException $e) { $check('real_fault_after_order_persisted', $e->getMessage() === 'post-payment item persistence failure'); }
WC_Order_Item_Product::$fail = false;
$o2 = new WC_Order(78);
$check('fault_paid_reloaded_without_snapshot', $o2->is_paid() && !$o2->items[101]->meta_exists(P::LIGNE));
$p->update_meta_data(P::PRODUIT, [11, 25]); $p->save();
$GLOBALS['product_reads'] = 0; $o2->save(); $o2 = new WC_Order(78);
$check('late_save_never_reads_current_product', $GLOBALS['product_reads'] === 0);
$check('late_missing_stays_closed', P::instantanes([0], $o2->items[101]) === []);
$check('late_missing_not_rebuilt', !$o2->items[101]->meta_exists(P::LIGNE));
$check('late_missing_signalled', $o2->items[101]->meta_exists('imagine_pack_anomalie'));
$historical = new WC_Order(79); $historicalLine = new WC_Order_Item_Product(0, 42, 79); $historicalLine->save();
$historical->items = [101 => $historicalLine]; $historical->paid = true; $historical->save();
$historical = new WC_Order(79); $historical->date = new DateTimeImmutable('@1234567892'); $historical->save();
$historical = new WC_Order(79);
$check('already_paid_missing_date_never_reconstructed', !$historical->items[101]->meta_exists(P::LIGNE) && $historical->items[101]->meta_exists(P::ANOMALIE));
// Malformed and mismatched paid envelopes cannot be repaired or expanded.
foreach ([['broken'], ['numeros' => [32], 'paye_le' => 1234567890, 'produit' => 999], ['numeros' => [32], 'paye_le' => 1234567899, 'produit' => 42]] as $bad) {
    $i = $o->items[101]; $i->delete_meta_data(P::ANOMALIE); $i->update_meta_data(P::LIGNE, $bad); $i->save(); $o = new WC_Order();
    $check('unreliable_closed_before_save_' . count($checks), P::instantanes([0], $o->items[101]) === []);
    $o->save(); $o = new WC_Order();
    $check('unreliable_' . count($checks), P::instantanes([0], $o->items[101]) === [] && $o->items[101]->meta_exists('imagine_pack_anomalie'));
}
$_POST = [A::PRODUIT => '11']; $p->update_meta_data(P::PRODUIT, [11, 18]); A::enregistrer($p);
$check('single_issue_unlinks_pack_partial_form', !$p->meta_exists(P::PRODUIT) && $p->get_meta(A::PRODUIT) === 11);
$_POST = [];
echo json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => count(array_filter($checks, static fn ($v) => !$v))], JSON_THROW_ON_ERROR);
exit(in_array(false, $checks, true) ? 1 : 0);
