<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

use DateTimeImmutable;

final readonly class EntreeCache
{
    public function __construct(
        public Decision $decision,
        public DateTimeImmutable $creation,
        public DateTimeImmutable $expiration,
    ) {
    }
}
