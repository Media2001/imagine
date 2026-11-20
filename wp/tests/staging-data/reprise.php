<?php

declare(strict_types=1);

// A-01 reprise: fixtures inventées, aucun WordPress ni accès réseau.
require __DIR__ . '/../../outils/staging/lib.php';
require __DIR__ . '/fixtures.php';

function repriseCheck(bool $ok, string $message): void
{
    global $assertions;
    ++$assertions;
    if (!$ok) {
        throw new RuntimeException($message);
    }
}
$assertions = 0;
$context = ['environment'=>'staging', 'isolated'=>true, 'restored'=>true,
    'database'=>'invented_staging', 'target_url'=>'https://invented.test',
    'production_hosts'=>['production.invalid']];
$proof = static fn (): array => ['mail_blocked'=>true, 'http_blocked'=>true,
    'subscriptions_staging'=>true, 'subscriptions_present'=>false,
    'environment_staging'=>true, 'cron_disabled'=>true, 'as_async_disabled'=>true,
    'as_runner_disabled'=>true, 'gateways_disabled'=>true];
$store = fixture();
$plugins = ['woocommerce/woocommerce.php', 'contact-form-7/wp-contact-form-7.php',
    'wordpress-seo/wp-seo.php', 'advanced-custom-fields/acf.php', 'wp-mail-smtp/wp_mail_smtp.php'];
