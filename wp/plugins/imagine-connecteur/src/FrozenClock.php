<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;

final class FrozenClock implements Clock
{
    public function __construct(private DateTimeImmutable $time)
    {
        $this->set($time);
    }

    public function now(): DateTimeImmutable
    {
        return $this->time;
    }

    public function set(DateTimeImmutable $time): void
    {
        $this->time = $time->setTimezone(new DateTimeZone('Europe/Brussels'));
    }

    public function advance(int $seconds): void
    {
        if ($seconds < 0) {
            throw new InvalidArgumentException('L’horloge ne peut pas reculer.');
        }
        $this->time = $this->time->setTimestamp($this->time->getTimestamp() + $seconds);
    }
}
