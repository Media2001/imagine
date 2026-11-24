<?php
/** C13 : deux témoins natifs supplémentaires, distincts de tous les profils C09. */
declare(strict_types=1);
namespace Imagine\Demo\C13;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new \RuntimeException('C13 refuse cette cible.');
}
$owned = '_imagine_c13_fixture';
$manifest = get_option('imagine_c13_fixture', []);
$now = new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
foreach (['BE', 'FR'] as $country) {
    $login = 'c13-postal-' . strtolower($country);
    $user = get_user_by('login', $login);
    if ($user && get_user_meta($user->ID, $owned, true) !== $country) {
        throw new \RuntimeException('Collision de compte C13.');
    }
    $email = get_user_by('email', $login . '@example.org');
    if ($email && (!$user || $email->ID !== $user->ID)) {
        throw new \RuntimeException('Collision email C13.');
    }
    $id = (int) ($manifest[$country] ?? 0);
    $sub = $id ? wcs_get_subscription($id) : null;
    if ($id && (!$sub || $sub->get_meta($owned) !== $country || !$user || $sub->get_customer_id() !== $user->ID)) {
        throw new \RuntimeException('Collision abonnement C13.');
    }
    if ($sub) {
        continue; // Ne jamais réinitialiser un objet existant pour faire passer une recette.
    }
    if (!$user) {
        $uid = wp_insert_user(['user_login' => $login, 'user_email' => $login . '@example.org',
            'user_pass' => wp_generate_password(40, true, true), 'role' => 'customer',
            'display_name' => 'Personnage Fictif C13 ' . $country,
            'meta_input' => [$owned => $country, 'imagine_sans_email' => $country === 'BE' ? '1' : '0']]);
        if (is_wp_error($uid)) { throw new \RuntimeException('Compte témoin C13 indisponible.'); }
        $user = get_userdata($uid);
    }
    $sub = wcs_create_subscription(['customer_id' => $user->ID, 'status' => 'pending',
        'start_date' => $now->format('Y-m-d H:i:s'), 'billing_period' => 'year', 'billing_interval' => 1]);
    if (is_wp_error($sub)) { throw new \RuntimeException('Témoin natif C13 indisponible.'); }
    $sub->update_meta_data($owned, $country);
    $sub->set_requires_manual_renewal(true);
    $sub->set_payment_method('');
    $sub->set_payment_method_title('Aucun paiement — témoin technique C13');
    $sub->set_transaction_id('');
    $sub->set_date_paid(null);
    $sub->set_date_completed(null);
    $sub->set_address(['first_name' => '=Personnage Fictif C13', 'last_name' => $country,
        'address_1' => '13 rue Imaginaire', 'address_2' => '', 'postcode' => $country === 'BE' ? '1000' : '75000',
        'city' => '@Ville Fictive', 'country' => $country], 'shipping');
    $sub->update_dates(['start' => $now->format('Y-m-d H:i:s'),
        'end' => '2027-11-01 00:00:00', 'next_payment' => 0], 'gmt');
    // Fenêtre explicitement fictive pour le test C07 grâce. Aucun règlement simulé.
    $sub->update_meta_data('_imagine_acces_grace_debut', $now->format('Y-m-d H:i:s'));
    $sub->update_meta_data('_imagine_acces_grace_fin', '2027-01-06 00:00:00');
    $sub->set_status('on-hold');
    $sub->save();
    $manifest[$country] = $sub->get_id();
    update_option('imagine_c13_fixture', $manifest, false);
    if (get_option('imagine_c13_fixture') !== $manifest || wcs_get_subscription($sub->get_id())->get_meta($owned) !== $country) {
        throw new \RuntimeException('Témoin C13 non relu.');
    }
}
echo wp_json_encode($manifest);
