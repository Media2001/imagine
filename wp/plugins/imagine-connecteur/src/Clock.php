<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use DateTimeImmutable;

interface Clock
{
    public function now(): DateTimeImmutable;
}
