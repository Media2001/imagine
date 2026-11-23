<?php

declare(strict_types=1);

// Independent logical fingerprint: no WordPress or subject code is loaded.
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . getenv('A02_DB'), 'root', '', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$tables = $pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN);
sort($tables);
$manifest = [];
foreach ($tables as $table) {
    if (!preg_match('/\A[a-zA-Z0-9_]+\z/D', $table)) {
        throw new RuntimeException('FIXTURE_TABLE_NAME');
    }
    $schema = $pdo->query('SHOW CREATE TABLE `' . $table . '`')->fetch(PDO::FETCH_NUM)[1];
    $statement = $pdo->query('SELECT * FROM `' . $table . '`');
    $rows = [];
    while ($row = $statement->fetch(PDO::FETCH_ASSOC)) {
        $rows[] = hash('sha256', serialize($row));
    }
    sort($rows);
    $manifest[$table] = ['rows' => count($rows), 'schema_sha256' => hash('sha256', $schema), 'rows_sha256' => hash('sha256', implode("\n", $rows))];
}
echo json_encode(['logical_sha256' => hash('sha256', json_encode($manifest)), 'tables' => $manifest], JSON_PRETTY_PRINT) . "\n";
