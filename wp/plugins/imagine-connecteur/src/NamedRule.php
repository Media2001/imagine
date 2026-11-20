<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use Closure;
use InvalidArgumentException;

final readonly class NamedRule implements Rule
{
    private Closure $check;

    public function __construct(private string $name, callable $check)
    {
        if (trim($name) === '') {
            throw new InvalidArgumentException('Une règle doit être nommée.');
        }
        $this->check = Closure::fromCallable($check);
    }

    public function name(): string
    {
        return $this->name;
    }

    public function check(Event $event): ?string
    {
        return ($this->check)($event);
    }
}
