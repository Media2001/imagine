<?php

declare(strict_types=1);

namespace Imagine\AccountSecurity;

final class Inventory
{
    public static function management(array $caps): bool
    {
        foreach ($caps as $cap => $enabled) {
            $pattern = '/\A(?:manage_|edit_others_|delete_others_|activate_plugins\z|edit_plugins\z'
                . '|edit_themes\z|install_plugins\z|update_core\z|promote_users\z|create_users\z|delete_users\z'
                . '|edit_users\z|update_plugins\z|switch_themes\z|delete_plugins\z|delete_themes\z'
                . '|install_themes\z|update_themes\z|edit_theme_options\z|export\z|import\z|remove_users\z)/';
            if ($enabled && preg_match($pattern, (string) $cap)) {
                return true;
            }
        }
        return false;
    }
    private static function label(string $value): string
    {
        return strlen($value) <= 160 && !preg_match('/[@\x00-\x1f]|(?:sk_|pk_|whsec_|xkeysib-)/i', $value)
            ? $value : '[masque]';
    }
    public static function collect(string $site, string $asOf): array
    {
        \Imagine\PublicAddresses\Runtime::boot($site);
        $source = file_get_contents($site . '/wp-config.php');
        $fileEdit = self::configBoolean($source, 'DISALLOW_FILE_EDIT');
        $fileMods = self::configBoolean($source, 'DISALLOW_FILE_MODS');
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        $active = get_option('active_plugins', []);
        $protections = [];
        foreach (get_plugins() as $file => $plugin) {
            $label = $file . ' ' . $plugin['Name'];
            $factor = '~(?:two.factor|2fa|two.step|2.step|login.security|authenticator)~i';
            $firewall = '~(?:wordfence|firewall|sucuri|all.in.one.wp.security|solid.security|ithemes.security)~i';
            $kind = match (true) {
                preg_match($factor, $label) === 1 => 'double_authentification',
                preg_match('~(?:limit.login|login.limit|loginizer)~i', $label) === 1 => 'limitation_tentatives',
                preg_match($firewall, $label) === 1 => 'pare_feu',
                default => null,
            };
            if ($kind !== null) {
                $protections[] = ['name' => self::label($plugin['Name']), 'version' => self::label($plugin['Version']),
                    'active' => in_array($file, $active, true), 'kind' => $kind];
            }
        }
        usort($protections, static fn(array $a, array $b): int => strcmp($a['name'], $b['name']));
        $knownTwoFactor = is_callable(['Two_Factor_Core', 'is_user_using_two_factor']);
        $loginKnown = in_array('wp-last-login/wp-last-login.php', $active, true);
        $clock = \DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:s\Z', $asOf, new \DateTimeZone('UTC'));
        if (!$clock || $clock->format('Y-m-d\TH:i:s\Z') !== $asOf) {
            throw new \RuntimeException('A17_CLOCK_INVALID');
        }
        $cutoff = $clock->modify('-12 months')->getTimestamp();
        $roles = [];
        foreach (wp_roles()->roles as $role => $definition) {
            if (!preg_match('/\A[a-zA-Z_][a-zA-Z0-9_-]{0,99}\z/D', $role)) {
                if (self::management($definition['capabilities'])) {
                    throw new \RuntimeException('A17_ROLE_IDENTIFIER_UNSAFE');
                }
                continue;
            }
            if (
                !in_array($role, ['administrator', 'editor', 'shop_manager'], true)
                && !self::management($definition['capabilities'])
            ) {
                continue;
            }
            $roles[$role] = ['role' => $role, 'accounts' => 0, 'application_password_accounts' => 0,
                'two_factor_active' => $knownTwoFactor ? 0 : null,
                'last_login' => ['status' => $loginKnown ? 'observe' : 'inconnu',
                    'no_recent_record' => $loginKnown ? 0 : null, 'unknown_accounts' => 0]];
        }
        $unique = [];
        foreach (get_users(['fields' => ['ID']]) as $record) {
            $user = new \WP_User((int) $record->ID);
            $memberships = array_intersect($user->roles, array_keys($roles));
            if (!$memberships) {
                continue;
            }
            $id = (int) $record->ID;
            $unique[$id] = true;
            $apps = \WP_Application_Passwords::get_user_application_passwords($id);
            $twoFactor = $knownTwoFactor ? (bool) \Two_Factor_Core::is_user_using_two_factor($id) : null;
            $last = $loginKnown ? get_user_meta($id, 'wp-last-login', true) : '';
            $last = (is_int($last) || (is_string($last) && ctype_digit($last))) && (int) $last > 0
                && (int) $last <= $clock->getTimestamp() ? (int) $last : null;
            foreach ($memberships as $role) {
                $roles[$role]['accounts']++;
                $roles[$role]['application_password_accounts'] += (int) (count($apps) > 0);
                if ($knownTwoFactor) {
                    $roles[$role]['two_factor_active'] += (int) $twoFactor;
                }
                if (!$loginKnown || $last === null) {
                    $roles[$role]['last_login']['unknown_accounts']++;
                } elseif ($last < $cutoff) {
                    $roles[$role]['last_login']['no_recent_record']++;
                }
            }
        }
        ksort($roles);
        $defaultRole = get_option('default_role', '');
        if (!is_string($defaultRole) || !preg_match('/\A[a-zA-Z_][a-zA-Z0-9_-]{0,99}\z/D', $defaultRole)) {
            $defaultRole = '[inconnu]';
        }
        return ['schema' => 'imagine-a17-security-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'as_of_utc' => $asOf, 'cutoff_utc' => gmdate('Y-m-d\TH:i:s\Z', $cutoff),
            'unique_management_accounts' => count($unique), 'roles' => array_values($roles),
            'two_factor_adapter' => $knownTwoFactor ? 'Two_Factor_Core::is_user_using_two_factor' : 'inconnu',
            'last_login_adapter' => $loginKnown ? 'WP Last Login:wp-last-login' : 'inconnu',
            'protections' => $protections, 'configuration' => [
                'public_registration' => (bool) get_option('users_can_register'), 'default_role' => $defaultRole,
                'admin_file_editing' => $fileEdit === true || $fileMods === true ? false
                    : ($fileEdit === null || $fileMods === null ? null : true),
                'xmlrpc_authenticated_methods' => (bool) apply_filters('xmlrpc_enabled', true),
                'application_passwords_available' => wp_is_application_passwords_available(),
            ]];
    }

