<?php

declare(strict_types=1);

require '/opt/dbfixture-original.php';
global $wpdb;
$wpdb->query("CREATE TABLE `wp_fiction_compat` (`id` bigint NOT NULL PRIMARY KEY, `amount` int, `doubled` int GENERATED ALWAYS AS (`amount` + 1) STORED, `payload` JSON, `stamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00', `wide` longtext, KEY `pref` (`wide`(16))) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC");
$wpdb->query("INSERT INTO wp_fiction_compat (id,amount,payload,wide) VALUES (1,7,'{\"fiction\":true}','FICTION')");
foreach (['MyISAM', 'MEMORY'] as $engine) {
    $table = 'wp_fiction_' . strtolower($engine);
    $wpdb->query("CREATE TABLE `$table` (`id` bigint NOT NULL PRIMARY KEY,`stamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00') ENGINE=$engine");
    $wpdb->query("INSERT INTO `$table` VALUES (1,'0000-00-00 00:00:00')");
}
// One genuine >16 MiB row plus >474 MiB total, exported by the unmodified plugin.
$wpdb->query('SET GLOBAL max_allowed_packet=268435456');
$wpdb->close();
$wpdb->db_connect();
$wpdb->query('CREATE TABLE wp_fiction_volume (`id` bigint NOT NULL PRIMARY KEY,`payload` longtext) ENGINE=InnoDB');
for ($i = 1; $i <= 480; ++$i) {
    $wpdb->query($wpdb->prepare('INSERT INTO wp_fiction_volume VALUES (%d,%s)', $i, str_repeat('F', 1048576)));
}
$wpdb->query("INSERT INTO wp_fiction_volume VALUES (481,REPEAT('L',18874368))");
if ($wpdb->last_error !== '') {
    throw new RuntimeException('FOURTH_FIXTURE_SQL_FAILED');
}
file_put_contents('/report/fourth-fixture.json', json_encode(['synthetic_only' => true, 'volume_rows' => 481,
    'volume_payload_bytes' => 480 * 1048576 + 18874368, 'large_row_bytes' => 18874368]));
