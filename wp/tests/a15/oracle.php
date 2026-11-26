<?php

declare(strict_types=1);

$rows = [];
$summary = [];
foreach (WC()->mailer()->get_emails() as $email) {
    $ref = new ReflectionClass($email);
    $source = $ref->getFileName();
    preg_match('~/wp-content/plugins/([^/]+)/~', $source, $match);
    $owner = isset($match[1]) ? 'plugin:' . $match[1] : 'other';
    $rows[] = ['id' => $email->id, 'extension' => $owner, 'enabled' => $email->is_enabled()];
    $summary[$owner] = ($summary[$owner] ?? 0) + (int) $email->is_enabled();
}
usort($rows, static fn(array $a, array $b): int => $a['id'] <=> $b['id']);
ksort($summary);
echo 'A15_JSON=' . json_encode([
    'emails' => $rows, 'summary' => $summary, 'count' => count($rows),
    'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),
]) . "\n";
