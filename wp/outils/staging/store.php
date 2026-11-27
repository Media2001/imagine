<?php

declare(strict_types=1);

namespace Imagine\Staging;

use RuntimeException;

interface Store
{
    public function database(): string;
    /** Toutes les tables de la base, pas seulement le préfixe WordPress. */
    public function schema(): array;
    public function rows(string $table): array;
    public function begin(): void;
    public function commit(): void;
    public function rollback(): void;
    /** Compare-and-swap : échec si la ligne originale a changé. null supprime. */
    public function replace(string $table, array $before, ?array $after): void;
    public function insert(string $table, array $row): int;
}
