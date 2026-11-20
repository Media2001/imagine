<?php

declare(strict_types=1);

// Faux transport PDO : vérifie le contrat d'inventaire, pas un serveur SQL.
require __DIR__ . '/../../outils/staging/lib.php';
require __DIR__ . '/../../outils/staging/pdo-store.php';

final class SyntheticStatement extends PDOStatement
{
    public function __construct(private array $result = []) {}
    public function execute(?array $params = null): bool { return true; }
    public function fetchAll(int $mode = PDO::FETCH_DEFAULT, mixed ...$args): array { return $this->result; }
    public function fetchColumn(int $column = 0): mixed { return $this->result[0][$column] ?? false; }
    public function fetch(int $mode = PDO::FETCH_DEFAULT, int $cursorOrientation = PDO::FETCH_ORI_NEXT, int $cursorOffset = 0): mixed { return $this->result[0] ?? false; }
}
final class SyntheticPdo extends PDO
{
    public function __construct() {}
    public function setAttribute(int $attribute, mixed $value): bool { return true; }
    public function getAttribute(int $attribute): mixed { return $attribute === PDO::ATTR_DRIVER_NAME ? 'mysql' : null; }
    public function prepare(string $query, array $options = []): PDOStatement|false
    {
        return new SyntheticStatement([['MyISAM']]);
    }
    public function query(string $query, ?int $fetchMode = null, mixed ...$fetchModeArgs): PDOStatement|false
    {
        return new SyntheticStatement(match (true) {
            $query === 'SELECT DATABASE()' => [['invented_staging']],
            $query === 'SHOW FULL TABLES' => [['x_options', 'BASE TABLE'], ['extension odd`name', 'BASE TABLE'], ['x_summary', 'VIEW']],
            str_starts_with($query, 'SHOW COLUMNS') => [['Field'=>'id'], ['Field'=>'setting']],
            $query === 'SHOW TRIGGERS' => [['Trigger'=>'synthetic_trigger', 'Statement'=>'SYNTHETIC VALUE MUST NOT LEAK']],
            $query === 'SHOW EVENTS' => [['Name'=>'synthetic_event', 'Definition'=>'SYNTHETIC VALUE MUST NOT LEAK']],
            default => [],
        });
    }
}
$context = ['environment'=>'staging','isolated'=>true,'restored'=>true,'database'=>'invented_staging',
    'target_url'=>'https://invented.test','production_hosts'=>['production.invalid']];
$store = new Imagine\Staging\PdoStore(new SyntheticPdo(), $context);
$schema = $store->schema();
$details = $store->details();
$checks = [
    count($schema) === 3,
    $schema['x_summary'] === ['id','setting'],
    isset($schema['extension odd`name']),
    $details['tables']['x_summary']['type'] === 'VIEW',
    $details['tables']['x_options']['engine'] === 'MyISAM',
    $details['triggers'] === ['synthetic_trigger'],
    $details['events'] === ['synthetic_event'],
    in_array('VUE_CONSERVEE', $details['warnings'], true),
    in_array('MOTEUR_NON_TRANSACTIONNEL', $details['warnings'], true),
    !str_contains(json_encode($details), 'VALUE MUST NOT LEAK'),
];
if (in_array(false, $checks, true)) {
    throw new RuntimeException('Inventaire PDO reprise incomplet');
}
print('OK '.count($checks)." assertions PDO contract\n");
