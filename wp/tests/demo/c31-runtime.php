<?php

declare(strict_types=1);

use Imagine\Site\DomainesRefuses;
use Imagine\Site\DomainesRefusesRegles;
use Imagine\Site\DomainesRefusesReglages;

if (!class_exists(DomainesRefuses::class)) { throw new RuntimeException('C31 absent'); }
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void { $checks[$name] = $ok;if (!$ok) { throw new RuntimeException($name); } };
$domains = ['jetable-fictif.example.org', 'temporaire-fictif.example.org', 'usage-unique-fictif.example.org'];
update_option(DomainesRefuses::OPTION, $domains, false);
$check('liste_relue', DomainesRefuses::configuration() === $domains);
$refused = [];
foreach (['wp' => 'register_new_user', 'woo' => 'wc_create_new_customer'] as $path => $function) {
    $email = 'c31-refus-' . $path . '@JETABLE-FICTIF.example.org';$refused[] = $email;
    $result = $path === 'wp' ? register_new_user('fictif-c31-' . $path, $email) : wc_create_new_customer($email, 'fictif-c31-' . $path, wp_generate_password(48));
    $check($path . '_refus_natif', is_wp_error($result) && in_array('imagine_adresse_alternative', $result->get_error_codes(), true));
    $check($path . '_aucun_compte', get_user_by('email', $email) === false && username_exists('fictif-c31-' . $path) === false);
    $okEmail = 'c31-ok-' . $path . '@example.org';
    $ok = $path === 'wp' ? register_new_user('fictif-c31-ok-' . $path, $okEmail) : wc_create_new_customer($okEmail, 'fictif-c31-ok-' . $path, wp_generate_password(48));
    $check($path . '_accepte_natif', !is_wp_error($ok) && get_userdata($ok)->user_email === $okEmail);
}
$check('sous_domaine_non_herite', !DomainesRefusesRegles::refuse('fictif@sub.jetable-fictif.example.org', $domains));
update_option(DomainesRefuses::OPTION, [], false);
$emptyEmail = 'c31-vide@jetable-fictif.example.org';
$empty = wc_create_new_customer($emptyEmail, 'fictif-c31-vide', wp_generate_password(48));
$check('liste_vide_accepte', !is_wp_error($empty) && get_userdata($empty)->user_email === $emptyEmail);
update_option(DomainesRefuses::OPTION, $domains, false);
$check('existant_reste_intact', get_userdata($empty)->user_email === $emptyEmail);
$error = new WP_Error();
DomainesRefuses::compte($error, (object)['ID' => $empty, 'user_email' => $emptyEmail]);
$check('email_existant_inchange_accepte', !$error->has_errors());
$newEmail = 'c31-changement@jetable-fictif.example.org';$refused[] = $newEmail;
$error = new WP_Error();
do_action('woocommerce_save_account_details_errors', $error, (object)['ID' => $empty, 'user_email' => $newEmail]);
$check('changement_adresse_refuse', in_array('imagine_adresse_alternative', $error->get_error_codes(), true) && get_userdata($empty)->user_email === $emptyEmail);
$admin = wp_insert_user(['user_login' => 'fictif-c31-admin', 'user_email' => 'c31-admin@jetable-fictif.example.org', 'user_pass' => wp_generate_password(48), 'role' => 'customer']);
$check('administration_hors_filtre', !is_wp_error($admin) && get_userdata($admin)->user_email === 'c31-admin@jetable-fictif.example.org');
global $wpdb;
foreach ($refused as $email) {
    foreach ([$wpdb->users => ['user_email'], $wpdb->usermeta => ['meta_value'], $wpdb->options => ['option_value']] as $table => $columns) {
        foreach ($columns as $column) {
            $found = $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$table} WHERE {$column} LIKE %s", '%' . $wpdb->esc_like($email) . '%'));
            $check('adresse_absente_' . count($checks), $wpdb->last_error === '' && (int)$found === 0);
        }
    }
}
// Même fabrique utilisée par WC_Checkout::process_customer, avec un vrai refus.
wp_set_current_user(0);
$checkoutEmail = 'c31-refus-checkout@jetable-fictif.example.org';$refused[] = $checkoutEmail;
$thrown = false;
try {
    $checkout = new WC_Checkout();
    $create = new ReflectionMethod($checkout, 'process_customer');
    $create->invoke($checkout, ['createaccount' => 1, 'billing_email' => $checkoutEmail, 'account_username' => 'fictif-c31-checkout', 'account_password' => wp_generate_password(48)]);
} catch (Exception $e) { $thrown = str_contains($e->getMessage(), 'autre adresse email'); }
$check('checkout_refus_natif', $thrown && get_user_by('email', $checkoutEmail) === false);
$mutantEmail = 'c31-mutant@jetable-fictif.example.org';
remove_filter('woocommerce_registration_errors', [DomainesRefuses::class, 'inscription'], 30);
try { $mutant = wc_create_new_customer($mutantEmail, 'fictif-c31-mutant', wp_generate_password(48)); }
finally { add_filter('woocommerce_registration_errors', [DomainesRefuses::class, 'inscription'], 30, 3); }
$check('mutation_aucun_compte_detectee', !is_wp_error($mutant) && get_user_by('email', $mutantEmail) !== false);
// Nettoyage ciblé dans la transaction de recette ; les hooks C21 d'effacement
// ouvrent leur propre transaction et ne sont pas le sujet de ce canari.
$wpdb->delete($wpdb->usermeta, ['user_id' => (int)$mutant]);
$wpdb->delete($wpdb->users, ['ID' => (int)$mutant]);
clean_user_cache((int)$mutant);
$check('mutation_compte_retire_relu', get_user_by('email', $mutantEmail) === false);
$check('antislash_domaine_refuse', DomainesRefusesRegles::liste("jetable-fictif\\.example.org") === null);
$check('source_wp_woo_reelle', (new ReflectionFunction('register_new_user'))->getFileName() !== false && (new ReflectionFunction('wc_create_new_customer'))->getFileName() !== false);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
