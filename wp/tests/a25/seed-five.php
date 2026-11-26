<?php

declare(strict_types=1);

global $wpdb;
for ($i = 0; $i < 5; $i++) {
    wp_insert_comment(['comment_post_ID' => 1, 'comment_author' => 'A25_FIVE_PRIVATE_CANARY',
        'comment_author_email' => 'a25-five@example.org', 'comment_author_IP' => '192.0.2.42',
        'comment_content' => 'A25_FIVE_BODY_PRIVATE_CANARY', 'comment_date' => '2000-01-01 00:30:00',
        'comment_date_gmt' => '1999-12-31 23:30:00', 'comment_approved' => '1', 'user_id' => 0]);
    $order = wc_create_order(['customer_id' => 0]);
    $order->set_date_created('1999-06-01 12:00:00');
    $order->save();
    $wpdb->insert($wpdb->prefix . 'fluentform_submissions', ['form_id' => 1,
        'response' => 'A25_FIVE_FORM_PRIVATE_CANARY', 'created_at' => '1999-06-01 12:00:00']);
}
echo "A25_FIVE_OK\n";
