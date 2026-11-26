<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
global $wpdb;
foreach (get_users() as $existing) {
    $existing->set_role('administrator');
}
add_role('a23_operator', 'Fictitious role', ['read' => true, 'edit_users' => true]);
$ids = [];
for ($i = 0; $i < 32; $i++) {
    $id = wp_insert_user(['user_login' => 'a23-fictif-' . $i,
        'user_email' => 'a23-fictif-' . $i . '@example.org', 'role' => 'customer',
        'user_pass' => wp_generate_password(40), 'display_name' => 'A23_NAME_PRIVATE_CANARY']);
    if (is_wp_error($id)) {
        throw new RuntimeException('A23_SEED_FAILED');
    }
    $ids[] = $id;
    $email = match (true) {
        $i < 5 => '', $i < 10 => 'A23_EMAIL_PRIVATE_CANARY_' . $i,
        $i < 15 => 'shared-' . ($i - 10) . '@example.org',
        $i < 20 => 'SHARED-' . ($i - 15) . '@example.org',
        default => 'a23-fictif-' . $i . '@example.org',
    };
    $login = match (true) {
        $i < 5 => 'Case' . $i, $i >= 25 && $i < 30 => 'cASE' . ($i - 25),
        $i >= 10 && $i < 15, $i >= 20 && $i < 25 => $email,
        $i === 30 => 'A23_LOGIN_PRIVATE_CANARY', default => 'a23-fictif-' . $i,
    };
    $hash = match (true) {
        $i < 10 => '$P$A23_HASH_FRAGMENT_PRIVATE_CANARY',
        $i < 30 => '$wp$2y$A23_HASH_FRAGMENT_PRIVATE_CANARY',
        $i === 30 => 'A23_HASH_UNKNOWN_PRIVATE_CANARY', default => '',
    };
    // Deliberately impossible values inserted only into this disposable fixture.
    $wpdb->update($wpdb->users, ['user_login' => $login, 'user_email' => $email, 'user_pass' => $hash], ['ID' => $id]);
    clean_user_cache($id);
    if ($i < 27) {
        $s = wcs_create_subscription(['customer_id' => $id, 'status' => 'pending',
            'billing_period' => 'year', 'billing_interval' => 1, 'start_date' => '2026-01-01 00:00:00']);
        if (is_wp_error($s)) {
            throw new RuntimeException('A23_SEED_FAILED');
        }
        $status = match (true) {
            $i < 5 => 'active', $i < 10 => 'pending', $i < 15 => 'on-hold',
            $i < 20 => 'pending-cancel', $i < 25 => 'expired', default => 'cancelled',
        };
        $s->set_requires_manual_renewal(true);
        $s->save();
        if ($status !== 'pending') {
            $s->update_status('active');
            $s->update_status($status);
        }
    } elseif ($i < 29) {
        $order = wc_create_order(['customer_id' => $id]);
        $order->set_status('pending');
        $order->save();
    }
}
// Two living subscriptions must not count as two readers.
$s = wcs_create_subscription(['customer_id' => $ids[0], 'status' => 'pending',
    'billing_period' => 'year', 'billing_interval' => 1]);
if (is_wp_error($s)) {
    throw new RuntimeException('A23_SEED_FAILED');
}
foreach (['editor', 'shop_manager', 'a23_operator', 'subscriber'] as $i => $role) {
    $id = wp_insert_user(['user_login' => 'a23-admin-fictif-' . $i,
        'user_email' => 'a23-admin-fictif-' . $i . '@example.org', 'role' => $role,
        'user_pass' => wp_generate_password(40)]);
    if (is_wp_error($id)) {
        throw new RuntimeException('A23_SEED_FAILED');
    }
    if ($role === 'subscriber') {
        (new WP_User($id))->add_cap('manage_a23_private_fixture');
    }
    if ($role === 'editor') {
        $wpdb->update($wpdb->users, ['user_email' => 'a23-fictif-31@example.org'], ['ID' => $id]);
    }
}
// Regression P1: five masked role holders would wrongly publish a bcrypt group.
$roleFixtures = ['negative_override' => true, 'multi_role' => false];
for ($i = 0; $i < 6; $i++) {
    $multiple = $i === 5;
    $id = wp_insert_user(['user_login' => 'a23-role-fictif-' . $i,
        'user_email' => 'a23-role-fictif-' . $i . '@example.org',
        'role' => $multiple ? 'customer' : 'a23_operator',
        'user_pass' => wp_generate_password(40), 'display_name' => 'A23_ROLE_NAME_PRIVATE_CANARY']);
    if (is_wp_error($id)) {
        throw new RuntimeException('A23_SEED_FAILED');
    }
    $user = new WP_User($id);
    if ($multiple) {
        $user->add_role('a23_operator');
    }
    $user->add_cap('edit_users', false);
    $wpdb->update($wpdb->users, ['user_pass' => '$2y$A23_ROLE_HASH_PRIVATE_CANARY'], ['ID' => $id]);
    clean_user_cache($id);
    $user = new WP_User($id);
    $masked = in_array('a23_operator', $user->roles, true)
        && ($user->allcaps['edit_users'] ?? null) === false
        && wp_roles()->roles['a23_operator']['capabilities']['edit_users'] === true;
    if ($multiple) {
        $roleFixtures['multi_role'] = $masked && count($user->roles) === 2
            && in_array('customer', $user->roles, true);
    } else {
        $roleFixtures['negative_override'] = $roleFixtures['negative_override'] && $masked;
    }
    // Three masked users and the multiple-role user have a living contract;
    // two masked users have no commerce. Both published totals must stay unchanged.
    if ($i < 3 || $multiple) {
        $s = wcs_create_subscription(['customer_id' => $id, 'status' => 'pending',
            'billing_period' => 'year', 'billing_interval' => 1]);
        if (is_wp_error($s)) {
            throw new RuntimeException('A23_SEED_FAILED');
        }
        $s->set_requires_manual_renewal(true);
        $s->save();
    }
}
if (in_array(false, $roleFixtures, true)) {
    throw new RuntimeException('A23_SEED_FAILED');
}
echo 'A23_ROLE_FIXTURES ' . json_encode($roleFixtures, JSON_THROW_ON_ERROR) . "\n";
echo "A23_SEED_OK\n";
