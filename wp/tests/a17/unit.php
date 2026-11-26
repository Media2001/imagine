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
    foreach (
        ['edit_users', 'update_plugins', 'switch_themes', 'delete_plugins', 'delete_themes',
        'install_themes', 'update_themes', 'edit_theme_options', 'export', 'import', 'remove_users'] as $cap
    ) {
        $check('isolated_management:' . $cap, $class::management(['read' => true, $cap => true]));
        $check('disabled_management:' . $cap, !$class::management(['read' => true, $cap => false]));
    }
    $check('content_only_excluded', !$class::management(['read' => true, 'edit_posts' => true,
        'publish_posts' => true, 'upload_files' => true, 'delete_posts' => true]));
    $check('manage_prefix_stays_inclusive', $class::management(['manage_categories' => true]));
    $check('subscriber_not_management', !$class::management(['read' => true, 'manage_options' => false]));
    $check('literal_config_not_executed', $class::configBoolean(
        "<?php define('DISALLOW_FILE_EDIT', true);",
        'DISALLOW_FILE_EDIT'
    ) === true);
    $check('literal_false', $class::configBoolean(
        "<?php define('DISALLOW_FILE_EDIT', false);",
        'DISALLOW_FILE_EDIT'
    ) === false);
    $check('expression_is_unknown', $class::configBoolean(
        "<?php define('DISALLOW_FILE_EDIT', getenv('X'));",
        'DISALLOW_FILE_EDIT'
    ) === null);
    $check('conditional_definition_unknown', $class::configBoolean(
        "<?php if (false) { define('DISALLOW_FILE_EDIT', true); }",
        'DISALLOW_FILE_EDIT'
    ) === null);
    foreach (
        [
        "if (false): ; define('DISALLOW_FILE_EDIT', true); endif;",
        "foreach ([] as \$x): ; define('DISALLOW_FILE_EDIT', true); endforeach;",
        "while (false): ; define('DISALLOW_FILE_EDIT', true); endwhile;",
        "switch (0): case 1: ; define('DISALLOW_FILE_EDIT', true); endswitch;",
        "if (false) ; define('DISALLOW_FILE_EDIT', true);",
        "return; define('DISALLOW_FILE_EDIT', true);",
        "function fixture() { ; define('DISALLOW_FILE_EDIT', true); }",
        ] as $index => $statement
    ) {
        $check(
            'non_demonstrated_context_unknown:' . $index,
            $class::configBoolean('<?php ' . $statement, 'DISALLOW_FILE_EDIT') === null
        );
    }
    $check('absent_constant_false_default', $class::configBoolean('<?php // nothing', 'DISALLOW_FILE_EDIT') === false);
    $check('leap_day_calendar_convention', (new DateTimeImmutable('2024-02-29T12:00:00Z'))
        ->modify('-12 months')->format('Y-m-d\\TH:i:s\\Z') === '2023-03-01T12:00:00Z');
}
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
