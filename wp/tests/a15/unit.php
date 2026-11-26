<?php

declare(strict_types=1);

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$check('inventory_exists', is_file('/subject/a15/Inventory.php'));
if (is_file('/subject/a15/Inventory.php')) {
    require '/subject/a15/Inventory.php';
    // Native WC_Email API deliberately uses snake_case method names.
    // phpcs:disable PSR1.Methods.CamelCapsMethodName.NotCamelCaps
    $email = new class {
        public string $id = 'fixture';
        public bool $block_email_editor_enabled = false;
        public string $title = 'Fictif de contrôle';
        public array $settings = [
            'subject' => 'A15_PRIVATE_SUBJECT_CANARY', 'heading' => '',
            'body' => 'A15_PRIVATE_BODY_CANARY', 'recipient' => 'a15-secret@example.org',
        ];
        public function is_enabled(): bool
        {
            return false;
        }
        public function is_customer_email(): bool
        {
            return false;
        }
        public function get_title(): string
        {
            return $this->title;
        }
        public function get_form_fields(): array
        {
            return [
                'subject' => ['default' => ''], 'heading' => ['default' => ''],
                'body' => ['default' => 'Native default'],
                'subject_full' => ['default' => '', 'placeholder' => 'Full subject default'],
                'subject_partial' => ['default' => '', 'placeholder' => 'Partial subject default'],
                'subject_paid' => ['default' => '', 'placeholder' => 'Paid subject default'],
                'heading_partial' => ['default' => '', 'placeholder' => 'Partial heading default'],
                'recipient' => ['default' => 'admin@example.org,second@example.org'],
            ];
        }
        public function get_default_subject(): string
        {
            return 'Native subject';
        }
        public function get_default_heading(): string
        {
            return 'Native heading';
        }
        public function get_default_body(): string
        {
            return 'Native default';
        }
        public function get_content(): string
        {
            throw new RuntimeException('NEVER_RENDER');
        }
        public function trigger(): void
        {
            throw new RuntimeException('NEVER_TRIGGER');
        }
    };
    // phpcs:enable PSR1.Methods.CamelCapsMethodName.NotCamelCaps
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('disabled_and_internal_personalised', $r['enabled'] === false
        && $r['recipient_nature'] === 'administration' && $r['recipient_customised'] === true);
    $check('subject_body_flags_only', $r['subject_customised'] === true && $r['content_customised'] === true);
    $check('private_values_absent', !preg_match(
        '/@|CANARY|Native subject|Native default/',
        json_encode($r, JSON_THROW_ON_ERROR)
    ));
    $email->settings = ['subject' => 'Native subject', 'body' => 'Native default'];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('explicit_default_not_custom', $r['subject_customised'] === false && $r['content_customised'] === false);
    $email->settings = [];
    $email->title = 'a15-secret@example.org';
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('address_in_title_masked', !str_contains(json_encode($r, JSON_THROW_ON_ERROR), '@'));
    $check('absent_settings_not_custom', $r['subject_customised'] === false
        && $r['content_customised'] === false && $r['recipient_customised'] === false);
    $email->settings = ['subject_partial' => 'A15_VARIANT_PRIVATE_CANARY',
        'heading_partial' => 'A15_HEADING_PRIVATE_CANARY'];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('declared_variants_only_modified', $r['subject_customised'] === true && $r['content_customised'] === true);
    $email->settings = ['subject_partial' => 'Partial subject default',
        'heading_partial' => 'Partial heading default', 'subject_paid' => 'Paid subject default'];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('declared_variants_own_defaults', !$r['subject_customised'] && !$r['content_customised']);
    $email->settings = ['subject_full' => '', 'heading_partial' => '', 'subject_paid' => ''];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('declared_empty_variants_native_fallback', !$r['subject_customised'] && !$r['content_customised']);
    $email->settings = ['recipient' => ' SECOND@example.org ; admin@example.org '];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('saved_default_recipient_list_not_custom', $r['recipient_customised'] === false);
    $email->settings['recipient'] = 'different@example.org';
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('different_recipient_custom', $r['recipient_customised'] === true);
    $email->settings = ['recipient' => 'admin@example.org,second@example.org', 'cc' => 'extra@example.org'];
    $r = \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    $check('cc_addition_separate_from_default_recipient', $r['recipient_customised'] === true);
    $email->block_email_editor_enabled = true;
    $refused = false;
    try {
        \Imagine\EmailInventory\Inventory::shape($email, 'fixture');
    } catch (RuntimeException $error) {
        $refused = $error->getMessage() === 'A15_BLOCK_EDITOR_UNSUPPORTED';
    }
    $check('block_editor_not_misreported_as_unmodified', $refused);
}
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
