<?php

declare(strict_types=1);

// Only executed inside the A28-owned synthetic fixture, never on a real site.
if (DB_NAME !== 'imagine_e2e_classic_test' && DB_NAME !== 'imagine_e2e_hpos_test') {
    throw new RuntimeException('A28_SYNTHETIC_ONLY');
}
global $wpdb;
$tables = [
    'fluentform_submissions', 'fluentform_entry_details', 'fluentform_submission_meta',
    'fluentform_logs', 'fluentform_draft_submissions', 'ff_scheduled_actions', 'fiction_messages',
];
foreach ($tables as $kind) {
    $table = $wpdb->prefix . $kind;
    $wpdb->query("CREATE TABLE `$table` (`id` bigint NOT NULL, `payload` longtext, PRIMARY KEY (`id`)) ENGINE=InnoDB");
    $wpdb->insert($table, ['id' => 1, 'payload' => 'A28_FICTIVE_' . $kind]);
}
$ids = [];
foreach (['flamingo_inbound', 'flamingo_contact', 'fiction_magazine'] as $type) {
    $id = wp_insert_post([
        'post_type' => $type, 'post_status' => 'publish',
        'post_title' => 'A28_FICTIVE_' . $type, 'post_content' => 'A28_FICTIVE_' . $type,
    ], true);
    if (is_wp_error($id)) {
        throw new RuntimeException('A28_SEED_FAILED');
    }
    $ids[$type] = $id;
    update_post_meta($id, '_a28_message', 'A28_FICTIVE_META_' . $type);
    $revision = wp_insert_post([
        'post_type' => 'revision', 'post_status' => 'inherit', 'post_parent' => $id,
        'post_content' => 'A28_FICTIVE_REVISION_' . $type,
    ], true);
    add_metadata('post', $revision, '_a28_message', 'A28_FICTIVE_REVISION_META_' . $type);
}
echo 'A28_SEED ' . json_encode(['posts' => $ids, 'tables' => $tables]) . "\n";
