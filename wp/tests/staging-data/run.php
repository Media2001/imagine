<?php

declare(strict_types=1);

// Données intégralement inventées. Aucun WordPress, réseau ou serveur SQL.
require __DIR__ . '/../../outils/staging/lib.php';

use Imagine\Staging\Guard;

$tests = 0;
function check(bool $value, string $message): void
{
    global $tests;
    ++$tests;
    if (!$value) {
        throw new RuntimeException($message);
    }
}
function rejects(callable $call, string $message): void
{
    try {
        $call();
    } catch (Throwable $e) {
        check(true, $message);
        return;
    }
    check(false, $message);
}

$context = [
    'environment' => 'staging', 'isolated' => true, 'restored' => true,
    'database' => 'invented_staging', 'target_url' => 'https://invented.test',
    'production_hosts' => ['production.invalid'],
];
check(Guard::context($context) === 'https://invented.test', 'contexte staging');
foreach (['production', '', 'development'] as $environment) {
    rejects(fn () => Guard::context(array_replace($context, ['environment' => $environment])), 'refus environnement');
}
rejects(fn () => Guard::context(array_replace($context, ['target_url' => 'https://production.invalid'])), 'refus production');
rejects(fn () => Guard::context(array_replace($context, ['database' => 'invented'])), 'refus base non staging');
rejects(fn () => Guard::context(array_replace($context, ['production_hosts' => []])), 'inventaire production obligatoire');
require __DIR__ . '/fixtures.php';
$store = fixture();
$engine = new Imagine\Staging\Engine($store, $context, 'x_');
$engine->neutraliser();
check($store->rows('x_woocommerce_payment_tokens') === [], 'tokens supprimés');
check($store->rows('x_actionscheduler_actions')[0]['status'] === 'canceled', 'AS annulé');
check($store->rows('x_actionscheduler_actions')[0]['schedule'] === '', 'schedule AS supprimé sans désérialisation');
check($store->rows('x_actionscheduler_logs') === [], 'journaux supprimés');
check(!str_contains(serialize($store->tables), 'cus_SYNTHETIC_ONLY'), 'identifiants supprimés partout');
check(!str_contains(serialize($store->tables), 'sk_live_SYNTHETIC_ONLY'), 'secrets supprimés');
$first = serialize($store->tables);
$engine->neutraliser();
check(serialize($store->tables) === $first, 'neutralisation idempotente');
$bad = fixture();
$bad->columns['x_unknown_private'] = ['id', 'payload'];
$before = serialize($bad->tables);
(new Imagine\Staging\Engine($bad, $context, 'x_'))->neutraliser();
check(isset($bad->columns['x_unknown_private']), 'table inconnue sans colonne personnelle conservée');
$bad = fixture();
$bad->ignoreUrlWrites = true;
$differentTarget = array_replace($context, ['target_url' => 'https://new-invented.test']);
rejects(fn () => (new Imagine\Staging\Engine($bad, $differentTarget, 'x_'))->neutraliser(), 'écriture URL relue');
$engine->anonymiser('SYNTHETIC-test-password-2026');
check(count($store->rows('x_users')) === 31, 'admin après restauration');
$users = $store->rows('x_users');
$admin = array_values(array_filter($users, fn ($u) => $u['user_login'] === 'imagine-test-admin'))[0];
check(password_verify('SYNTHETIC-test-password-2026', $admin['user_pass']), 'secret admin haché');
check(!str_contains(serialize($store->tables), 'SYNTHETIC-test-password-2026'), 'secret absent données');
check($store->rows('x_usermeta')[0]['meta_value'] === 'BE', 'pays conservé');
check($store->rows('x_wc_orders')[0]['total_amount'] === '42.50', 'montant conservé');
check($store->rows('x_wc_orders')[0]['payment_method'] === 'stripe', 'passerelle historique conservée');
check($store->rows('x_wc_orders')[0]['status'] === 'wc-active', 'statut conservé');
check($store->rows('x_wc_order_addresses')[0]['first_name'] === '', 'HPOS noms retirés');
check($store->rows('x_posts')[0]['post_content'] === '', 'commandes classiques anonymisées');
$engine->anonymiser('SYNTHETIC-test-password-2026');
check(count($store->rows('x_users')) === 31, 'pas de doublon admin');
rejects(fn () => $engine->anonymiser('short'), 'secret faible refusé');
$probe = static fn (): array => ['mail_blocked' => true, 'http_blocked' => true, 'subscriptions_staging' => true, 'environment_staging' => true, 'cron_disabled' => true, 'as_async_disabled' => true, 'as_runner_disabled' => true, 'gateways_disabled' => true];
$report = $engine->verifier($probe);
check($report['ok'] === true, 'vérification indépendante');
check($engine->verifier(null)['ok'] === false, 'preuve runtime absente bloque');
$store->tables['x_postmeta'][] = ['meta_id' => 900, 'post_id' => 1, 'meta_key' => 'trap', 'meta_value' => 'pm_SYNTHETIC_ONLY'];
check($engine->verifier($probe)['ok'] === false, 'piège oublié bloque');
array_pop($store->tables['x_postmeta']);
$store->tables['x_users'][0]['user_email'] = 'fictif@outside.invalid';
check($engine->verifier($probe)['ok'] === false, 'email externe bloque');
$store->tables['x_users'][0]['user_email'] = 'abonne-1@example.org';
$store->tables['x_actionscheduler_actions'][0]['status'] = 'pending';
check(in_array('ACTION_EN_ATTENTE', $engine->verifier($probe)['warnings'], true), 'AS résiduel averti');
$store->tables['x_actionscheduler_actions'][0]['status'] = 'canceled';
check(!str_contains(json_encode($engine->verifier($probe)), 'abonne-1'), 'rapport sans données');
$nested = fixture();
$nested->tables['x_postmeta'][] = ['meta_id' => 901, 'post_id' => 1, 'meta_key' => 'invented_contact', 'meta_value' => serialize(['first_name' => 'FICTIF', 'country' => 'BE', 'email' => 'fictif@outside.invalid'])];
$nested->tables['x_postmeta'][] = ['meta_id' => 902, 'post_id' => 1, 'meta_key' => 'invented_json', 'meta_value' => '{"first_name":"FICTIF","country":"BE","email":"fictif@outside.invalid"}'];
$nested->tables['x_postmeta'][] = ['meta_id' => 903, 'post_id' => 1, 'meta_key' => 'invented_empty_json', 'meta_value' => '{"empty":{},"list":[],"numeric":{"0":"BE"}}'];
$nestedEngine = new Imagine\Staging\Engine($nested, $context, 'x_');
$nestedEngine->neutraliser();
$nestedEngine->anonymiser('SYNTHETIC-test-password-2026');
$values = array_column($nested->rows('x_postmeta'), 'meta_value', 'meta_key');
check(unserialize($values['invented_contact'])['first_name'] === '', 'PII sérialisée');
check(json_decode($values['invented_json'], true)['first_name'] === '', 'PII JSON');
check($values['invented_empty_json'] === '{"empty":{},"list":[],"numeric":{"0":"BE"}}', 'types JSON conservés');
require __DIR__ . '/../../outils/staging/files.php';
$scratch = getenv('IMAGINE_TEST_SCRATCH');
if (!$scratch || !is_dir($scratch)) {
    throw new RuntimeException('IMAGINE_TEST_SCRATCH requis');
}
$root = $scratch . '/imagine-synthetic-' . bin2hex(random_bytes(6));
mkdir($root . '/wp-content/uploads/imports', 0777, true);
mkdir($root . '/wp-includes', 0777, true);
mkdir($root . '/wp-content/plugins/woocommerce/includes/importers', 0777, true);
mkdir($root . '/wp-content/mu-plugins/production', 0777, true);
file_put_contents($root . '/wp-content/mu-plugins/production.php', '<?php // SYNTHETIC MU');
file_put_contents($root . '/wp-content/mu-plugins/production/helper.php', '<?php // SYNTHETIC HELPER');
file_put_contents($root . '/wp-content/db.php', '<?php // SYNTHETIC DROPIN');
file_put_contents($root . '/wp-content/sunrise.php', '<?php // SYNTHETIC DROPIN');
file_put_contents($root . '/wp-content/object-cache.php', '<?php // SYNTHETIC CACHE');
file_put_contents($root . '/wp-content/advanced-cache.php', '<?php // SYNTHETIC CACHE');
file_put_contents($root . '/wp-includes/cache.php', 'SYNTHETIC SOURCE');
file_put_contents($root . '/wp-content/plugins/woocommerce/includes/importers/class-import.php', 'SYNTHETIC SOURCE');
file_put_contents($root . '/.imagine-staging-offline', "OFFLINE_COPY\n");
file_put_contents($root . '/wp-content/uploads/imports/invented.csv', 'SYNTHETIC');
file_put_contents($root . '/invented.SQL.GZ', 'SYNTHETIC');
file_put_contents($root . '/wp-content/debug.log', 'SYNTHETIC');
file_put_contents($root . '/wp-content/uploads/invented.jpg', 'SYNTHETIC');
$files = new Imagine\Staging\Files($root);
rejects(fn () => $files->verify(), 'archives présentes bloquent');
$files->purge();
$files->verify();
check(!file_exists($root . '/invented.SQL.GZ'), 'dump supprimé');
check(file_get_contents($root . '/wp-content/mu-plugins/production.php') === '<?php // SYNTHETIC MU', 'MU production conservé');
check(is_file($root . '/wp-content/mu-plugins/production/helper.php'), 'MU sous-répertoire conservé');
check(is_file($root . '/wp-content/db.php') && is_file($root . '/wp-content/sunrise.php'), 'dropins non-cache conservés');
check(!file_exists($root . '/wp-content/object-cache.php') && !file_exists($root . '/wp-content/advanced-cache.php'), 'seuls dropins cache retirés');
check(in_array('production.php', $files->inventory()['mu_plugins'], true), 'MU listé sans contenu');
check(!is_dir($root . '/wp-content/uploads/imports'), 'imports supprimés');
check(file_exists($root . '/wp-content/uploads/invented.jpg'), 'média conservé');
check(file_exists($root . '/wp-includes/cache.php'), 'source core cache conservée');
check(file_exists($root . '/wp-content/plugins/woocommerce/includes/importers/class-import.php'), 'source importateur conservée');
$files->purge();
$files->verify();
check(true, 'purge idempotente');
$it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS), RecursiveIteratorIterator::CHILD_FIRST);
foreach ($it as $entry) {
    $entry->isDir() ? rmdir($entry->getPathname()) : unlink($entry->getPathname());
}
rmdir($root);
$called = false;
$store->tables['x_postmeta'][] = ['meta_id' => 999, 'post_id' => 1, 'meta_key' => 'trap', 'meta_value' => 'sk_live_SYNTHETIC_ONLY'];
$engine->verifier(function () use (&$called, $probe) {
    $called = true;
    return $probe();
});
check($called === false, 'aucun bootstrap si données refusées');
array_pop($store->tables['x_postmeta']);
$prod = fixture();
$prod->tables['x_options'][0]['option_value'] = 'https://production.invalid';
rejects(fn () => new Imagine\Staging\Engine($prod, $context, 'x_'), 'URL source production refusée');
$unknown = fixture();
$unknown->columns['x_users'][] = 'unknown_personal_field';
check(new Imagine\Staging\Engine($unknown, $context, 'x_') instanceof Imagine\Staging\Engine, 'colonne inconnue conservée');
$objects = fixture();
$objects->tables['x_postmeta'][] = ['meta_id' => 998, 'post_id' => 1, 'meta_key' => 'trap', 'meta_value' => 'O:8:"stdClass":0:{}'];
(new Imagine\Staging\Engine($objects, $context, 'x_'))->neutraliser();
check(end($objects->tables['x_postmeta'])['meta_value'] === 'O:8:"stdClass":0:{}', 'objets PHP conservés sans exécution');
check($store->rows('x_posts')[0]['post_date'] === '2026-01-01 00:00:00', 'dates et heures conservées');
$unknownType = fixture();
$unknownType->tables['x_posts'][0]['post_type'] = 'unknown_form_submission';
check(new Imagine\Staging\Engine($unknownType, $context, 'x_') instanceof Imagine\Staging\Engine, 'CPT inconnu conservé');
$opaque = fixture();
$opaqueEngine = new Imagine\Staging\Engine($opaque, $context, 'x_');
$opaqueEngine->neutraliser();
$opaqueEngine->anonymiser('SYNTHETIC-test-password-2026');
$opaque->tables['x_options'][] = ['option_id' => 999, 'option_name' => 'unknown_service_settings', 'option_value' => 'SYNTHETIC_OPAQUE_CREDENTIAL'];
check($opaqueEngine->verifier($probe)['ok'] === true, 'option inconnue conservée et non bloquante');
$store->tables['x_wc_order_addresses'][0]['phone'] = '0000-SYNTHETIC';
check(in_array('IDENTITE_RESIDUELLE', $engine->verifier($probe)['warnings'], true), 'téléphone résiduel averti');
$store->tables['x_wc_order_addresses'][0]['phone'] = '';
rejects(fn () => $engine->verifier(function () use ($store, $probe) {
    $store->tables['x_options'][0]['option_value'] = 'https://drift-invented.test';
    return $probe();
}), 'mutation cible pendant sonde refusée hors critères de données');
$store->tables['x_options'][0]['option_value'] = 'https://invented.test';
$noRole = fixture();
$noRoleEngine = new Imagine\Staging\Engine($noRole, $context, 'x_');
$noRoleEngine->neutraliser();
$noRoleEngine->anonymiser('SYNTHETIC-test-password-2026');
$noRole->tables['x_usermeta'] = array_values(array_filter($noRole->tables['x_usermeta'], fn ($m) => $m['meta_key'] !== 'x_capabilities'));
check($noRoleEngine->verifier($probe)['ok'] === true, 'rôle absent ne crée pas de sixième blocage');
require __DIR__ . '/../../outils/staging/runtime-probe.php';
check(Imagine\Staging\runtimeProbe() === [], 'absence de WP ne simule pas une sonde réussie');
$store->tables['x_postmeta'][] = ['meta_id' => 997, 'post_id' => 1, 'meta_key' => 'invented_ip', 'meta_value' => '2001:db8::1'];
check($engine->verifier($probe)['ok'] === true, 'IPv6 seule ne crée pas de sixième blocage');
array_pop($store->tables['x_postmeta']);
check($store->rows('x_wc_customer_lookup')[0]['username'] === 'abonne-1', 'identifiant lookup anonymisé');
$classic = array_values(array_filter($store->rows('x_postmeta'), fn ($m) => $m['post_id'] === 1));
$classicValues = array_column($classic, 'meta_value', 'meta_key');
check($classicValues['_billing_address_1'] === '', 'adresse classique anonymisée');
check($classicValues['_order_total'] === '42.50' && $classicValues['_payment_method'] === 'stripe', 'métadonnées métier conservées');
$aliases = fixture();
$aliases->tables['x_postmeta'][] = ['meta_id' => 996, 'post_id' => 1, 'meta_key' => 'trap', 'meta_value' => 'a:2:{i:0;s:1:"x";i:1;R:2;}'];
(new Imagine\Staging\Engine($aliases, $context, 'x_'))->neutraliser();
check(end($aliases->tables['x_postmeta'])['meta_value'] === 'a:2:{i:0;s:1:"x";i:1;R:2;}', 'références PHP opaques conservées');
print("OK $tests assertions\n");
