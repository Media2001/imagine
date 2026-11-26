<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
update_option('woocommerce_customer_on_hold_order_settings', ['enabled' => 'no', 'subject' => 'A15_SUBJECT_PRIVATE_CANARY', 'additional_content' => 'A15_BODY_PRIVATE_CANARY']);
update_option('woocommerce_new_order_settings', ['enabled' => 'yes', 'recipient' => 'a15-recipient-canary@example.org', 'subject' => 'A15_ADMIN_SUBJECT_PRIVATE_CANARY']);
$active = get_option('active_plugins');
$active[] = 'a15-smtp/a15-smtp.php';
update_option('active_plugins', $active);
$plans = wc_memberships_get_membership_plans();
$plan = reset($plans);
if (!$plan || !$plan->set_email_content('WC_Memberships_User_Membership_Activated_Email', 'A15_PLAN_BODY_PRIVATE_CANARY')) {
    throw new RuntimeException('A15_NATIVE_PLAN_SEED_FAILED');
}
echo "A15_SEED_OK\n";
