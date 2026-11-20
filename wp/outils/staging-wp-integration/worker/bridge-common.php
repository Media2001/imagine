<?php
declare(strict_types=1);

function workerRequest(): array {
    $fd = getenv('STAGING_REQUEST_FD');
    $raw = $fd !== false && ctype_digit($fd) ? file_get_contents('php://fd/' . $fd) : stream_get_contents(STDIN);
    $r = json_decode($raw ?: '', true, 32, JSON_THROW_ON_ERROR);
    if (($r['protocol'] ?? '') !== 'staging-offline-v1' || ($r['environment'] ?? '') !== 'staging'
        || ($r['wordpress_path'] ?? '') !== '/var/www/html'
        || ($r['database']['socket'] ?? '') !== '/run/mysqld/mysqld.sock'
        || ($r['database']['user'] ?? '') !== 'wp'
        || !preg_match('/^[a-zA-Z0-9_]+_(staging|test)$/D', $r['database']['name'] ?? '')) {
        throw new RuntimeException('REFUS');
    }
    return $r;
}
function workerContext(array $r): array {
    return ['environment'=>'staging', 'isolated'=>true, 'restored'=>true,
            'database'=>$r['database']['name'], 'target_url'=>$r['staging_url'],
            'production_hosts'=>$r['production_hosts'], 'table_decisions'=>$r['table_decisions'] ?? []];
}
function workerPdo(array $r): PDO {
    $db = $r['database'];
    $pdo = new PDO('mysql:unix_socket=/run/mysqld/mysqld.sock;dbname='.$db['name'].';charset=utf8mb4',
        'wp', $db['password'], [PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,
                               PDO::ATTR_EMULATE_PREPARES=>false]);
    if ($pdo->query('SELECT DATABASE()')->fetchColumn() !== $db['name']
        || (int)$pdo->query('SELECT @@skip_networking')->fetchColumn() !== 1) {
        throw new RuntimeException('REFUS');
    }
    return $pdo;
}
