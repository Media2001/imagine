<?php

declare(strict_types=1);

add_filter('pre_wp_mail', '__return_false', PHP_INT_MAX);
$admin = wp_insert_user(['user_login' => 'A17_LOGIN_PRIVATE_CANARY', 'user_email' => 'a17-fictif@example.org',
    'user_pass' => wp_generate_password(40), 'role' => 'administrator']);
add_role('a17_gestion', 'A17 nom prive', ['read' => true, 'manage_imagine' => true]);
foreach (['a17_gestion', 'editor', 'shop_manager'] as $role) {
    wp_insert_user(['user_login' => 'a17-fictif-' . $role, 'user_email' => 'a17-' . $role . '@example.org',
        'user_pass' => wp_generate_password(40), 'role' => $role]);
}
\WP_Application_Passwords::create_new_application_password($admin, ['name' => 'A17_APP_PRIVATE_CANARY']);
update_user_meta($admin, '_a17_fixture_two_factor', true);
update_user_meta($admin, 'wp-last-login', strtotime('2025-01-01T12:00:00Z'));
$first = get_users(['role' => 'administrator', 'exclude' => [$admin]])[0];
update_user_meta($first->ID, 'wp-last-login', strtotime('2026-11-01T12:00:00Z'));
foreach (['edit_users', 'update_plugins', 'switch_themes'] as $cap) {
    $role = 'a17_' . $cap;
    add_role($role, 'Fictif', ['read' => true, $cap => true]);
    wp_insert_user(['user_login' => 'a17-fictif-' . $role, 'user_email' => $role . '@example.org',
        'user_pass' => wp_generate_password(40), 'role' => $role]);
}
add_role('a17_content_only', 'Fictif contenu', ['read' => true, 'edit_posts' => true, 'publish_posts' => true]);
wp_insert_user(['user_login' => 'a17-fictif-contenu', 'user_email' => 'contenu@example.org',
    'user_pass' => wp_generate_password(40), 'role' => 'a17_content_only']);
foreach (['boundary' => '2025-11-26T12:00:00Z', 'future' => '2026-11-26T12:00:01Z'] as $label => $date) {
    $id = wp_insert_user(['user_login' => 'a17-fictif-' . $label, 'user_email' => $label . '@example.org',
        'user_pass' => wp_generate_password(40), 'role' => 'editor']);
    update_user_meta($id, 'wp-last-login', strtotime($date));
}
update_option('users_can_register', 1);
update_option('default_role', 'subscriber');
$active = get_option('active_plugins');
$active[] = 'two-factor/two-factor.php';
$active[] = 'other-2fa/other-2fa.php';
update_user_meta(get_users(['role' => 'shop_manager'])[0]->ID, '_other_2fa_enabled', true);
$active[] = 'wp-last-login/wp-last-login.php';
$active[] = 'limit-login-attempts-reloaded/limit-login-attempts-reloaded.php';
update_option('active_plugins', $active);
echo "A17_SEED_OK\n";
