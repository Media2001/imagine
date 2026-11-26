<?php

declare(strict_types=1);

namespace Imagine\Demo\C18;

use Imagine\Site\{ExtractionsNatives, ExtractionsRegles};

if (is_file(WP_PLUGIN_DIR . '/imagine-site/ExtractionsNatives.php')) {
    require_once WP_PLUGIN_DIR . '/imagine-site/ExtractionsRegles.php';
    require_once WP_PLUGIN_DIR . '/imagine-site/ExtractionsNatives.php';
}
$checks = ['raccord_present' => class_exists(ExtractionsNatives::class)];
if ($checks['raccord_present']) {
    $fixture = get_option('imagine_c09_fixture');
    $writes = [];
    $guard = static function (string $sql) use (&$writes): string {
        if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
            $writes[] = strtok(trim($sql), ' ');
            throw new \RuntimeException('Écriture inattendue dans une extraction.');
        }
        return $sql;
    };
    add_filter('query', $guard, PHP_INT_MAX);
    try {
        $all = ExtractionsNatives::lire('localite', []);
        $c09ids = array_map('strval', $fixture['subscriptions']);
        $byProfile = static fn (array $rows): array => array_values(array_intersect($c09ids, array_column($rows, 'abonnement_id')));
        $fr = ExtractionsNatives::lire('localite', ['pays' => 'FR']);
        $checks['C09_etranger_seul_FR'] = $byProfile($fr) === [(string) $fixture['subscriptions']['A-ETRANGER']];
        foreach (['bacs' => 'A-VIR', 'imagine_papier' => 'A-PAPIER'] as $method => $profile) {
            $rows = ExtractionsNatives::lire('mode', ['mode_paiement' => $method]);
            $checks['mode_' . $profile] = $byProfile($rows) === [(string) $fixture['subscriptions'][$profile]];
        }
        foreach (['En délai de grâce' => 'A-GRACE', 'Suspendu' => 'A-SUSP', 'Expiré' => 'A-EXPIRE', 'Actif' => 'A-CARTE'] as $status => $profile) {
            $rows = ExtractionsNatives::lire('etat', ['etat' => $status]);
            $checks['etat_' . $profile] = in_array((string) $fixture['subscriptions'][$profile], array_column($rows, 'abonnement_id'), true)
                && count(array_filter($rows, static fn ($r): bool => $r['etat'] !== $status)) === 0;
        }
        $rows = ExtractionsNatives::lire('echeance', ['du' => gmdate('Y-m-d'), 'au' => gmdate('Y-m-d', strtotime('+30 days'))]);
        $checks['A_ECHEANCE_30_jours'] = in_array((string) $fixture['subscriptions']['A-ECHEANCE'], array_column($rows, 'abonnement_id'), true);
        $same = array_values(array_filter($all, static fn ($r): bool => $r['abonnement_id'] === (string) $fixture['subscriptions']['A-SANSMAIL']));
        $checks['sans_email_colonne_vide'] = count($same) === 1 && $same[0]['email'] === '';
        $checks['colonnes_strictes'] = $all !== [];
        foreach ($all as $row) {
            $checks['colonnes_strictes'] = $checks['colonnes_strictes'] && array_keys($row) === ExtractionsRegles::COLONNES;
        }
        $checks['aucune_ecriture_natif'] = $writes === [];
    } finally {
        remove_filter('query', $guard, PHP_INT_MAX);
    }
    wp_set_current_user($fixture['users']['E-ABO']);
    $checks['capacite_dediee_sans_droits_globaux'] = \Imagine\Site\ExtractionsAdmin::autorise()
        && !current_user_can('manage_options') && !current_user_can('manage_woocommerce');
    $attempted = 0;
    global $wpdb;
    $fault = static function (string $sql) use (&$attempted, $wpdb): string {
        if (preg_match('/^\s*INSERT\b/i', $sql) && str_contains($sql, \Imagine\Site\ExtractionsAdmin::JOURNAL)) {
            $attempted++;
            return "SELECT option_id FROM {$wpdb->options} WHERE 1=0";
        }
        if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
            throw new \RuntimeException('Écriture autre que le journal.');
        }
        return $sql;
    };
    $checks['journal_indisponible_refus_sans_CSV'] = false;
    add_filter('query', $fault, PHP_INT_MAX);
    try {
        \Imagine\Site\ExtractionsAdmin::preparer('localite', []);
    } catch (\RuntimeException $error) {
        $checks['journal_indisponible_refus_sans_CSV'] = $attempted === 1 && str_contains($error->getMessage(), 'Journal indisponible');
    } finally {
        remove_filter('query', $fault, PHP_INT_MAX);
    }
    wp_set_current_user(0);
}
echo wp_json_encode(['checks' => $checks]);
