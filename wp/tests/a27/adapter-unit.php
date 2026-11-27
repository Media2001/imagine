<?php

declare(strict_types=1);

// Pure adapter boundary: real A-19 reader, only the native hook/subscription shell is doubled.
require '/subject/a19/Inventory.php';
require '/subject/a27/Analysis.php';
require '/subject/a27/Inventory.php';

use Imagine\SavedPayments\Analysis;
use Imagine\SavedPayments\Inventory;

require __DIR__ . '/SubscriptionDouble.php';
require __DIR__ . '/adapter-hooks.php';
class_alias(Imagine\Tests\SavedPayments\SubscriptionDouble::class, 'WC_Subscription');
$GLOBALS['a27_filters'] = [];

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$subscription = new WC_Subscription();
$schema = [];
$throws = false;
$calls = 0;
add_filter('woocommerce_subscription_payment_meta', static function () use (&$schema, &$calls, &$throws) {
    $calls++;
    if ($throws) {
        throw new RuntimeException('A27_TEST_SCHEMA_EXCEPTION');
    }
    return $schema;
}, 10);
try {
    $method = new ReflectionMethod(Inventory::class, 'paymentReference');
    foreach (
        [['opaque', ['private' => 'A27_OPAQUE_PRIVATE_CANARY'], 'unknown'],
        ['null', null, 'unknown'], ['empty', '', 'absent'], ['scalar', 'opaque-local-reference', 'present']]
        as [$name, $value, $expected]
    ) {
        $schema = ['ppcp-gateway' => ['post_meta' => ['opaque_field' => ['value' => $value]]]];
        $upstream = \Imagine\SubscriptionCoherence\Inventory::paymentReference($subscription);
        $check($name . '_actual_a19_boundary', $upstream === ($expected === 'unknown' ? 'absent' : $expected));
        $before = $GLOBALS['a27_filters'];
        $calls = 0;
        $reference = $method->invoke(null, $subscription);
        $check($name . '_adapted_presence', $reference === $expected);
        $check($name . '_one_schema_evaluation', $calls === 1);
        $check($name . '_observer_removed', $GLOBALS['a27_filters'] === $before);
        if ($name === 'opaque') {
            $row = ['user' => 1, 'status' => 'active', 'manual' => false, 'gateway' => 'ppcp-gateway',
                'tokens' => [], 'metadata' => [], 'reference' => $reference];
            $counts = Analysis::analyse(array_fill(0, 5, $row), [], '2026-11-26T12:00:00+00:00', false);
            $check('opaque_five_automatic_illisible', $counts['automatic'] === ['groups' => [
                ['gateway' => 'ppcp-gateway', 'type' => 'illisible', 'count' => 5]], 'autres' => 0]);
            $check('opaque_five_relation_unknown', $counts['relations'] === ['groups' => [
                ['gateway' => 'ppcp-gateway', 'metric' => 'subscriptions_link_unknown', 'count' => 5]], 'autres' => 0]);
        }
    }
    $before = $GLOBALS['a27_filters'];
    $throws = true;
    try {
        $method->invoke(null, $subscription);
        $check('schema_exception_propagated', false);
    } catch (RuntimeException $error) {
        $check('schema_exception_propagated', $error->getMessage() === 'A27_TEST_SCHEMA_EXCEPTION');
    }
    $check('observer_removed_after_exception', $GLOBALS['a27_filters'] === $before);
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'detail' => get_class($error)];
}
$result = ['suite' => 'A27-adapter-pure', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/adapter-unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
echo 'A27_ADAPTER_UNIT ' . count($checks) . "\n";
exit($result['exit_code']);
