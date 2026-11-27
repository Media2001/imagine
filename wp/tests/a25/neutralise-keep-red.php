<?php

declare(strict_types=1);

// Disposable bench only: reenact the former keep request against current A28.
require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';

$db = getenv('A25_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1,
    'table_decisions' => ['wp_fluentform_submissions' => ['action' => 'garder'],
        'wp_a25_unknown_entries' => ['action' => 'garder'],
        'wp_a25_submission_entries' => ['action' => 'garder'],
        'wp_a25_submission_details' => ['action' => 'garder']]];
try {
    $engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
    $engine->neutraliser();
} catch (Imagine\Staging\FormDecisionRefused $error) {
    if ($error->getMessage() === 'FORM_MESSAGES_DECISION_REFUSED' && $error->table === 'fluentform_submissions') {
        echo "A25_OLD_KEEP_REFUSED\n";
        exit(1); // Genuine refusal path is the expected RED control, not a green command.
    }
    exit(2);
}
echo "A25_OLD_KEEP_UNEXPECTEDLY_ALLOWED\n";
exit(0);
