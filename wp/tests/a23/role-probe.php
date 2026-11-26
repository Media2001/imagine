<?php

declare(strict_types=1);

// Boundary doubles only. Run in its own PHP process, never in WordPress.
namespace {
    require __DIR__ . '/RoleRuntimeDouble.php';
    require __DIR__ . '/RoleUserDouble.php';
    require __DIR__ . '/RoleDatabaseDouble.php';
    define('ARRAY_A', 'ARRAY_A');

    function wp_roles(): object
    {
        return $GLOBALS['a23RoleRegistry'];
    }

    function is_email(string $email): string|false
    {
        return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : false;
    }

}

namespace Imagine\ReaderAccountsRoleTest {
    use Imagine\ReaderAccounts\Inventory;

    $root = dirname(__DIR__, 2) . '/outils/bascule';
    if (!is_file($root . '/a23/Inventory.php')) {
        $root = '/subject';
    }
    require $root . '/a17/Inventory.php';
    require $root . '/a23/Analysis.php';
    // Optional scratch-only predecessor for an honest RED replay by the parent.
    require($argv[1] ?? $root . '/a23/Inventory.php');

    $checks = [];
    $check = static function (string $name, bool $ok) use (&$checks): void {
        $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    };
    $add = static function (array $roles, array $caps, bool $live, string $hash): void {
        $db = $GLOBALS['wpdb'];
        $id = count($db->users) + 1;
        $db->users[] = ['ID' => $id, 'user_login' => 'A23_ROLE_LOGIN_PRIVATE_CANARY_' . $id,
            'user_email' => 'a23-role-' . $id . '@example.org', 'user_pass' => $hash];
        $GLOBALS['a23RoleUsers'][$id] = ['roles' => $roles, 'allcaps' => $caps];
        if ($live) {
            $db->commerce[] = ['id' => (string) $id, 'type' => 'shop_subscription',
                'status' => 'wc-pending', 'customer' => (string) $id];
        }
    };

    try {
        foreach (['classic', 'hpos'] as $storage) {
            $GLOBALS['wpdb'] = new \A23RoleDatabaseDouble();
            $GLOBALS['wpdb']->storage = $storage;
            $GLOBALS['a23RoleUsers'] = [];
            $GLOBALS['a23RoleRegistry'] = (object) ['roles' => [
                'customer' => ['capabilities' => ['read' => true]],
                'a23_operator' => ['capabilities' => ['read' => true, 'edit_users' => true]],
                'a23_disabled' => ['capabilities' => ['edit_users' => false]],
            ]];
            for ($i = 0; $i < 5; $i++) {
                $add(['customer'], ['read' => true], true, '$P$A23_ROLE_HASH_PRIVATE_CANARY');
            }
            for ($i = 0; $i < 5; $i++) {
                $add(
                    ['a23_operator'],
                    ['read' => true, 'edit_users' => false],
                    $i < 3,
                    '$2y$A23_ROLE_HASH_PRIVATE_CANARY'
                );
            }
            $add(
                ['customer', 'a23_operator'],
                ['read' => true, 'edit_users' => false],
                true,
                '$2y$A23_ROLE_HASH_PRIVATE_CANARY'
            );
            $add(['customer'], ['manage_a23' => true], false, '$2y$A23_ROLE_HASH_PRIVATE_CANARY');
            // Fixed roles remain excluded even when their definitions are absent.
            foreach (['administrator', 'editor', 'shop_manager'] as $role) {
                $add([$role], [], false, '$2y$A23_ROLE_HASH_PRIVATE_CANARY');
            }
            $report = Inventory::collect('/fictitious-boundary-double');
            $counts = $report['counts'];
            $check($storage . ':role_negative_override_excluded', $counts['readers']['accounts'] === 5);
            $check($storage . ':role_multi_management_excluded', $counts['live_readers']['accounts'] === 5);
            $check(
                $storage . ':management_without_commerce_excluded',
                $counts['without_commerce'] === ['groups' => [], 'autres' => 0]
            );
            $check($storage . ':no_false_published_family', $counts['readers']['families'] === [
                'groups' => [['label' => 'phpass', 'accounts' => 5]], 'autres' => 0]);
            $check($storage . ':private_values_absent', !str_contains(json_encode($report), 'CANARY')
                && !str_contains(json_encode($report), '@'));
            $check($storage . ':authoritative_storage', $report['storage'] === $storage);
            // A direct false grant and a disabled management-looking role are not management.
            $add(['a23_disabled'], ['edit_users' => false], false, '');
            $check(
                $storage . ':false_capability_keeps_reader',
                Inventory::collect('/fictitious-boundary-double')['counts']['readers']['accounts'] === 6
            );
            $GLOBALS['a23RoleRegistry']->roles['A23_ROLE_PRIVATE_CANARY@example.org'] = [
                'capabilities' => ['read' => true]];
            $check(
                $storage . ':unsafe_non_management_role_ignored',
                Inventory::collect('/fictitious-boundary-double')['counts']['readers']['accounts'] === 6
            );
            unset($GLOBALS['a23RoleRegistry']->roles['A23_ROLE_PRIVATE_CANARY@example.org']);
            foreach (['bad@example.org', '9bad', "bad\n", str_repeat('a', 101)] as $i => $role) {
                $GLOBALS['a23RoleRegistry']->roles[$role] = ['capabilities' => ['edit_users' => true]];
                $code = '';
                try {
                    Inventory::collect('/fictitious-boundary-double');
                } catch (\RuntimeException $error) {
                    $code = $error->getMessage();
                }
                $check($storage . ':unsafe_management_role_closed:' . $i, $code === 'A23_ROLE_IDENTIFIER_UNSAFE');
                unset($GLOBALS['a23RoleRegistry']->roles[$role]);
            }
            foreach (['A', 'A_' . str_repeat('a', 97) . '-'] as $i => $role) {
                $GLOBALS['a23RoleRegistry']->roles[$role] = ['capabilities' => ['edit_users' => true]];
                $add([$role], ['edit_users' => false], false, '');
                $check(
                    $storage . ':valid_role_boundary:' . $i,
                    Inventory::collect('/fictitious-boundary-double')['counts']['readers']['accounts'] === 6
                );
            }
        }
    } catch (\Throwable $error) {
        $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'class' => get_class($error)];
    }
    $exit = (int) in_array('FAIL', array_column($checks, 'status'), true);
    echo json_encode(['suite' => 'A23-role-definitions-boundary-doubles', 'checks' => $checks,
        'exit_code' => $exit], JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n";
    exit($exit);
}
