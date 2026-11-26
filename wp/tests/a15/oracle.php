<?php

declare(strict_types=1);

$rows = [];
$summary = [];
require '/subject/a15/Inventory.php';
$byId = [];
foreach (WC()->mailer()->get_emails() as $email) {
    $ref = new ReflectionClass($email);
    $byId[$email->id] = $email;
    $source = $ref->getFileName();
    preg_match('~/wp-content/plugins/([^/]+)/~', $source, $match);
    $owner = isset($match[1]) ? 'plugin:' . $match[1] : 'other';
    $rows[] = ['id' => $email->id, 'extension' => $owner, 'enabled' => $email->is_enabled()];
    $summary[$owner] = ($summary[$owner] ?? 0) + (int) $email->is_enabled();
}
usort($rows, static fn(array $a, array $b): int => $a['id'] <=> $b['id']);
ksort($summary);
$cases = [];
foreach (
    ['customer_refunded_order' => ['subject_partial', 'heading_partial'],
    'customer_invoice' => ['subject_paid', 'heading_paid']] as $id => [$subject, $heading]
) {
    $email = $byId[$id];
    $fields = $email->get_form_fields();
    foreach (['modified', 'subject_only', 'heading_only', 'default', 'empty'] as $mode) {
        $settings = [
            $subject => in_array($mode, ['modified', 'subject_only'], true) ? 'A15_VARIANT_PRIVATE_CANARY'
                : ($mode === 'empty' ? '' : $fields[$subject]['placeholder']),
            $heading => in_array($mode, ['modified', 'heading_only'], true) ? 'A15_HEADING_PRIVATE_CANARY'
                : ($mode === 'empty' ? '' : $fields[$heading]['placeholder']),
        ];
        $shape = \Imagine\EmailInventory\Inventory::shape($email, 'fixture', $settings);
        $cases[$id . ':' . $mode] = [$shape['subject_customised'], $shape['content_customised']];
    }
}
$email = $byId['new_order'];
$default = $email->get_form_fields()['recipient']['default'];
foreach (
    ['absent' => [], 'saved_default' => ['recipient' => strtoupper($default)],
    'different' => ['recipient' => 'a15-other@example.org'],
    'cc_addition' => ['recipient' => $default, 'cc' => 'a15-extra@example.org']] as $label => $settings
) {
    $shape = \Imagine\EmailInventory\Inventory::shape($email, 'fixture', $settings);
    $cases['recipient:' . $label] = $shape['recipient_customised'];
}
echo 'A15_JSON=' . json_encode([
    'emails' => $rows, 'summary' => $summary, 'count' => count($rows),
    'native_shape_cases' => $cases,
    'hpos' => Automattic\WooCommerce\Utilities\OrderUtil::custom_orders_table_usage_is_enabled(),
]) . "\n";
