<?php

declare(strict_types=1);

require '/subject/staging/lib.php';
require '/subject/staging/pdo-store.php';
$db = getenv('A26_DB');
$pdo = new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=' . $db, 'root', '');
$context = ['environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => $db, 'target_url' => 'https://a02.synthetic.test',
    'production_hosts' => ['production.invalid'], 'table_policy_version' => 1, 'table_decisions' => []];
$option = static fn(string $name): mixed => unserialize((string) $pdo->query(
    'SELECT option_value FROM wp_options WHERE option_name=' . $pdo->quote($name)
)->fetchColumn(), ['allowed_classes' => false]);
$before = $option('active_plugins');
$contentSql = "SELECT ID,post_content FROM wp_posts WHERE post_type='post' ORDER BY ID";
$contents = $pdo->query($contentSql)->fetchAll(PDO::FETCH_KEY_PAIR);
$engine = new Imagine\Staging\Engine(new Imagine\Staging\PdoStore($pdo, $context), $context, 'wp_');
$engine->neutraliser();
$engine->anonymiser(bin2hex(random_bytes(24)));
$after = $option('active_plugins');
$disabled = $option('imagine_staging_disabled_plugins');
$settings = $option('googlesitekit_analytics-4_settings');
$erased = 0;
$afterContents = $pdo->query($contentSql)->fetchAll(PDO::FETCH_ASSOC);
foreach ($afterContents as $row) {
    if (($contents[$row['ID']] ?? '') !== '' && $row['post_content'] === '') {
        $erased++;
    }
}
echo json_encode(['neutraliser_and_anonymiser_executed' => true,
    'marker_present' => is_array($disabled),
    'analytics_removed' => in_array('google-site-kit/google-site-kit.php', $before, true)
        && !in_array('google-site-kit/google-site-kit.php', $after, true)
        && in_array('google-site-kit/google-site-kit.php', $disabled, true),
    'pixel_removed' => in_array('facebook-for-woocommerce/facebook-for-woocommerce.php', $before, true)
        && !in_array('facebook-for-woocommerce/facebook-for-woocommerce.php', $after, true)
        && in_array('facebook-for-woocommerce/facebook-for-woocommerce.php', $disabled, true),
    'measurement_declaration_retained' => ($settings['measurementID'] ?? '') !== '',
    'sensitive_setting_erased' => ($settings['client_id'] ?? null) === '',
    'published_contents_erased' => $erased], JSON_THROW_ON_ERROR) . "\n";
