<?php

declare(strict_types=1);

namespace Imagine\AccountSecurity;

final class Inventory
{
    public static function management(array $caps): bool
    {
        foreach ($caps as $cap => $enabled) {
            if ($enabled && preg_match('/\A(?:manage_|edit_others_|delete_others_|publish_|activate_plugins\z|edit_plugins\z|edit_themes\z|install_plugins\z|update_core\z|promote_users\z|create_users\z|delete_users\z)/', (string) $cap)) {
                return true;
            }
        }
        return false;
    }
    public static function configBoolean(string $source, string $name): ?bool
    {
        $tokens = array_values(array_filter(token_get_all($source), static fn($t): bool => !is_array($t)
            || !in_array($t[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)));
        $found = [];
        foreach ($tokens as $i => $token) {
            if (!is_array($token) || !in_array($token[0], [T_STRING, T_NAME_FULLY_QUALIFIED], true)
                || strtolower(ltrim($token[1], '\\')) !== 'define' || ($tokens[$i + 1] ?? '') !== '(') {
                continue;
            }
            $literal = $tokens[$i + 2] ?? null;
            if (!is_array($literal) || $literal[0] !== T_CONSTANT_ENCAPSED_STRING
                || substr($literal[1], 1, -1) !== $name || ($tokens[$i + 3] ?? '') !== ',') {
                continue;
            }
            $value = $tokens[$i + 4] ?? null;
            $found[] = is_array($value) && $value[0] === T_STRING && ($tokens[$i + 5] ?? '') === ')'
                ? match (strtolower($value[1])) {'true' => true, 'false' => false, default => null} : null;
        }
        return !$found ? false : (count($found) === 1 ? $found[0] : null);
    }
}
