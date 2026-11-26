<?php

declare(strict_types=1);

// Oracle/setup only, never runs with subject credentials.
add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
global $wpdb;
foreach ($wpdb->get_col("SELECT comment_ID FROM {$wpdb->comments}") as $id) {
    wp_delete_comment((int) $id, true);
}
$person = (int) get_user_by('login', 'a02-fictif')->ID;
foreach (
    [['2023-12-31 23:30:00', '1', true, false], ['2024-06-01 12:00:00', '0', false, true],
    ['2024-07-01 12:00:00', 'spam', true, false]] as [$date, $state, $address, $account]
) {
    $id = wp_insert_comment(['comment_post_ID' => 1, 'comment_author' => 'A25_PERSON_PRIVATE_CANARY',
        'comment_author_email' => $address ? 'a25-fictif@example.org' : '',
        'comment_author_IP' => $address ? '192.0.2.41' : '', 'comment_content' => 'A25_COMMENT_PRIVATE_CANARY',
        'comment_date' => '2024-01-01 00:30:00', 'comment_date_gmt' => $date,
        'comment_approved' => $state, 'comment_type' => 'comment', 'user_id' => $account ? $person : 0]);
    if (!$id) {
        throw new RuntimeException('A25_SEED_COMMENT');
    }
}
foreach ([2023, 2024] as $year) {
    $order = wc_create_order(['customer_id' => 0]);
    $order->set_date_created($year . '-06-01 12:00:00');
    $order->set_billing_email('a25-guest@example.org');
    $order->set_billing_first_name('A25_GUEST_PRIVATE_CANARY');
    $order->save();
    if ($order->get_customer_id() !== 0) {
        throw new RuntimeException('A25_SEED_ORDER');
    }
}
$wpdb->query("CREATE TABLE {$wpdb->prefix}fluentform_submissions (id bigint unsigned PRIMARY KEY AUTO_INCREMENT,
    form_id int unsigned NULL, response longtext NULL, created_at timestamp NULL,
    updated_at timestamp NULL) ENGINE=InnoDB");
$wpdb->query("CREATE TABLE {$wpdb->prefix}a25_unknown_entries (id bigint PRIMARY KEY, form_id int,
    message longtext, submitted_at datetime) ENGINE=InnoDB");
foreach ([2023, 2024] as $i => $year) {
    $wpdb->insert($wpdb->prefix . 'fluentform_submissions', ['form_id' => 1,
        'response' => json_encode(['message' => 'A25_FORM_PRIVATE_CANARY', 'email' => 'a25-form@example.org']),
        'created_at' => $year . '-06-01 12:00:00']);
    $wpdb->insert($wpdb->prefix . 'a25_unknown_entries', ['id' => $i + 1, 'form_id' => 2,
        'message' => 'A25_UNKNOWN_FORM_PRIVATE_CANARY', 'submitted_at' => $year . '-06-01 12:00:00']);
}
$wpdb->query("CREATE TABLE {$wpdb->prefix}a25_submission_entries (submission_id bigint PRIMARY KEY, form_id int,
    response longtext, created_at datetime) ENGINE=InnoDB");
$wpdb->query("CREATE TABLE {$wpdb->prefix}a25_submission_details (id bigint PRIMARY KEY, submission_id bigint,
    form_id int, message longtext, created_at datetime, KEY (submission_id)) ENGINE=InnoDB");
for ($i = 1; $i <= 5; $i++) {
    if (
        $wpdb->insert($wpdb->prefix . 'a25_submission_entries', ['submission_id' => $i, 'form_id' => 3,
        'response' => 'A25_PK_MESSAGE_PRIVATE_CANARY', 'created_at' => '2022-06-01 12:00:00']) !== 1
    ) {
        throw new RuntimeException('A25_SEED_SUBMISSION_PK');
    }
    // Two details per message: counting this table would inflate five messages to fifteen.
    foreach ([1, 2] as $detail) {
        if (
            $wpdb->insert($wpdb->prefix . 'a25_submission_details', ['id' => $i * 2 + $detail,
            'submission_id' => $i, 'form_id' => 3, 'message' => 'A25_CHILD_MESSAGE_PRIVATE_CANARY',
            'created_at' => '2022-06-01 12:00:00']) !== 1
        ) {
            throw new RuntimeException('A25_SEED_SUBMISSION_CHILD');
        }
    }
}
echo "A25_SEED_OK\n";
