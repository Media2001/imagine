<?php

declare(strict_types=1);

// Test doubles only; separate installed-source/native gate remains mandatory.
// Native Woo/WCS boundary names must match the installed API, not PSR class/method spelling.
// phpcs:disable PSR1.Files.SideEffects.FoundWithSymbols, PSR1.Classes.ClassDeclaration.MissingNamespace
// phpcs:disable PSR1.Classes.ClassDeclaration.MultipleClasses, Squiz.Classes.ValidClassName.NotCamelCaps
// phpcs:disable PSR1.Methods.CamelCapsMethodName.NotCamelCaps
class WC_Meta_Data
{
    public function __construct(private string $key, private mixed $value)
    {
    }
    public function get_data(): array
    {
        return ['key' => $this->key, 'value' => $this->value];
    }
}
class WC_Order
{
    public function __construct(private array $meta)
    {
    }
    public function get_meta(string $key, bool $single = true, string $context = 'view'): array
    {
        return array_values(array_filter($this->get_meta_data(), static fn ($m) => $m->get_data()['key'] === $key));
    }
    public function get_meta_data(): array
    {
        $result = [];
        foreach ($this->meta as $key => $values) {
            foreach ($values as $value) {
                $result[] = new WC_Meta_Data($key, $value);
            }
        }
        return $result;
    }
}
class WC_Subscription extends WC_Order
{
}
class WCS_Related_Order_Store
{
    public bool $alter = false;
    public function get_related_subscription_ids(WC_Order $order, string $type): array
    {
        if ($this->alter) {
            return [99];
        }
        return array_map(
            static fn ($m): int => abs((int) $m->get_data()['value']),
            $order->get_meta('_subscription_' . $type, false)
        );
    }
}
function wcs_get_subscription(int $id): WC_Subscription|false
{
    return $id === 7 ? new WC_Subscription([]) : false;
}
// phpcs:enable PSR1.Classes.ClassDeclaration, Squiz.Classes.ValidClassName, PSR1.Methods.CamelCapsMethodName
require '/subject/a31/Inventory.php';
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$store = new WCS_Related_Order_Store();
$read = static fn (array $m, bool $p = false): array =>
    Imagine\OrderHistory\Inventory::relations(new WC_Order($m), $store, $p);
$check('parent_native_relation', $read([], true)['nature'] === 'parent');
$check('standalone_not_default_for_opaque', $read([])['nature'] === 'none');
foreach (['renewal', 'switch', 'resubscribe'] as $type) {
    $check('native_relation_' . $type, $read(['_subscription_' . $type => ['7']])['nature'] === $type);
}
$check('renewal_missing_native_subscription', $read(['_subscription_renewal' => ['8']])['orphan_renewal']);
$check('existing_subscription_not_orphan', !$read(['_subscription_renewal' => ['7']])['orphan_renewal']);
foreach (['', '0', '-7', '7junk', 'A31_PRIVATE_CANARY', ['7'], '99999999999999999999999'] as $i => $value) {
    $check('malformed_' . $i, $read(['_subscription_renewal' => [$value]])['nature'] === 'illisible');
}
$check(
    'mixed_natures_illisible',
    $read(['_subscription_switch' => ['7'], '_subscription_renewal' => ['7']])['nature'] === 'illisible'
);
$check('parent_and_renewal_illisible', $read(['_subscription_renewal' => ['7']], true)['nature'] === 'illisible');
$check(
    'extension_relation_illisible',
    $read(['_subscription_stripe_subscription_id' => ['7']])['nature'] === 'illisible'
);
$store->alter = true;
$check('native_filter_contradiction_illisible', $read(['_subscription_renewal' => ['7']])['nature'] === 'illisible');
$code = (int) in_array('FAIL', array_column($checks, 'status'), true);
file_put_contents(
    '/report/adapter-unit.json',
    json_encode(['checks' => $checks, 'exit_code' => $code], JSON_PRETTY_PRINT) . "\n"
);
exit($code);
