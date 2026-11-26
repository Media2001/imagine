<?php

declare(strict_types=1);

$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
}
$file = '/subject/a11/Address.php';
check('address_engine_exists', is_file($file));
if (is_file($file)) {
    require $file;
    $f = [Imagine\PublicAddresses\Address::class, 'relative'];
    foreach (['https://fixture.test/sub/a/%7e/%c3%a9/?x=%2f&x=+' => '/sub/a/~/%C3%A9/?x=%2f&x=+', 'https://fixture.test/?p=12' => '/?p=12', 'https://fixture.test/' => '/'] as $input => $expected) {
        check('relative:' . $expected, $f($input, 'https://fixture.test/sub') === $expected);
    }
    foreach (['https://evil.test/a', 'https://fixture.test/a?', 'https://fixture.test/a#x', 'https://fixture.test/a%2fb', 'https://fixture.test/../b', 'https://fixture.test/é', 'https://fixture.test//evil', 'https://fixture.test/a%0ab', 'https://fixture.test/a?x=%zz'] as $input) {
        try {
            $f($input, 'https://fixture.test');
            check('refused:' . $input, false);
        } catch (RuntimeException $error) {
            check('refused:' . $input, $error->getMessage() === 'A11_URL_NOT_A09_COMPATIBLE');
        }
    }
}
require '/subject/a11/Runtime.php';
foreach (["define('WPMU_PLUGIN_DIR','/fiction/custom-mu');", "define('WP_PLUGIN_URL','https://fiction.invalid/plugins');", "define('FICTION_PATH_OVERRIDE','/fiction');", "const WPMU_PLUGIN_DIR = '/fiction/custom-mu';"] as $declaration) {
    try {
        Imagine\PublicAddresses\Runtime::validateConfiguration('<?php ' . $declaration);
        check('unknown-layout-refused:' . substr($declaration, 8, 20), false);
    } catch (Throwable $error) {
        check('unknown-layout-refused:' . substr($declaration, 8, 20), $error instanceof RuntimeException && $error->getMessage() === 'A11_CONFIG_OVERRIDE_UNSUPPORTED');
    }
}
try {
    Imagine\PublicAddresses\Runtime::validateConfiguration("<?php define('DB_NAME','fiction'); define('AUTH_KEY','FICTION_SECRET'); define('WP_DEBUG',false);");
    check('ordinary-known-config-accepted', true);
} catch (Throwable) {
    check('ordinary-known-config-accepted', false);
}
class wpdb
{
    public string $last_error = '';
    public function query($query) { $this->last_error = 'FICTION_SELECT_DENIED'; return false; }
}
require '/subject/a11/ReadOnlyDb.php';
$db = (new ReflectionClass(Imagine\PublicAddresses\ReadOnlyDb::class))->newInstanceWithoutConstructor();
$fenced = new ReflectionProperty(Imagine\PublicAddresses\ReadOnlyDb::class, 'fenced');
$fenced->setValue($db, true);
try {
    $db->query('SELECT ID FROM wp_posts');
    check('failed-select-is-not-empty-result', false);
} catch (Throwable $error) {
    check('failed-select-is-not-empty-result', $error instanceof RuntimeException && $error->getMessage() === 'A11_READ_FAILED');
}
file_put_contents('/report/unit.json', json_encode(['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)], JSON_PRETTY_PRINT) . "\n");
foreach ($checks as $check) {
    echo $check['status'] . ' ' . $check['check'] . "\n";
}
exit((int) in_array('FAIL', array_column($checks, 'status'), true));