$store->tables['x_options'][] = ['option_id'=>50,'option_name'=>'active_plugins','option_value'=>serialize($plugins)];
$settings = serialize(['title'=>'Réglage fictif', 'layout'=>['columns'=>3], 'email_label'=>'Contact fictif']);
$store->tables['x_options'][] = ['option_id'=>51,'option_name'=>'unrecognized_editor_settings','option_value'=>$settings];
$store->columns['x_extension_catalogue'] = ['id','setting'];
$store->tables['x_extension_catalogue'] = [['id'=>1,'setting'=>'SYNTHETIC layout']];
$store->tables['x_posts'][] = ['ID'=>40,'post_type'=>'wpcf7_contact_form', 'post_content'=>'SYNTHETIC FORM'];
$engine = new Imagine\Staging\Engine($store, $context, 'x_');
$engine->neutraliser();
$options = array_column($store->rows('x_options'), 'option_value', 'option_name');
repriseCheck($options['unrecognized_editor_settings'] === $settings, 'réglages inconnus intacts');
repriseCheck(unserialize($options['active_plugins']) === array_slice($plugins, 0, 4), 'plugins fonctionnels gardés, SMTP seul retiré');
repriseCheck($store->rows('x_extension_catalogue')[0]['setting'] === 'SYNTHETIC layout', 'table inconnue gardée');
$stripe = unserialize($options['woocommerce_stripe_settings']);
repriseCheck($stripe['enabled'] === 'yes' && $stripe['secret_key'] === '' && $stripe['testmode'] === 'yes', 'réglage Stripe conservé sauf clé, mode test');
$engine->anonymiser('SYNTHETIC-test-password-2026');
$report = $engine->verifier($proof);
repriseCheck($report['ok'], 'inconnus sans PII non bloquants');
repriseCheck(in_array('wp-mail-smtp/wp_mail_smtp.php', $report['disabled_plugins'], true), 'désactivation nommée dans rapport');
repriseCheck($report['unknown_tables'][0]['name'] === 'x_extension_catalogue' && $report['unknown_tables'][0]['rows'] === 1, 'inventaire sans valeurs');
repriseCheck(!str_contains(json_encode($report), 'SYNTHETIC layout'), 'aucune valeur de table rapportée');
$private = fixture();
$private->columns['other_contacts'] = ['id', 'email', 'telephone', 'layout'];
$private->tables['other_contacts'] = [['id'=>1,'email'=>'synthetic@outside.invalid','telephone'=>'SYNTHETIC','layout'=>'wide']];
$privateEngine = new Imagine\Staging\Engine($private, $context, 'x_');
$privateEngine->neutraliser();
$privateEngine->anonymiser('SYNTHETIC-test-password-2026');
repriseCheck(in_array('TABLE_PERSONNELLE_A_TRANCHER', $privateEngine->verifier($proof)['issues'], true), 'table personnelle en attente de Ced');
repriseCheck($private->rows('other_contacts')[0]['email'] === 'synthetic@outside.invalid', 'pas de décision fabriquée');
foreach (['garder', 'vider', 'anonymiser'] as $action) {
    $copy = clone $private;
    $decision = ['other_contacts'=>['action'=>$action]];
    if ($action === 'anonymiser') {
        $decision['other_contacts']['columns'] = ['email','telephone'];
    }
    $decided = new Imagine\Staging\Engine($copy, $context, 'x_', $decision);
    $decided->neutraliser();
    $decided->anonymiser('SYNTHETIC-test-password-2026');
    repriseCheck($decided->verifier($proof)['ok'], 'décision synthétique '.$action.' acceptée');
    if ($action === 'garder') {
        repriseCheck($copy->rows('other_contacts') === $private->rows('other_contacts'), 'garder personnel intact');
    } elseif ($action === 'vider') {
        repriseCheck($copy->rows('other_contacts') === [], 'vider appliqué');
    } else {
        repriseCheck($copy->rows('other_contacts')[0]['email'] === 'abonne-1@example.org'
            && $copy->rows('other_contacts')[0]['telephone'] === ''
            && $copy->rows('other_contacts')[0]['layout'] === 'wide', 'colonnes décidées seules anonymisées');
    }
}
foreach (['sk_live_SYNTHETIC_ONLY', 'pk_live_SYNTHETIC_ONLY', 'rk_live_SYNTHETIC_ONLY', 'whsec_SYNTHETIC_ONLY', 'xkeysib-SYNTHETIC_ONLY', 'cus_SYNTHETIC_ONLY', 'pm_SYNTHETIC_ONLY', 'B-SYNTHETICONLY'] as $trap) {
    $store->tables['x_extension_catalogue'][0]['setting'] = $trap;
    repriseCheck(!$engine->verifier($proof)['ok'], 'motif connu partout refusé');
}
$store->tables['x_extension_catalogue'][0]['setting'] = 'SYNTHETIC layout';
$store->tables['x_extension_catalogue'][0]['setting'] = '{"nested":"sk\\u005flive\\u005fSYNTHETIC"}';
repriseCheck(!$engine->verifier($proof)['ok'], 'motif connu JSON échappé refusé');
$store->tables['x_extension_catalogue'][0]['setting'] = 'SYNTHETIC layout';
$store->tables['x_postmeta'][] = ['meta_id'=>999,'post_id'=>1,'meta_key'=>'_paypal_payer_id','meta_value'=>'SYNTHETICOPAQUEID'];
repriseCheck(!$engine->verifier($proof)['ok'], 'identifiant PayPal de champ connu refusé sans préfixe');
array_pop($store->tables['x_postmeta']);
foreach (['mail_blocked'=>'EMAIL_NON_COUPE', 'subscriptions_staging'=>'SUBSCRIPTIONS_NON_STAGING'] as $field=>$issue) {
    $badProof = $proof();
    $badProof['subscriptions_present'] = true;
    $badProof[$field] = false;
    repriseCheck(in_array($issue, $engine->verifier(static fn () => $badProof)['issues'], true), 'preuve refusée : '.$field);
}
$absent = $proof();
$absent['subscriptions_staging'] = null;
repriseCheck($engine->verifier(static fn () => $absent)['ok'], 'Subscriptions absent non bloquant');
$activeSubs = clone $store;
foreach ($activeSubs->tables['x_options'] as &$option) {
    if ($option['option_name'] === 'active_plugins') {
        $option['option_value'] = serialize(['woocommerce-subscriptions/woocommerce-subscriptions.php']);
    }
}
unset($option);
repriseCheck(!(new Imagine\Staging\Engine($activeSubs, $context, 'x_'))->verifier(static fn () => $absent)['ok'], 'plugin Subscriptions actif mais classe absente refusé');
foreach (['x_users'=>'user_email', 'x_wc_orders'=>'billing_email', 'x_wc_order_addresses'=>'email'] as $table=>$column) {
    $original = $store->tables[$table][0][$column];
    $store->tables[$table][0][$column] = 'trap@outside.invalid';
    repriseCheck(in_array('EMAIL_EXTERNE', $engine->verifier($proof)['issues'], true), 'piège email '.$table);
    $store->tables[$table][0][$column] = $original;
}
$store->tables['x_postmeta'][] = ['meta_id'=>998,'post_id'=>2,'meta_key'=>'custom_details','meta_value'=>'{"email":"trap\\u0040outside.invalid"}'];
repriseCheck(in_array('EMAIL_EXTERNE', $engine->verifier($proof)['issues'], true), 'email encodé abonnement classique refusé');
array_pop($store->tables['x_postmeta']);
$store->tables['x_options'][] = ['option_id'=>52,'option_name'=>'synthetic_contact_settings','option_value'=>serialize(['email'=>'contact@outside.invalid', 'font'=>'serif'])];
repriseCheck($engine->verifier($proof)['ok'], 'email option hors comptes commandes : avertissement seulement');
repriseCheck(in_array('EMAIL_HORS_PERIMETRE_COMPTES_COMMANDES', $engine->verifier($proof)['warnings'], true), 'email hors périmètre signalé');
$failedDecision = false;
try { new Imagine\Staging\Engine($private, $context, 'x_', ['other_contacts'=>['action'=>'invented']]); }
catch (RuntimeException) { $failedDecision = true; }
repriseCheck($failedDecision, 'décision invalide refusée, pas normalisée');
$called = false;
$store->tables['x_extension_catalogue'][0]['setting'] = 'sk_live_SYNTHETIC_ONLY';
$engine->verifier(function () use (&$called, $proof) { $called = true; return $proof(); });
repriseCheck(!$called, 'aucune sonde avant blocages offline');
$store->tables['x_extension_catalogue'][0]['setting'] = 'SYNTHETIC layout';
repriseCheck(!$engine->verifier(function () use ($store, $proof) {
    $store->tables['x_extension_catalogue'][0]['setting'] = 'sk_live_SYNTHETIC_ONLY';
    return $proof();
})['ok'], 'secret apparu pendant bootstrap détecté après');
$store->tables['x_extension_catalogue'][0]['setting'] = 'SYNTHETIC layout';
// Configurations connues : retirer les champs secrets, jamais tout le réglage.
$providers = clone $store;
$providers->tables['x_options'][] = ['option_id'=>60,'option_name'=>'woocommerce-ppcp-settings','option_value'=>serialize([
    'sandbox_on'=>false, 'client_id'=>'SYNTHETIC_OPAQUE_CLIENT', 'client_secret'=>'SYNTHETIC_OPAQUE_SECRET',
    'title'=>'PayPal fictif', 'smart_button_locations'=>['checkout']])];
$providers->tables['x_options'][] = ['option_id'=>61,'option_name'=>'synthetic_mailin','option_value'=>serialize([
    'api-key'=>'SYNTHETIC_OPAQUE_KEY', 'list_id'=>17, 'enabled'=>true])];
$providerEngine = new Imagine\Staging\Engine($providers, $context, 'x_');
$providerEngine->neutraliser();
$providerOptions = array_column($providers->rows('x_options'), 'option_value', 'option_name');
$paypal = unserialize($providerOptions['woocommerce-ppcp-settings']);
repriseCheck($paypal['sandbox_on'] === true && $paypal['client_id'] === '' && $paypal['client_secret'] === ''
    && $paypal['title'] === 'PayPal fictif' && $paypal['smart_button_locations'] === ['checkout'], 'PayPal PPCP sandbox sans credentials, fonctionnel intact');
$mailin = unserialize($providerOptions['synthetic_mailin']);
repriseCheck($mailin['api-key'] === '' && $mailin['list_id'] === 17 && $mailin['enabled'] === true, 'clé Brevo opaque retirée seule');
print("OK $assertions assertions reprise\n");
