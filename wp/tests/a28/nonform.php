<?php

declare(strict_types=1);

$root = getenv('A28_SUBJECT');
if (!in_array($root, ['/subject', '/reference'], true)) {
    throw new RuntimeException('A28_REFERENCE_REFUSED');
}
require $root . '/command.php';
require __DIR__ . '/MemoryStore.php';
$store = new Imagine\A28Tests\MemoryStore();
$store->tables['x_fiction_messages'] = [['id' => 1, 'payload' => 'A28_FICTIVE_KEEP']];
$store->tables['x_posts'] = [
    ['ID' => 10, 'post_type' => 'post', 'post_content' => 'A28_FICTIVE_EDITORIAL'],
    ['ID' => 11, 'post_type' => 'fiction_magazine', 'post_content' => 'A28_FICTIVE_UNKNOWN'],
    ['ID' => 12, 'post_type' => 'wpcf7_contact_form', 'post_content' => 'A28_FICTIVE_DEFINITION'],
];
$store->tables['x_postmeta'] = [['meta_id' => 10, 'post_id' => 11, 'meta_key' => '_fixture', 'meta_value' => 'A28_FICTIVE_KEEP']];
$context = [
    'environment' => 'staging', 'isolated' => true, 'restored' => true, 'database' => 'a28_test',
    'target_url' => 'https://fiction.test', 'production_hosts' => ['source.invalid'],
];
$engine = new Imagine\Staging\Engine($store, $context, 'x_', ['x_fiction_messages' => ['action' => 'garder']]);
$engine->neutraliser();
$report = $engine->verifier(static fn (): array => array_fill_keys([
    'mail_blocked', 'subscriptions_staging', 'http_blocked', 'environment_staging',
    'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled',
], true));
$added = $report['form_message_residues'] ?? null;
unset($report['form_message_residues']);
$diagnostics = [];
foreach (['DECISION_INVALIDE', 'REFUS', 'A28_UNTRUSTED_FICTIVE'] as $code) {
    $diagnostics[] = Imagine\Staging\Command::diagnostic(new RuntimeException($code), 'neutraliser');
}
echo json_encode(['tables' => $store->tables, 'report' => $report, 'diagnostics' => $diagnostics]);
fwrite(STDERR, json_encode(['added_count' => $added]));
