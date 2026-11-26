<?php

declare(strict_types=1);

namespace Imagine\ContentInventory\Tests;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};

require '/subject/a12/AuditLibrary.php';
\Imagine\ContentInventory\AuditLibrary::load();
require '/subject/a12/Registry.php';
$root = '/unit-origin-fixture';
foreach (
    [
    'wp-includes/post.php' => 'core',
    'wp-content/plugins/synthetic/vendor/registrar.php' => 'plugin',
    'wp-content/themes/synthetic/functions.php' => 'theme',
    'wp-content/mu-plugins/submodule/registrar.php' => 'mu_plugin',
    ] as $file => $owner
) {
    mkdir(dirname($root . '/' . $file), 0700, true);
    file_put_contents($root . '/' . $file, '<?php');
    $check('real_origin:' . $owner, \Imagine\ContentInventory\Registry::origin($root, $root . '/' . $file)
        === ['owner' => $owner, 'file' => $file]);
}
$unknown = ['owner' => 'unknown', 'file' => null];
$check(
    'unreadable_origin_not_invented',
    \Imagine\ContentInventory\Registry::origin($root, $root . '/absent.php') === $unknown
);
$check(
    'outside_origin_never_exports_absolute_path',
    \Imagine\ContentInventory\Registry::origin($root, __FILE__) === $unknown
);
$check('missing_stack_origin_explicit', \Imagine\ContentInventory\Registry::origin($root, null) === $unknown);
require '/subject/a12/Command.php';
foreach (['/', '/work', '/work/site', '/work/site/reports', '/code', '/code/repo', '/code/repo/reports'] as $parent) {
    try {
        $check('disjoint_output_refusal:' . $parent, !\Imagine\ContentInventory\Command::disjointOutput($parent, '/work/site', '/code/repo'));
    } catch (\Throwable) {
        $check('disjoint_output_refusal:' . $parent, false);
    }
}
try {
    $check('disjoint_output_accepted', \Imagine\ContentInventory\Command::disjointOutput('/reports', '/work/site', '/code/repo'));
} catch (\Throwable) {
    $check('disjoint_output_accepted', false);
}
$result = [
    'suite' => 'A12-pure-unit', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true),
];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
echo json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n";
exit($result['exit_code']);
