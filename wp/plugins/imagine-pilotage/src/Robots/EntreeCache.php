<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

use DateTimeImmutable;

final readonly class EntreeCache
{
    public DateTimeImmutable $creation;
    public DateTimeImmutable $expiration;

    public function __construct(
        public Decision $decision,
        DateTimeImmutable $creation,
        DateTimeImmutable $expiration,
    ) {
        $zone = new \DateTimeZone('Europe/Brussels');
        $this->creation = $creation->setTimezone($zone);
        $this->expiration = $expiration->setTimezone($zone);
    }
}
