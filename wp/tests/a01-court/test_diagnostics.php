<?php

declare(strict_types=1);

require '/subject/command.php';

$secret = 'FICTION_PRIVATE@example.org';
$failure = \Imagine\Staging\Command::diagnostic(new RuntimeException($secret), 'verifier');
if ($failure['stage'] !== 'native_verifier' || $failure['php']['class'] !== 'RuntimeException'
    || str_contains(json_encode($failure), $secret) || isset($failure['message'])) {
    throw new RuntimeException('DIAGNOSTIC_UNSAFE');
}
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=imagine_ai1wm_fixture', 'root', '');
try {
    $pdo->exec("INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('home','FICTION_PRIVATE@example.org','yes')");
    throw new RuntimeException('EXPECTED_DUPLICATE');
} catch (PDOException $error) {
    $failure = \Imagine\Staging\Command::diagnostic($error, 'anonymiser');
    if ($failure['database']['errno'] !== 1062 || $failure['database']['sqlstate'] !== '23000'
        || str_contains(json_encode($failure), 'Duplicate') || str_contains(json_encode($failure), $secret)) {
        throw new RuntimeException('PDO_DIAGNOSTIC_UNSAFE');
    }
}
echo json_encode(['assertions' => 8, 'ok' => true]);
