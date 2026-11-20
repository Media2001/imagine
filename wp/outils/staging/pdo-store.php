<?php

declare(strict_types=1);

namespace Imagine\Staging;

use PDO;
use RuntimeException;

/** PDO fourni par le worker : aucun secret, DSN, configuration WordPress ou réseau ici. */
final class PdoStore implements Store
{
    private array $tables = [];
    public function __construct(private PDO $pdo, array $context)
    {
        Guard::context($context);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
        if ($pdo->getAttribute(PDO::ATTR_DRIVER_NAME) !== 'mysql' || $this->database() !== $context['database']) {
            throw new RuntimeException('BASE_REFUSEE');
        }
    }
    public function database(): string
    {
        return (string) $this->pdo->query('SELECT DATABASE()')->fetchColumn();
    }
    private static function quote(string $identifier): string
    {
        if (!preg_match('/^[a-zA-Z0-9_]+$/D', $identifier)) {
            throw new RuntimeException('IDENTIFIANT_SQL_REFUSE');
        }
        return '`' . $identifier . '`';
    }
    public function schema(): array
    {
        $out = [];
        foreach ($this->pdo->query('SHOW FULL TABLES')->fetchAll(PDO::FETCH_NUM) as [$name, $type]) {
            if ($type !== 'BASE TABLE') {
                throw new RuntimeException('VUE_REFUSEE');
            }
            $statement = $this->pdo->prepare('SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = ?');
            $statement->execute([$name]);
            if (strtoupper((string) $statement->fetchColumn()) !== 'INNODB') {
                throw new RuntimeException('MOTEUR_NON_TRANSACTIONNEL');
            }
            $out[$name] = array_column($this->pdo->query('SHOW COLUMNS FROM ' . self::quote($name))->fetchAll(PDO::FETCH_ASSOC), 'Field');
        }
        // Les triggers peuvent recopier les données hors des tables traitées.
        if ($this->pdo->query('SHOW TRIGGERS')->fetch()) {
            throw new RuntimeException('TRIGGER_REFUSE');
        }
        if ($this->pdo->query('SHOW EVENTS')->fetch()) {
            throw new RuntimeException('EVENT_SQL_REFUSE');
        }
        $this->tables = $out;
        return $out;
    }
    private function table(string $name): string
    {
        if (!isset($this->tables[$name])) {
            throw new RuntimeException('TABLE_NON_INVENTORIEE');
        }
        return self::quote($name);
    }
    public function rows(string $table): array
    {
        return $this->pdo->query('SELECT * FROM ' . $this->table($table))->fetchAll(PDO::FETCH_ASSOC);
    }
    public function begin(): void
    {
        $this->pdo->beginTransaction();
    }
    public function commit(): void
    {
        $this->pdo->commit();
    }
    public function rollback(): void
    {
        if ($this->pdo->inTransaction()) {
            $this->pdo->rollBack();
        }
    }
    public function replace(string $table, array $before, ?array $after): void
    {
        if ($before === $after) {
            return;
        }
        if (!$before) {
            throw new RuntimeException('CAS_VIDE');
        }
        $where = implode(' AND ', array_map(static fn (string $c): string => 'BINARY ' . self::quote($c) . ' <=> ?', array_keys($before)));
        $values = array_values($before);
        if ($after === null) {
            $sql = 'DELETE FROM ' . $this->table($table) . ' WHERE ' . $where;
        } else {
            if (array_keys($before) !== array_keys($after)) {
                throw new RuntimeException('CAS_COLONNES');
            }
            $sql = 'UPDATE ' . $this->table($table) . ' SET ' . implode(', ', array_map(static fn (string $c): string => self::quote($c) . ' = ?', array_keys($after))) . ' WHERE ' . $where;
            $values = array_merge(array_values($after), $values);
        }
        $statement = $this->pdo->prepare($sql);
        $statement->execute($values);
        if ($statement->rowCount() !== 1) {
            throw new RuntimeException('CAS_ECHOUE');
        }
    }
    public function insert(string $table, array $row): int
    {
        if (array_diff(array_keys($row), $this->tables[$table] ?? [])) {
            throw new RuntimeException('INSERT_COLONNES');
        }
        $sql = 'INSERT INTO ' . $this->table($table) . ' (' . implode(', ', array_map(self::quote(...), array_keys($row))) . ') VALUES (' . implode(', ', array_fill(0, count($row), '?')) . ')';
        $this->pdo->prepare($sql)->execute(array_values($row));
        return (int) $this->pdo->lastInsertId();
    }
}
