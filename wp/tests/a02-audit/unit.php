<?php

declare(strict_types=1);

namespace Imagine\Audit\Tests;

final class WakeCanary
{
    public static bool $woke = false;

    public function __wakeup(): void
    {
        self::$woke = true;
    }
}

$subject = '/subject/audit';
$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
check('audit_entrypoint_exists', is_file($subject));
if (is_file($subject)) {
    define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
    require $subject;
    check('identifier_preserved', \Imagine\Audit\Audit::identifier('woocommerce/woocommerce.php') === 'woocommerce/woocommerce.php');
    check('identifier_email_redacted', \Imagine\Audit\Audit::identifier('person@example.org') === '[masque]');
    check('identifier_markup_redacted', \Imagine\Audit\Audit::identifier('<script>') === '[masque]');
    check('identifier_traversal_redacted', \Imagine\Audit\Audit::identifier('../wp-config.php') === '[masque]');
    check('identifier_token_redacted', \Imagine\Audit\Audit::identifier('sk_live_FICTIONAL_PRIVATE_VALUE') === '[masque]');
    $literal = "<?php define('DB_NAME', 'fixture'); define('DB_USER', 'audit'); define('DB_PASSWORD', ''); define('DB_HOST', 'localhost:/scratch/db.sock'); \$table_prefix = 'abc_'; require 'never-execute.php';";
    if (method_exists(\Imagine\Audit\Audit::class, 'config')) {
        $config = \Imagine\Audit\Audit::config($literal);
        check('config_literal_without_execution', $config['DB_NAME'] === 'fixture' && $config['table_prefix'] === 'abc_');
        try {
            \Imagine\Audit\Audit::config(str_replace("'fixture'", "getenv('UNSAFE')", $literal));
            check('config_dynamic_refused', false);
        } catch (\RuntimeException $e) {
            check('config_dynamic_refused', $e->getMessage() === 'A02_CONFIG_NON_LITERAL');
        }
        try {
            \Imagine\Audit\Audit::config(str_replace("define('DB_NAME'", "if (false) define('DB_NAME'", $literal));
            check('config_conditional_refused', false);
        } catch (\RuntimeException $e) {
            check('config_conditional_refused', $e->getMessage() === 'A02_CONFIG_NON_LITERAL');
        }
        check('serialized_object_never_instantiated', \Imagine\Audit\Audit::decode('O:8:"stdClass":0:{}') === []);
        check('version_only', \Imagine\Audit\Audit::version('11.1.1') === '11.1.1' && \Imagine\Audit\Audit::version('private@example.org') === null);
        $gateway = '<?php class Gateway extends WC_Payment_Gateway { const ID = "bacs"; function x() { $this->id = self::ID; } }';
        check('gateway_literal_constant', \Imagine\Audit\Audit::gatewayIds($gateway) === ['bacs']);
        check('nongateway_id_ignored', \Imagine\Audit\Audit::gatewayIds('<?php class Hook { function x(WC_Payment_Gateway $g) { $this->id = "not_a_gateway"; } }') === []);
        $gatewaySources = [
            'base.php' => '<?php namespace A02; abstract class Base extends \\WC_Payment_Gateway { const ID = "indirect"; }',
            'child.php' => '<?php namespace A02; class Concrete extends Base { function x() { $this->id = self::ID; } } class Unrelated { function x() { $this->id = "not_gateway"; } }',
            'override.php' => '<?php abstract class KnownBase extends WC_Payment_Gateway { function x() { $this->id = "base_known"; } } class DynamicChild extends KnownBase { function x() { $this->id = getenv("NO_EXECUTE"); } }',
            'empty.php' => '<?php class EmptyGateway extends WC_Payment_Gateway {}',
            'dynamic.php' => '<?php class DynamicGateway extends WC_Payment_Gateway { function x() { $this->id = getenv("NO_EXECUTE"); } } class MissingGateway extends MissingBase { function x() { $this->id = "uncertain"; } }',
        ];
        $inventory = method_exists(\Imagine\Audit\Audit::class, 'gatewayInventory')
            ? \Imagine\Audit\Audit::gatewayInventory($gatewaySources) : ['ids' => [], 'unresolved' => []];
        check('gateway_indirect_cross_file_inherited_constant', $inventory['ids'] === ['base_known', 'indirect']);
        check('gateway_unresolved_explicit', count($inventory['unresolved']) === 4);
        \Imagine\Audit\Audit::decode(serialize(['nested' => new WakeCanary()]));
        check('nested_object_magic_not_called', WakeCanary::$woke === false);
        check('malformed_serialization_empty', \Imagine\Audit\Audit::decode('not serialized') === []);
    } else {
        check('config_literal_without_execution', false);
    }
}
file_put_contents('/report/unit.json', json_encode(['checks' => $checks], JSON_PRETTY_PRINT) . "\n");
echo json_encode($checks) . "\n";
exit(count(array_filter($checks, static fn(array $c): bool => $c['status'] === 'FAIL')) > 0 ? 1 : 0);
