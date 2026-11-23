<?php

declare(strict_types=1);

namespace Imagine\Audit\Tests;

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
        check('serialized_object_never_instantiated', \Imagine\Audit\Audit::decode('O:8:"stdClass":0:{}') === []);
        check('version_only', \Imagine\Audit\Audit::version('11.1.1') === '11.1.1' && \Imagine\Audit\Audit::version('private@example.org') === null);
    } else {
        check('config_literal_without_execution', false);
    }
}
file_put_contents('/report/unit.json', json_encode(['checks' => $checks], JSON_PRETTY_PRINT) . "\n");
echo json_encode($checks) . "\n";
exit(count(array_filter($checks, static fn(array $c): bool => $c['status'] === 'FAIL')) > 0 ? 1 : 0);
