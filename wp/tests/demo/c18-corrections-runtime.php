<?php

declare(strict_types=1);

namespace Imagine\Demo\C18Corrections;

use Imagine\Site\{ExtractionsAdmin, ExtractionsNatives, ExtractionsRegles, MonCompte, TableauBordNatives};

// Existing normal-route native checks, including fail-closed journal persistence.
ob_start();
(static function (): void {
    require WP_CONTENT_DIR . '/imagine-demo-build/c18-runtime.php';
})();
$normal = json_decode(ob_get_clean(), true, flags: JSON_THROW_ON_ERROR);
$checks = $normal['checks'];
$writes = [];
$outgoing = [];
$guard = static function (string $sql) use (&$writes): string {
    if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
        $writes[] = strtok(trim($sql), ' ');
        throw new \RuntimeException('Écriture interdite C18/C19.');
    }
    return $sql;
};
$http = static function () use (&$outgoing): never {
    $outgoing[] = 'HTTP';
    throw new \RuntimeException('HTTP interdit.');
};
$mail = static function () use (&$outgoing): never {
    $outgoing[] = 'email';
    throw new \RuntimeException('Email interdit.');
};
$gettext = static fn (string $translated, string $text, string $domain): string =>
    $domain === 'imagine-site' && $text === 'Actif' ? 'Active' : $translated;
$c19probe = static function (): array {
    ob_start();
    require WP_CONTENT_DIR . '/imagine-demo-build/c19-runtime.php';
    return json_decode(ob_get_clean(), true, flags: JSON_THROW_ON_ERROR);
};
add_filter('query', $guard, PHP_INT_MAX);
add_filter('pre_http_request', $http, PHP_INT_MAX);
add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
$oldGet = $_GET;
$oldUser = get_current_user_id();
try {
    $before = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
    $dashboardBefore = TableauBordNatives::lire();
    $c19Before = $c19probe();
    add_filter('gettext', $gettext, PHP_INT_MAX, 3);
    $after = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
    $checks['gettext_reel_Actif_Active'] = $before !== [] && MonCompte::etat(wcs_get_subscription((int) $before[0]['abonnement_id'])) === 'Active';
    $checks['meme_filtre_memes_identifiants_et_lignes'] = $before === $after;
    $checks['cles_natives_stables_C19'] = count(array_filter($after, static fn (array $row): bool => $row['etat'] !== 'Actif')) === 0;
    $display = ExtractionsAdmin::affichage($after);
    $checks['affichage_traduit_seulement'] = array_column($display, 'abonnement_id') === array_column($after, 'abonnement_id')
        && count(array_filter($display, static fn (array $row): bool => $row['etat'] !== 'Active')) === 0;
    $stream = fopen('php://memory', 'w+b');
    ExtractionsRegles::csv($stream, 'etat', $display);
    rewind($stream);
    $columns = fgetcsv($stream, escape: '');
    $csv = [];
    while (($row = fgetcsv($stream, escape: '')) !== false) {
        $csv[] = array_combine($columns, $row);
    }
    fclose($stream);
    $checks['CSV_traduit_colonnes_fermees_meme_selection'] = $columns === ExtractionsRegles::COLONNES && $csv === $display;
    wp_set_current_user(get_option('imagine_c09_fixture')['users']['E-ABO']);
    $_GET = ['extraction' => 'etat', 'etat' => 'Actif'];
    ob_start();
    ExtractionsAdmin::page();
    $html = ob_get_clean();
    $checks['option_valeur_stable_label_traduit'] = preg_match('/<option value="Actif"[^>]*>Active<\/option>/', $html) === 1;
    $checks['apercu_traduit_meme_nombre'] = str_contains($html, 'data-imagine-extraction-nombre="' . count($after) . '"');
    $checks['POST_conserve_cle_stable'] = str_contains($html, 'name="etat" value="Actif"');
    $dashboardAfter = TableauBordNatives::lire();
    $c19After = $c19probe();
    $checks['C19_memes_indicateurs_avec_gettext'] = $dashboardBefore === $dashboardAfter;
    $checks['C19_actifs_egal_apercu_C18'] = $dashboardAfter['actifs']['valeurs']['total'] === count($after);
    foreach (['normal' => $c19Before, 'gettext' => $c19After] as $mode => $probe) {
        foreach ($probe['checks'] as $key => $value) {
            $checks['seam_C19_' . $mode . '_' . $key] = $value;
        }
    }
    $checks['aucune_ecriture_dans_seam'] = $writes === [];
    $checks['aucun_email_ni_appel_sortant'] = $outgoing === [];
} finally {
    remove_filter('gettext', $gettext, PHP_INT_MAX);
    remove_filter('query', $guard, PHP_INT_MAX);
    remove_filter('pre_http_request', $http, PHP_INT_MAX);
    remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
    $_GET = $oldGet;
    wp_set_current_user($oldUser);
}
echo wp_json_encode(['checks' => $checks, 'total' => count($checks),
    'failures' => array_keys(array_filter($checks, static fn ($value): bool => $value !== true)),
    'actifs_ids_avant' => array_column($before, 'abonnement_id'),
    'actifs_ids_gettext' => array_column($after, 'abonnement_id'),
    'C19_valeurs_avant' => array_map(static fn (array $metric): array => $metric['valeurs'], $dashboardBefore),
    'C19_valeurs_gettext' => array_map(static fn (array $metric): array => $metric['valeurs'], $dashboardAfter)]);
