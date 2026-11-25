<?php
/** Extension ciblée du reset C09 ; ne réinitialise pas les profils/C12/C14. */
declare(strict_types=1);

function imagine_c16_reset(): array
{
    if (!defined('WP_CLI') || !WP_CLI) {
        throw new RuntimeException('Reset CLI uniquement.');
    }
    \Imagine\Site\CommandeNative::garde();
    $owned = \Imagine\Site\CommandeNative::OWNED;
    $objects = [];
    foreach (['shop_subscription', 'shop_order'] as $type) {
        foreach (wc_get_orders(['type' => $type, 'limit' => -1, 'status' => 'any',
            'meta_key' => $owned, 'meta_value' => '1']) as $object) {
            if ($object->get_meta($owned) !== '1' || $object->get_created_via() !== 'imagine-c16'
                || $object->get_status() !== 'pending' || $object->is_paid() || $object->get_date_paid()
                || $object->get_transaction_id() !== '' || $object->get_refunds() !== []) {
                throw new RuntimeException('Objet C16 modifié ou payé : reset automatique refusé.');
            }
            $objects[$object->get_id()] = $object;
        }
    }
    $users = get_users(['meta_key' => $owned, 'meta_value' => '1']);
    // Prévol entier avant la première suppression ; aucun compte adopté.
    foreach ($users as $user) {
        if ($user->roles !== ['customer'] || wc_memberships_get_user_memberships($user->ID, ['status' => 'any']) !== []) {
            throw new RuntimeException('Compte C16 modifié : refus.');
        }
        foreach (array_merge(wc_get_orders(['customer_id' => $user->ID, 'type' => 'shop_order', 'limit' => -1]),
            array_values(wcs_get_users_subscriptions($user->ID))) as $object) {
            if (!isset($objects[$object->get_id()])) {
                throw new RuntimeException('Objet étranger sur compte C16 : refus.');
            }
        }
    }
    $deleted = ['objects' => array_keys($objects), 'users' => array_map(static fn ($u) => $u->ID, $users), 'transients' => 0];
    foreach ($objects as $object) {
        $object->delete(true);
    }
    require_once ABSPATH . 'wp-admin/includes/user.php';
    foreach ($users as $user) {
        if (!wp_delete_user($user->ID)) {
            throw new RuntimeException('Suppression compte C16 non confirmée.');
        }
    }
    global $wpdb;
    $keys = $wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s",
        $wpdb->esc_like('_transient_imagine_c16_brouillon_') . '%'));
    foreach ($keys as $key) {
        delete_transient(substr($key, strlen('_transient_')));
        $deleted['transients']++;
    }
    return $deleted;
}
