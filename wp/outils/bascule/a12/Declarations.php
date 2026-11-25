<?php

declare(strict_types=1);

namespace Imagine\ContentInventory;

/** Inert source evidence only: never equate a literal call with runtime registration. */
final class Declarations
{
    public static function parse(string $source): array
    {
        $tokens = array_values(array_filter(token_get_all($source), static function ($token): bool {
            return !is_array($token) || !in_array($token[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true);
        }));
        $result = ['post_types' => [], 'taxonomies' => [], 'unresolved_calls' => 0];
        foreach ($tokens as $i => $token) {
            if (!is_array($token) || !in_array($token[0], [T_STRING, T_NAME_FULLY_QUALIFIED], true)) {
                continue;
            }
            $function = strtolower(ltrim($token[1], '\\'));
            if (!in_array($function, ['register_post_type', 'register_taxonomy'], true) || ($tokens[$i + 1] ?? null) !== '(') {
                continue;
            }
            $previous = $tokens[$i - 1] ?? null;
            if (is_array($previous) && in_array($previous[0], [T_FUNCTION, T_OBJECT_OPERATOR, T_NULLSAFE_OBJECT_OPERATOR, T_DOUBLE_COLON], true)) {
                continue;
            }
            $arg = $tokens[$i + 2] ?? null;
            $limit = $function === 'register_post_type' ? 20 : 32;
            $name = is_array($arg) && $arg[0] === T_CONSTANT_ENCAPSED_STRING ? substr($arg[1], 1, -1) : '';
            if (($tokens[$i + 3] ?? null) !== ',' || !preg_match('/\A[a-z0-9_-]{1,' . $limit . '}\z/D', $name)) {
                $result['unresolved_calls']++;
                continue;
            }
            $key = $function === 'register_post_type' ? 'post_types' : 'taxonomies';
            $result[$key][] = $name;
        }
        foreach (['post_types', 'taxonomies'] as $key) {
            $result[$key] = array_values(array_unique($result[$key]));
            sort($result[$key]);
        }
        return $result;
    }
}
