<?php

declare(strict_types=1);

namespace Imagine\Staging;

use RuntimeException;

/** The suffix is validated against the closed, repository-owned policy, never site text. */
final class FormDecisionRefused extends RuntimeException
{
    public function __construct(public readonly string $table, array $tables)
    {
        if (!in_array($table, $tables, true)) {
            throw new RuntimeException('FORM_POLICY_REFUSED');
        }
        parent::__construct('FORM_MESSAGES_DECISION_REFUSED');
    }
}