    public static function configBoolean(string $source, string $name): ?bool
    {
        $tokens = array_values(array_filter(token_get_all($source), static fn($t): bool => !is_array($t)
            || !in_array($t[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)));
        $found = [];
        $depth = 0;
        foreach ($tokens as $i => $token) {
            if ($token === '{') {
                $depth++;
            } elseif ($token === '}') {
                $depth--;
            }
            if (
                !is_array($token) || !in_array($token[0], [T_STRING, T_NAME_FULLY_QUALIFIED], true)
                || strtolower(ltrim($token[1], '\\')) !== 'define' || ($tokens[$i + 1] ?? '') !== '('
            ) {
                continue;
            }
            $literal = $tokens[$i + 2] ?? null;
            if (
                !is_array($literal) || $literal[0] !== T_CONSTANT_ENCAPSED_STRING
                || substr($literal[1], 1, -1) !== $name || ($tokens[$i + 3] ?? '') !== ','
            ) {
                continue;
            }
            $previous = $tokens[$i - 1] ?? null;
            if ($depth !== 0 || !($previous === ';' || (is_array($previous) && $previous[0] === T_OPEN_TAG))) {
                $found[] = null;
                continue;
            }
            $value = $tokens[$i + 4] ?? null;
            $found[] = is_array($value) && $value[0] === T_STRING && ($tokens[$i + 5] ?? '') === ')'
                ? match (strtolower($value[1])) {
                'true' => true, 'false' => false, default => null
                } : null;
        }
        return !$found ? false : (count($found) === 1 ? $found[0] : null);
    }
}
