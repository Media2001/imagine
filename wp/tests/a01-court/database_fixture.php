<?php

declare(strict_types=1);

if (!str_contains(ABSPATH, '/imagine-test-a01-ai1wm-')) {
    throw new RuntimeException('SYNTHETIC_PATH_REQUIRED');
}
global $wpdb;
$bytes = implode('', array_map(chr(...), range(0, 255))) . "\0\\'\"\n\r\x1a;FICTION_BINARY_ONLY";
foreach (['fiction_blob', 'fiction_kept_blob', 'fiction_email', 'matomo_archive_blob_2024_01', 'matomo_archive_blob_2024_07', 'matomo_archive_blob_2024_08', 'ahm_emails', 'fsmpt_email_logs', 'wfls_role_counts', 'pmxi_posts', 'pmxe_exports'] as $suffix) {
    $table = $wpdb->prefix . $suffix;
    $personal = $suffix === 'fiction_email' || str_contains($suffix, 'email');
    $wpdb->query("CREATE TABLE `$table` (`id` bigint NOT NULL PRIMARY KEY, " . ($personal ? '`email` text,' : '') . ' `payload` longblob) ENGINE=InnoDB');
    $wpdb->query("INSERT INTO `$table` VALUES (1," . ($personal ? "'FICTION_PRIVATE_SENTINEL@example.org'," : '') . '0x' . bin2hex($bytes) . ')');
}
$wpdb->query("CREATE TABLE `{$wpdb->prefix}actionscheduler_actions` (`action_id` bigint PRIMARY KEY, `hook` varchar(191), `status` varchar(20), `args` text, `schedule` text, `extended_args` text, `claim_id` bigint) ENGINE=InnoDB");
$wpdb->query("INSERT INTO `{$wpdb->prefix}actionscheduler_actions` VALUES (1,'fiction_generic','pending','{\"email\":\"FICTION_AS_SENTINEL@example.org\"}','FICTION','FICTION_EXTENDED@example.org',0),(2,'fiction_done','complete','FICTION_DONE@example.org','FICTION',NULL,0),(3,'pmxe_cron','pending','FICTION_EXPORT@example.org','FICTION',NULL,0),(4,'pmxi_cron','pending','FICTION_IMPORT@example.org','FICTION',NULL,0),(5,'woe_cron_export','pending','FICTION_WOE@example.org','FICTION',NULL,0)");
$wpdb->query("CREATE TABLE `{$wpdb->prefix}actionscheduler_logs` (`log_id` bigint PRIMARY KEY, `action_id` bigint, `message` text) ENGINE=InnoDB");
$wpdb->query("INSERT INTO `{$wpdb->prefix}actionscheduler_logs` VALUES (1,1,'FICTION_LOG_SENTINEL@example.org')");
wp_insert_comment(['comment_content' => 'FICTION_COMMENT_SENTINEL', 'comment_author' => 'FICTION_AUTHOR_SENTINEL', 'comment_author_email' => 'FICTION_COMMENT_SENTINEL@example.org', 'comment_author_IP' => '192.0.2.44']);
update_option('woocommerce_stripe_settings', ['enabled' => 'yes', 'secret_key' => 'sk_live_FICTION_ONLY', 'publishable_key' => 'pk_live_FICTION_ONLY', 'webhook_secret' => 'whsec_FICTION_ONLY', 'testmode' => 'no']);
update_option('fiction_credentials', ['api_key' => 'FICTION_OPTION_SECRET', 'layout' => 'wide']);
foreach (['memberships_profile_fields', 'download-manager-files'] as $folder) {
    wp_mkdir_p(WP_CONTENT_DIR . '/uploads/' . $folder);
    file_put_contents(WP_CONTENT_DIR . '/uploads/' . $folder . '/index.php', 'FICTION_EXCLUDED_SENTINEL');
}
file_put_contents('/report/database-fixture.json', json_encode(['blob_sha256' => hash('sha256', $bytes), 'blob_bytes' => strlen($bytes), 'synthetic_only' => true]));
echo "DATABASE_FIXTURE_SEEDED\n";
