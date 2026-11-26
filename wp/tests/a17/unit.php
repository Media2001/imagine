<?php

declare(strict_types=1);

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$check('implementation_present', is_file('/subject/a17/Inventory.php'));
if (is_file('/subject/a17/Inventory.php')) {
    require '/subject/a17/Inventory.php';
    $class = \Imagine\AccountSecurity\Inventory::class;
    $check('native_admin_capability', $class::management(['manage_options' => true]));
    $check('custom_management_capability', $class::management(['manage_imagine' => true]));
    $check('editor_capability', $class::management(['edit_others_posts' => true]));
    $check('subscriber_not_management', !$class::management(['read' => true, 'manage_options' => false]));
    $check('literal_config_not_executed', $class::configBoolean("<?php define('DISALLOW_FILE_EDIT', true);", 'DISALLOW_FILE_EDIT') === true);
    $check('literal_false', $class::configBoolean("<?php define('DISALLOW_FILE_EDIT', false);", 'DISALLOW_FILE_EDIT') === false);
    $check('expression_is_unknown', $class::configBoolean("<?php define('DISALLOW_FILE_EDIT', getenv('X'));", 'DISALLOW_FILE_EDIT') === null);
    $check('absent_constant_false_default', $class::configBoolean('<?php // nothing', 'DISALLOW_FILE_EDIT') === false);
}
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
