<?php

declare(strict_types=1);

use Imagine\Site\{ContactBrevo, Newsletters, Personnalisation, Cooperateurs};

if (!class_exists(ContactBrevo::class)) {
    fwrite(STDERR, "C29 adaptateur absent\n"); exit(1);
}
$fixture = get_option('imagine_c09_fixture');
$users = $fixture['users'];
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException($name); }
};
$expected = require __DIR__ . '/c29-attendus.php';
$check('catalogue_27_profils_exact', count($expected) === 27 && array_keys($users) === array_keys($expected));
$catalogue = [['id' => 'principale', 'titre' => 'FICTIF C29', 'presentation' => 'Essai', 'principale' => true]];
update_option(Newsletters::CATALOGUE, $catalogue, false);
update_option(Personnalisation::CATALOGUE, [['id' => 'fictif', 'titre' => 'FICTIF C29', 'multiple' => false,
    'choix' => [['id' => 'a', 'titre' => 'FICTIF A']]]], false);
$map = [];
foreach ($fixture['tariffs'] as $code => $id) { $map[(string)$id] = $code; }
update_option(ContactBrevo::TARIFS, $map, false);
$date = '2026-11-27T00:00:00Z';
foreach ($users as $code => $id) {
    $pref = str_starts_with($code, 'E-') || $code === 'V-INSCRIT' ? []
        : ['principale' => ['choix' => $code !== 'V-DEC-FIN', 'origine' => 'lecteur', 'date_utc' => $date]];
    update_user_meta($id, Newsletters::META, $pref);
    update_user_meta($id, Cooperateurs::META, ['cooperateur' => $code === 'P-COOP']);
    delete_user_meta($id, Personnalisation::META);
    delete_user_meta($id, Personnalisation::CONSENTEMENT);
}
update_user_meta($users['A-SANSMAIL'], Imagine\Site\SansEmail::META, '1');
update_user_meta($users['A-CARTE'], Personnalisation::META, ['fictif' => ['choix' => ['a'], 'date_utc' => $date]]);
update_user_meta($users['A-CARTE'], Personnalisation::CONSENTEMENT, ['accord' => true, 'date_utc' => $date]);
$writes = []; $outgoing = [];
$guard = static function (string $sql) use (&$writes): string {
    if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
        $writes[] = $sql; throw new RuntimeException('C29 écriture SQL');
    }
    return $sql;
};
$http = static function () use (&$outgoing): never { $outgoing[] = 'http'; throw new RuntimeException('C29 HTTP'); };
$mail = static function () use (&$outgoing): never { $outgoing[] = 'mail'; throw new RuntimeException('C29 mail'); };
add_filter('query', $guard, PHP_INT_MAX);
add_filter('pre_http_request', $http, PHP_INT_MAX);
add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
$actual = [];
try {
    foreach ($users as $code => $id) {
        [$status, $tariff, $coop, $reason] = $expected[$code];
        $want = $status === null ? null : ($status === 'a_retirer' ? ['statut' => 'a_retirer']
            : ['email' => get_userdata($id)->user_email, 'statut' => $status, 'cooperateur' => $coop,
                'tarif' => $tariff, 'newsletters' => ['principale'],
                'personnalisation' => $code === 'A-CARTE' ? ['fictif' => ['choix' => ['a'], 'date_utc' => $date]] : []]);
        $actual[$code] = ContactBrevo::fiche((int)$id);
        $check('profil_' . $code, $actual[$code] === ['fiche' => $want, 'raison' => $reason]);
    }
    $check('reglages_present', method_exists(ContactBrevo::class, 'reglages'));
    ContactBrevo::reglages();
    $check('reglage_tarif_enregistre', get_registered_settings()[ContactBrevo::TARIFS]['default'] === []);
    $check('tarif_invalide_ferme', ContactBrevo::tarifs(['0' => 'normal']) === [] && ContactBrevo::tarifs(['192' => '<script>']) === [] && ContactBrevo::tarifs('mauvais') === []);
    $check('tarif_map_valide', ContactBrevo::tarifs(['192' => 'normal-1']) === [192 => 'normal-1']);
    $check('ecran_present', method_exists(ContactBrevo::class, 'page'));
    wp_set_current_user((int)$users['E-ABO']);
    $_SERVER['REQUEST_METHOD'] = 'GET';
    $_GET['compte'] = (string)$users['A-CARTE'];
    ob_start(); ContactBrevo::page(); $html = ob_get_clean();
    $check('ecran_fiche_et_totaux', str_contains($html, 'data-imagine-brevo') && str_contains($html, 'data-brevo-fiche') && str_contains($html, 'data-brevo-total="abonne"'));
    $check('ecran_aucun_POST_script', !str_contains($html, 'method="post"') && !str_contains($html, '<script'));
    $check('aucune_ecriture_SQL', $writes === []);
    $check('aucun_sortant', $outgoing === []);
} finally {
    remove_filter('query', $guard, PHP_INT_MAX);
    remove_filter('pre_http_request', $http, PHP_INT_MAX);
    remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
}
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'profils' => $actual, 'writes' => $writes, 'outgoing' => $outgoing]);
