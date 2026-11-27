<?php

declare(strict_types=1);

use Imagine\A28Tests\MemoryStore;
use Imagine\Staging\Command;
use Imagine\Staging\Engine;

// T01 copies this bank, while the staging library stays on its read-only source mount.
$candidates = [__DIR__ . '/../../outils/staging', '/subject', '/repo/wp/outils/staging'];
foreach ($candidates as $candidate) {
    if (is_file($candidate . '/command.php')) {
        require $candidate . '/command.php';
        break;
    }
}
require __DIR__ . '/MemoryStore.php';
$context = [
    'environment' => 'staging', 'isolated' => true, 'restored' => true, 'database' => 'a28_test',
    'target_url' => 'https://fiction.test', 'production_hosts' => ['source.invalid'],
];
$proof = static fn(): array => array_fill_keys([
    'mail_blocked', 'subscriptions_staging', 'http_blocked', 'environment_staging',
    'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled',
], true);
$tables = ['fluentform_submissions', 'fluentform_entry_details', 'fluentform_submission_meta',
    'fluentform_logs', 'fluentform_draft_submissions', 'ff_scheduled_actions'];
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
try {
    foreach ($tables as $kind) {
        $store = new MemoryStore();
        $store->tables['x_' . $kind] = [['id' => 1, 'payload' => 'A28_FICTIVE_UNIT']];
        $engine = new Engine($store, $context, 'x_');
        $engine->neutraliser();
        $check('legacy_forced_empty_' . $kind, $store->tables['x_' . $kind] === []);
        foreach (['garder', 'anonymiser'] as $action) {
            $absent = new MemoryStore();
            $refusal = null;
            try {
                new Engine($absent, $context, 'x_', ['x_' . $kind => ['action' => $action]]);
            } catch (Throwable $error) {
                $refusal = Command::diagnostic($error, 'neutraliser');
            }
            $check('absent_closed_refusal_' . $action . '_' . $kind, ($refusal['code']
                ?? '') === 'FORM_MESSAGES_DECISION_REFUSED');
            $store = new MemoryStore();
            $store->tables['x_' . $kind] = [['id' => 1, 'payload' => 'A28_FICTIVE_UNIT']];
            $before = $store->tables;
            $refusal = null;
            try {
                new Engine($store, $context, 'x_', ['x_' . $kind => ['action' => $action]]);
            } catch (Throwable $error) {
                $refusal = Command::diagnostic($error, 'neutraliser');
            }
            $check('closed_refusal_' . $action . '_' . $kind, $refusal === [
                'stage' => 'native_neutraliser', 'code' => 'FORM_MESSAGES_DECISION_REFUSED', 'table' => $kind,
            ]);
            $check('no_write_on_refusal_' . $action . '_' . $kind, $store->tables === $before);
        }
        $engine = new Engine($store, $context, 'x_');
        $calls = 0;
        $report = $engine->verifier(static function () use (&$calls, $proof): array {
            ++$calls;
            return $proof();
        });
        $check('residue_numeric_' . $kind, !$report['ok'] && $report['form_message_residues'] === 1
            && in_array('FORM_MESSAGES_REMAIN', $report['issues'], true));
        $check('residue_no_bootstrap_' . $kind, $calls === 0);
        $check('no_message_output_' . $kind, !str_contains(json_encode($report), 'A28_FICTIVE_UNIT'));
    }
    // Known provenance must survive a parent removed before a new verification process.
    $store = new MemoryStore();
    $store->tables['x_postmeta'] = [
        ['meta_id' => 1, 'post_id' => 41, 'meta_key' => '_a28_message', 'meta_value' => 'A28_FICTIVE_ORPHAN'],
        ['meta_id' => 2, 'post_id' => 42, 'meta_key' => '_a28_message', 'meta_value' => 'A28_FICTIVE_REVISION'],
        ['meta_id' => 3, 'post_id' => 99, 'meta_key' => '_a28_message', 'meta_value' => 'A28_UNKNOWN_ORPHAN'],
    ];
    $engine = new Engine($store, $context + ['form_post_ids' => [41, 42]], 'x_');
    $calls = 0;
    $report = $engine->verifier(static function () use (&$calls, $proof): array {
        ++$calls;
        return $proof();
    });
    $check('known_orphan_postmeta_counted', !$report['ok'] && $report['form_message_residues'] === 2
        && in_array('FORM_MESSAGES_REMAIN', $report['issues'], true));
    $check('known_orphan_no_bootstrap', $calls === 0);
    $engine->neutraliser();
    $check('unknown_orphan_not_globally_purged', array_column($store->rows('x_postmeta'), 'post_id') === [99]);
    foreach ([[0], ['41'], [1 => 41], '41'] as $invalid) {
        $refused = false;
        try {
            new Engine(new MemoryStore(), $context + ['form_post_ids' => $invalid], 'x_');
        } catch (RuntimeException $error) {
            $refused = $error->getMessage() === 'CONTEXTE_REFUSE';
        }
        $check('invalid_provenance_' . count($checks), $refused);
    }
    $store = new MemoryStore();
    $store->tables['x_posts'] = [
        ['ID' => 41, 'post_type' => 'flamingo_inbound', 'post_parent' => 0],
        ['ID' => 42, 'post_type' => 'revision', 'post_parent' => 41],
    ];
    $store->tables['x_postmeta'] = [
        ['meta_id' => 1, 'post_id' => 42, 'meta_key' => '_a28_message', 'meta_value' => 'A28_FICTIVE_UNIT'],
    ];
    $engine = new Engine($store, $context, 'x_');
    $store->tables['x_posts'] = [];
    $report = $engine->verifier($proof);
    $check('in_memory_provenance_survives_parent_and_revision_loss', !$report['ok']
        && $report['form_message_residues'] === 1);
    foreach (['flamingo_inbound', 'flamingo_contact'] as $type) {
        $store = new MemoryStore();
        $store->tables['x_posts'] = [
            ['ID' => 1, 'post_type' => $type, 'post_parent' => 0, 'post_content' => 'A28_FICTIVE_UNIT'],
            ['ID' => 2, 'post_type' => 'revision', 'post_parent' => 1, 'post_content' => 'A28_FICTIVE_UNIT'],
            ['ID' => 3, 'post_type' => 'revision', 'post_parent' => 2, 'post_content' => 'A28_FICTIVE_UNIT'],
            ['ID' => 4, 'post_type' => 'fiction_magazine', 'post_parent' => 0, 'post_content' => 'A28_FICTIVE_UNIT'],
            ['ID' => 5, 'post_type' => 'wpcf7_contact_form', 'post_parent' => 0, 'post_content' =>
                'A28_FORM_DEFINITION'],
        ];
        $store->tables['x_postmeta'] = [
            ['meta_id' => 1, 'post_id' => 1, 'meta_key' => '_body', 'meta_value' => 'A28_FICTIVE_UNIT'],
            ['meta_id' => 2, 'post_id' => 2, 'meta_key' => '_body', 'meta_value' => 'A28_FICTIVE_UNIT'],
            ['meta_id' => 3, 'post_id' => 3, 'meta_key' => '_body', 'meta_value' => 'A28_FICTIVE_UNIT'],
            ['meta_id' => 4, 'post_id' => 4, 'meta_key' => '_body', 'meta_value' => 'A28_FICTIVE_UNIT'],
        ];
        $engine = new Engine($store, $context, 'x_');
        $report = $engine->verifier($proof);
        $check('post_residue_' . $type, !$report['ok'] && $report['form_message_residues'] === 6);
        $engine->neutraliser();
        $check('known_posts_revisions_deleted_' . $type, array_column($store->rows('x_posts'), 'ID') === [4, 5]);
        $check('known_postmeta_deleted_' . $type, array_column($store->rows('x_postmeta'), 'post_id') === [4]);
        $snapshot = $store->tables;
        $engine->neutraliser();
        $check('idempotent_' . $type, $store->tables === $snapshot);
        $report = $engine->verifier($proof);
        $check('unknown_type_remains_warning_' . $type, $report['ok'] && $report['form_message_residues'] === 0
            && in_array('fiction_magazine', $report['unknown_post_types'], true));
    }
    $store = new MemoryStore();
    $store->tables['x_fiction_fluentform_submissions'] = [['id' => 1, 'payload' => 'A28_FICTIVE_UNIT']];
    $before = $store->tables['x_fiction_fluentform_submissions'];
    (new Engine($store, $context, 'x_'))->neutraliser();
    $check('exact_suffix_only', $store->tables['x_fiction_fluentform_submissions'] === $before);
    $store = new MemoryStore();
    $store->tables['x_fluentform_submissions'] = [['id' => 1, 'payload' => 'A28_FICTIVE_UNIT']];
    $store->view = true;
    $engine = new Engine($store, $context, 'x_');
    $engine->neutraliser();
    $check('read_only_residue_never_verified', !$engine->verifier($proof)['ok']);
    $store = new MemoryStore();
    $engine = new Engine($store, $context, 'x_');
    $report = $engine->verifier(static function () use ($store, $proof): array {
        $store->tables['x_posts'][] = ['ID' => 42, 'post_type' => 'flamingo_inbound', 'post_content' =>
            'A28_FICTIVE_UNIT'];
        return $proof();
    });
    $check('residue_introduced_during_bootstrap_refused', !$report['ok'] && $report['form_message_residues'] === 1);
    $refusal = null;
    try {
        new Engine(new MemoryStore(), $context, 'x_', [0 => ['action' => 'garder']]);
    } catch (Throwable $error) {
        $refusal = Command::diagnostic($error, 'neutraliser');
    }
    $check('non_form_numeric_decision_keeps_A01_code', ($refusal['code'] ?? '') === 'DECISION_INVALIDE');
} catch (Throwable $error) {
    $checks[] = ['check' => 'exception', 'status' => 'FAIL', 'class' => get_class($error)];
}
$result = ['checks' => $checks, 'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true)];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT) . "\n");
echo 'A28_UNIT ' . count($checks) . "\n";
exit($result['exit_code']);
