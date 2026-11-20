<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

enum State: string
{
    case Pending = 'pending';
    case Processing = 'processing';
    case Sent = 'sent';
    case TemporaryFailure = 'temporary_failure';
    case Quarantine = 'quarantine';

    public function allows(self $next): bool
    {
        return match ($this) {
            self::Pending, self::TemporaryFailure => $next === self::Processing,
            self::Processing => in_array($next, [self::Sent, self::TemporaryFailure, self::Quarantine], true),
            self::Sent, self::Quarantine => false,
        };
    }
}
