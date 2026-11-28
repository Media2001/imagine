<?php

declare(strict_types=1);

use Imagine\Site\DomainesRefuses;
use Imagine\Site\DomainesRefusesRegles;
use Imagine\Site\DomainesRefusesReglages;

if (!class_exists(DomainesRefuses::class)) {
    throw new RuntimeException('C31 absent');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException($name);
    }
};
$domains = ['jetable-fictif.example.org', 'temporaire-fictif.example.org', 'usage-unique-fictif.example.org'];
update_option(DomainesRefuses::OPTION, $domains, false);
$check('liste_relue', DomainesRefuses::configuration() === $domains);
$refused = [];
foreach (['wp' => 'register_new_user', 'woo' => 'wc_create_new_customer'] as $path => $function) {
    $email = 'c31-refus-' . $path . '@JETABLE-FICTIF.example.org';
    $refused[] = $email;
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
// Sauvegardes Mon compte : vrais POST HTTP dans c31-compte.py, pas d'assertion vacante ici.
$admin = wp_insert_user(['user_login' => 'fictif-c31-admin', 'user_email' => 'c31-admin@jetable-fictif.example.org', 'user_pass' => wp_generate_password(48), 'role' => 'customer']);
$check('administration_hors_filtre', !is_wp_error($admin) && get_userdata($admin)->user_email === 'c31-admin@jetable-fictif.example.org');
global $wpdb;
// Toutes les colonnes textuelles de toutes les tables du préfixe courant.
$columns = [];
$tables = $wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s', $wpdb->esc_like($wpdb->prefix) . '%'));
foreach ($tables as $table) {
    if (!preg_match('/^[A-Za-z0-9_]+$/D', $table)) {
        throw new RuntimeException('Nom de table non sûr');
    }
    foreach ($wpdb->get_results("SHOW COLUMNS FROM `{$table}`", ARRAY_A) as $column) {
        if (preg_match('/char|text|blob|binary|json|enum|set/i', $column['Type'])) {
            $columns[$table][] = $column['Field'];
        }
    }
}
$check('stockages_non_vides', count($columns) > 10);
foreach (['users', 'usermeta', 'options', 'posts', 'postmeta', 'woocommerce_sessions', 'wc_orders', 'wc_order_addresses', 'wc_orders_meta', 'wc_customer_lookup'] as $suffix) {
    $check('stockage_present_' . $suffix, !empty($columns[$wpdb->prefix . $suffix]));
}
$scan = static function (string $email) use ($wpdb, $columns): array {
    $hits = [];
    foreach ($columns as $table => $fields) {
        foreach ($fields as $field) {
            if (!preg_match('/^[A-Za-z0-9_]+$/D', $field)) {
                throw new RuntimeException('Nom de colonne non sûr');
            }
            $count = $wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM `{$table}` WHERE `{$field}` LIKE %s", '%' . $wpdb->esc_like($email) . '%'));
            if ($wpdb->last_error !== '') {
                throw new RuntimeException('Lecture SQL indisponible');
            }
            if ((int) $count > 0) {
                $hits[$table . '.' . $field] = (int) $count;
            }
        }
    }
    return $hits;
};
$witness = 'c31-detection@example.org';
add_option('imagine_c31_detection', $witness, '', false);
update_user_meta((int) $empty, 'imagine_c31_detection', $witness);
$wpdb->insert($wpdb->prefix . 'woocommerce_sessions', ['session_key' => 'c31-detection', 'session_value' => serialize(['billing_email' => $witness]), 'session_expiry' => time() + 300]);
$order = new WC_Order();
$order->set_billing_email($witness);
$order->set_status('pending');
$order->save();
$positive = $scan($witness);
foreach (['options', 'usermeta', 'woocommerce_sessions', 'wc_orders', 'wc_order_addresses'] as $suffix) {
    $check('mutation_stockage_detectee_' . $suffix, count(array_filter(array_keys($positive), static fn ($name) => str_starts_with($name, $wpdb->prefix . $suffix . '.'))) > 0);
}
wp_set_current_user(0);
wc_load_cart();
WC()->cart->empty_cart();
$product = new WC_Product_Simple();
$product->set_name('FICTIF C31 recette commande');
$product->set_regular_price('0');
$product->set_virtual(true);
$product->save();
$check('vrai_panier_non_vide', WC()->cart->add_to_cart($product->get_id()) !== false && !WC()->cart->is_empty());
update_option('woocommerce_enable_signup_and_login_from_checkout', 'yes');
$checkoutEmail = 'c31-refus-checkout@jetable-fictif.example.org';
$refused[] = $checkoutEmail;
$_POST = wp_slash([
    'billing_first_name' => 'Fictif',
    'billing_last_name' => 'C31',
    'billing_country' => 'BE',
    'billing_address_1' => '1 rue fictive',
    'billing_city' => 'Fictif',
    'billing_postcode' => '1000',
    'billing_phone' => '020000000',
    'billing_email' => $checkoutEmail,
    'createaccount' => '1',
    'account_username' => 'fictif-c31-checkout',
    'account_password' => wp_generate_password(48),
    'terms' => '1',
]);
$_REQUEST['woocommerce-process-checkout-nonce'] = wp_create_nonce('woocommerce-process_checkout');
wc_clear_notices();
$ordersBefore = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_orders");
WC()->checkout()->process_checkout();
WC()->session->save_data();
$notices = wp_json_encode(wc_get_notices('error'));
if (!str_contains($notices, 'autre adresse email')) {
    echo wp_json_encode(['checkout_notices' => wc_get_notices('error'), 'checkout_leaks' => $scan($checkoutEmail)]);
}
$check('checkout_vrai_process_message_refus', str_contains($notices, 'autre adresse email'));
$check('checkout_aucun_compte', get_user_by('email', $checkoutEmail) === false && username_exists('fictif-c31-checkout') === false);
$check('checkout_aucune_commande', (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_orders") === $ordersBefore);
$leaks = $scan($checkoutEmail);
if ($leaks !== []) {
    echo wp_json_encode(['checkout_leaks' => $leaks]);
}
$check('checkout_adresse_absente_toutes_tables', $leaks === []);
// La page de démonstration utilise aussi le checkout Blocks/Store API natif.
$storeEmail = 'c31-refus-store@jetable-fictif.example.org';
$refused[] = $storeEmail;
$request = new WP_REST_Request('POST', '/wc/store/v1/checkout');
$request->set_header('Content-Type', 'application/json');
$request->set_header('Nonce', wp_create_nonce('wc_store_api'));
$request->set_body(wp_json_encode([
    'create_account' => true,
    'billing_address' => ['first_name' => 'Fictif', 'last_name' => 'C31', 'country' => 'BE', 'address_1' => '1 rue fictive', 'city' => 'Fictif', 'postcode' => '1000', 'email' => $storeEmail, 'phone' => '020000000'],
    'payment_method' => '',
]));
$response = rest_do_request($request);
WC()->session->save_data();
$storeData = $response->get_data();
$storeLeaks = $scan($storeEmail);
if ($storeLeaks !== [] || !str_contains(wp_json_encode($storeData), 'autre adresse email')) {
    echo wp_json_encode(['store_status' => $response->get_status(), 'store_result' => $storeData, 'store_leaks' => $storeLeaks]);
}
$check('store_vrai_checkout_message_refus', $response->get_status() === 400 && str_contains(wp_json_encode($storeData), 'autre adresse email'));
$check('store_aucun_compte', get_user_by('email', $storeEmail) === false);
$check('store_adresse_absente_toutes_tables', $storeLeaks === []);
$check('store_aucune_commande', (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_orders") === $ordersBefore);
$mutantEmail = 'c31-mutant@jetable-fictif.example.org';
remove_filter('woocommerce_registration_errors', [DomainesRefuses::class, 'inscription'], 30);
try {
    $mutant = wc_create_new_customer($mutantEmail, 'fictif-c31-mutant', wp_generate_password(48));
} finally {
    add_filter('woocommerce_registration_errors', [DomainesRefuses::class, 'inscription'], 30, 3);
}
$check('mutation_aucun_compte_detectee', !is_wp_error($mutant) && get_user_by('email', $mutantEmail) !== false);
// Nettoyage ciblé dans la transaction de recette ; les hooks C21 d'effacement
// ouvrent leur propre transaction et ne sont pas le sujet de ce canari.
$wpdb->delete($wpdb->usermeta, ['user_id' => (int) $mutant]);
$wpdb->delete($wpdb->users, ['ID' => (int) $mutant]);
clean_user_cache((int) $mutant);
$check('mutation_compte_retire_relu', get_user_by('email', $mutantEmail) === false);
foreach ($refused as $i => $email) {
    $check('adresse_absente_toutes_tables_' . $i, $scan($email) === []);
}
$journalBefore = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%'");
update_option(DomainesRefuses::OPTION, ['journal-fictif.example.org'], false);
$check('journal_liste_ecrit', (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->options} WHERE option_name LIKE 'imagine_reglages_journal_%'") === $journalBefore + 1);
$blockJournal = static fn (string $sql): string => str_starts_with($sql, 'INSERT') && str_contains($sql, 'imagine_reglages_journal_') ? 'SELECT 1' : $sql;
add_filter('query', $blockJournal);
try {
    update_option(DomainesRefuses::OPTION, ['refus-fictif.example.org'], false);
} finally {
    remove_filter('query', $blockJournal);
}
$check('journal_echec_restaure', DomainesRefuses::configuration() === ['journal-fictif.example.org']);
$check('antislash_domaine_refuse', DomainesRefusesRegles::liste("jetable-fictif\\.example.org") === null);
$check('source_wp_woo_reelle', (new ReflectionFunction('register_new_user'))->getFileName() !== false && (new ReflectionFunction('wc_create_new_customer'))->getFileName() !== false);
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'storage_tables' => count($columns), 'storage_columns' => array_sum(array_map('count', $columns)), 'positive_detection' => $positive, 'checkout_leaks' => $leaks]);
