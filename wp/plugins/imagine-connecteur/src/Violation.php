<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

final readonly class Violation
{
    public function __construct(public string $rule, public string $message)
    {
    }
}
