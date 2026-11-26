<?php

declare(strict_types=1);

namespace Imagine\Demo\C19;

use Imagine\Site\{TableauBordNatives, TableauBordAdmin, ExtractionsNatives, EcheancesNatives};

$checks = ['raccord_present' => class_exists(TableauBordNatives::class) && class_exists(TableauBordAdmin::class)];
$out = [];
if ($checks['raccord_present']) {
    $writes = [];
    $outgoing = [];
    $guard = static function (string $sql) use (&$writes): string {
        if (!preg_match('/^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b/i', $sql)) {
            $writes[] = strtok(trim($sql), ' ');
            throw new \RuntimeException('Écriture interdite C19.');
        }
        return $sql;
    };
    $http = static function () use (&$outgoing): never {
        $outgoing[] = 'http';
        throw new \RuntimeException('HTTP interdit C19.');
    };
    $mail = static function () use (&$outgoing): never {
        $outgoing[] = 'mail';
        throw new \RuntimeException('Email interdit C19.');
    };
    add_filter('query', $guard, PHP_INT_MAX);
    add_filter('pre_http_request', $http, PHP_INT_MAX);
    add_filter('pre_wp_mail', $mail, PHP_INT_MAX);
    try {
        $out = TableauBordNatives::lire();
        $active = ExtractionsNatives::lire('etat', ['etat' => 'Actif']);
        $checks['actifs_egal_lignes_C18'] = $out['actifs']['valeurs']['total'] === count($active);
        foreach ($out['actifs']['valeurs'] as $key => $number) {
            if ($key === 'total') {
                continue;
            }
            $mode = substr($key, 5);
            $checks['mode_' . $mode . '_egal_lignes_C18'] = $number === count(array_filter($active, static fn ($r): bool =>
                $r['mode_paiement'] === ($mode === 'inconnu' ? '' : $mode)));
        }
        foreach ([30, 90, 180] as $days) {
            $checks['echeances_' . $days . '_egal_lignes_C15'] = $out['echeances']['valeurs'][$days] === count(EcheancesNatives::lire('echeances', $days));
        }
        $checks['echecs_egal_lignes_C15'] = $out['echecs']['valeurs']['total'] === count(EcheancesNatives::lire('echecs', 30));
        $now = time();
        $start = strtotime(gmdate('Y-m-01 00:00:00', $now) . ' UTC');
        $counts = ['entrees' => 0, 'sorties' => 0];
        foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
            $debut = (int) $sub->get_time('start');
            $fin = (int) $sub->get_time('end');
            $counts['entrees'] += (int) ($debut > 0 && $debut >= $start && $debut <= $now);
            $counts['sorties'] += (int) ($sub->has_status(['cancelled', 'expired']) && $fin > 0 && $fin >= $start && $fin <= $now);
        }
        $checks['mouvements_egal_lignes_dates_natives'] = $counts === $out['mouvements']['valeurs'];
        $checks['quatre_indicateurs'] = array_keys($out) === ['actifs', 'echeances', 'echecs', 'mouvements'];
        $checks['sortie_sans_donnee_personnelle'] = true;
        foreach ($out as $metric) {
            $checks['sortie_sans_donnee_personnelle'] = $checks['sortie_sans_donnee_personnelle']
                && array_keys($metric) === ['titre', 'phrase', 'valeurs']
                && count(array_filter($metric['valeurs'], 'is_int')) === count($metric['valeurs']);
        }
        $fixture = get_option('imagine_c09_fixture');
        wp_set_current_user($fixture['users']['E-ABO']);
        $checks['droit_dedie_sans_droit_global'] = current_user_can(TableauBordAdmin::CAP) && TableauBordAdmin::autorise()
            && !current_user_can('manage_options') && !current_user_can('manage_woocommerce');
        ob_start();
        TableauBordAdmin::page();
        $html = ob_get_clean();
        $checks['rendu_tableau_simple'] = str_contains($html, 'data-imagine-indicateur="actifs"') && !str_contains($html, '<script');
        $checks['aucun_formulaire'] = !str_contains($html, '<form');
        $deny = static function (array $caps): array { $caps['imagine_referent_abonnements'] = false; return $caps; };
        add_filter('user_has_cap', $deny, PHP_INT_MAX);
        $checks['capacite_revoquee_refuse'] = !TableauBordAdmin::autorise();
        remove_filter('user_has_cap', $deny, PHP_INT_MAX);
        $checks['aucune_ecriture_SQL'] = $writes === [];
        $checks['aucun_appel_sortant'] = $outgoing === [];
        wp_set_current_user(0);
    } finally {
        remove_filter('query', $guard, PHP_INT_MAX);
        remove_filter('pre_http_request', $http, PHP_INT_MAX);
        remove_filter('pre_wp_mail', $mail, PHP_INT_MAX);
    }
}
echo wp_json_encode(['checks' => $checks, 'indicateurs' => $out]);
