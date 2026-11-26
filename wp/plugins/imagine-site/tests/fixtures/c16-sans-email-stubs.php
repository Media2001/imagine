<?php

declare(strict_types=1);

namespace Imagine\Site;

// Loaded only inside PHPUnit child processes; no WordPress or delivery transport.
function get_user_by(string $field, string $email): object|false
{
    if ($field !== 'email') {
        throw new \LogicException('Email lookup only.');
    }
    return match ($email) {
        'sans@example.org' => (object) ['ID' => 16],
        'normal@example.org' => (object) ['ID' => 17],
        default => false,
    };
}

function get_user_meta(int $id, string $key, bool $single): string
{
    if ($key !== SansEmail::META || !$single) {
        throw new \LogicException('Unique canonical marker required.');
    }
    return $id === 16 ? '1' : '0';
}
