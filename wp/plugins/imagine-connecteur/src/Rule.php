<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

interface Rule
{
    public function name(): string;

    public function check(Event $event): ?string;
}
