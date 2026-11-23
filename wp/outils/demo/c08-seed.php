<?php
/** Fixtures strictement fictives C-08, sans paiement ni envoi. */
declare(strict_types=1);
namespace Imagine\Demo\C08;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C-08 requise.');
}
$secret = json_decode(file_get_contents('/var/www/.imagine-demo/seed-secret.json'), true, 512, JSON_THROW_ON_ERROR);
$old = get_option('imagine_c08_fixture', []);
$existingPlan = get_page_by_path('c08-lecture-fictive', OBJECT, 'wc_membership_plan');
$planId = (int) ($old['plan'] ?? ($existingPlan->ID ?? 0));
$planId = wp_insert_post(['ID' => $planId, 'post_type' => 'wc_membership_plan', 'post_status' => 'publish',
    'post_title' => 'C08 — Lecture fictive manuelle', 'post_name' => 'c08-lecture-fictive'], true);
if (is_wp_error($planId)) { throw new \RuntimeException('Plan C08 non créé.'); }
update_post_meta($planId, '_access_method', 'manual-only');
$plans = get_option('imagine_acces_plans', []);
$plans[$planId] = 'abonnement';
update_option('imagine_acces_plans', $plans);
$manifest = ['plan' => $planId, 'users' => [], 'memberships' => [], 'subscriptions' => []];
foreach ($secret['c08_accounts'] as $key => $account) {
    $user = get_user_by('login', $account['login']);
    $userData = ['user_login' => $account['login'],
        'user_email' => $account['login'] . '@example.org', 'user_pass' => $account['password'],
        'role' => 'subscriber', 'display_name' => 'Personnage Fictif C08 ' . $key];
    if ($user) {
        $userData['ID'] = $user->ID;
        $id = wp_update_user($userData);
    } else {
        $id = wp_insert_user($userData);
    }
    if (is_wp_error($id)) { throw new \RuntimeException('Compte C08 non créé.'); }
    // Répare aussi une exécution interrompue; wp_update_user ne rehash pas une valeur
    // égale au champ stocké (cas d'un ancien essai wp_insert_user sur ID existant).
    if (!wp_check_password($account['password'], get_userdata($id)->user_pass, $id)) {
        wp_set_password($account['password'], $id);
    }
    if (!wp_check_password($account['password'], get_userdata($id)->user_pass, $id)) {
        throw new \RuntimeException('Mot de passe fictif non vérifié.');
    }
    $manifest['users'][$key] = $id;
    if ($key === 'sans-droit') { continue; }
    $sub = isset($old['subscriptions'][$key]) ? wcs_get_subscription($old['subscriptions'][$key]) : false;
    if (!$sub) {
        foreach (wcs_get_users_subscriptions($id) as $candidate) {
            if ($candidate->get_meta('_imagine_c08_fixture') === $key) { $sub = $candidate; break; }
        }
    }
    if (!$sub) {
        $sub = wcs_create_subscription(['customer_id' => $id, 'billing_period' => 'year', 'billing_interval' => 1,
            'start_date' => '2026-01-01 00:00:00', 'status' => 'pending']);
    }
    if (is_wp_error($sub)) { throw new \RuntimeException('Abonnement C08 non créé.'); }
    $sub->set_requires_manual_renewal(true);
    $sub->set_payment_method('');
    $sub->set_total('0');
    $sub->update_dates(['start' => '2026-01-01 00:00:00', 'end' => '2030-01-01 00:00:00'], 'gmt');
    $sub->update_meta_data('_imagine_c08_fixture', $key);
    // Fenêtre fictive explicite, pas une nouvelle durée métier décidée par ce lot.
    $sub->update_meta_data('_imagine_acces_grace_debut', $key === 'grace' ? '2026-01-01 00:00:00' : '');
    $sub->update_meta_data('_imagine_acces_grace_fin', $key === 'grace' ? '2030-01-01 00:00:00' : '');
    $sub->save();
    if ($sub->has_status('pending')) {
        $sub->update_status('active', 'Activation initiale fictive C08 sans paiement.');
    }
    $sub->update_status($key === 'grace' ? 'on-hold' : 'active', 'Fixture C08 hors ligne, aucun paiement.');
    $member = wc_memberships_get_user_membership($id, $planId);
    if (!$member) {
        $member = wc_memberships_create_user_membership(['plan_id' => $planId, 'user_id' => $id]);
    }
    if (is_wp_error($member)) { throw new \RuntimeException('Adhésion C08 non créée.'); }
    $member->set_start_date('2026-01-01 00:00:00');
    $member->set_end_date('2030-01-01 00:00:00');
    $member->update_status($key === 'grace' ? 'paused' : 'active');
    update_post_meta($member->get_id(), '_subscription_id', $sub->get_id());
    $manifest['memberships'][$key] = $member->get_id();
    $manifest['subscriptions'][$key] = $sub->get_id();
}
$number = get_option('imagine_demo_manifest')['demo-2026-t1'];
$witness = 'Les lucioles violettes de C08 gardent le secret du village fictif.';
$body = '<p>Début fictif C08. Aucune donnée réelle.</p><p>' . str_repeat('La place imaginaire accueille des histoires inventées. ', 12)
    . '</p><p>' . $witness . '</p><p>' . str_repeat('La rivière des nuages termine ce récit fictif. ', 12) . '</p><p>Fin fictive C08.</p>';
foreach (['article' => 'Extrait public C08 : une histoire entièrement fictive, réservée aux tests de lecture.', 'automatique' => ''] as $key => $excerpt) {
    $id = wp_insert_post(['ID' => (int) ($old[$key] ?? 0), 'post_type' => 'post', 'post_status' => 'publish',
        'post_title' => 'C08 — Article réservé fictif ' . $key, 'post_name' => 'c08-article-reserve-' . $key,
        'post_date' => '2026-01-01 12:00:00', 'post_date_gmt' => '2026-01-01 11:00:00',
        'post_content' => $body, 'post_excerpt' => $excerpt, 'post_password' => $secret['article_password'],
        'comment_status' => 'closed', 'ping_status' => 'closed', 'meta_input' => [
            'imagine_numero_id' => $number, 'imagine_reserve' => '1', 'imagine_c08_fixture' => $key]], true);
    if (is_wp_error($id)) { throw new \RuntimeException('Article C08 non créé.'); }
    $manifest[$key] = $id;
}
update_option('imagine_c08_fixture', $manifest);
$manifest['urls'] = ['article' => get_permalink($manifest['article']), 'automatique' => get_permalink($manifest['automatique'])];
echo wp_json_encode($manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
