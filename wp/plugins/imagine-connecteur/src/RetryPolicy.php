<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use InvalidArgumentException;

final readonly class RetryPolicy
{
    public function __construct(
        public int $maxAttempts,
        private int $initialSeconds,
        private int $factor,
        private int $maximumSeconds
    ) {
        if ($maxAttempts < 1 || $initialSeconds < 1 || $factor < 2 || $maximumSeconds < $initialSeconds) {
            throw new InvalidArgumentException('Paramètres de rejeu non valides.');
        }
    }

    public function delay(int $attempt): int
    {
        if ($attempt < 1) {
            throw new InvalidArgumentException('Le numéro d’essai commence à un.');
        }
        $delay = $this->initialSeconds;
        for ($index = 1; $index < $attempt && $delay < $this->maximumSeconds; ++$index) {
            $delay = $delay > intdiv($this->maximumSeconds, $this->factor)
                ? $this->maximumSeconds : min($this->maximumSeconds, $delay * $this->factor);
        }
        return $delay;
    }
}
