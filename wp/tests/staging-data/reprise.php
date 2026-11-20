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
print("OK $assertions assertions reprise\n");
