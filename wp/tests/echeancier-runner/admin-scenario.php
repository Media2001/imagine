<?php

declare(strict_types=1);

use Imagine\Pilotage\Echeancier\Planificateur;
use Imagine\Pilotage\Echeancier\ReglagesAdministration;
use Imagine\Pilotage\Numeros\Moteur;

function c05AdminScenario(): void
{
    require_once ABSPATH . 'wp-admin/includes/plugin.php';
    require_once ABSPATH . 'wp-admin/includes/template.php';
    $admin = new ReglagesAdministration();
    $admin->enregistrer();
    c05Check('admin_hooks_explicit', has_action('admin_init', [$admin, 'declarer']) !== false);
    $admin->declarer();
    $settings = get_registered_settings()[ReglagesAdministration::OPTION];
    c05Check('admin_not_public_rest', $settings['show_in_rest'] === false);
    c05Check('admin_no_default_margin', $admin->lire()->margeJours === null);
    c05Check('admin_options_capability', apply_filters('option_page_capability_imagine_c05', 'manage_options') === 'manage_woocommerce');
    $a = c05Annee('2027-04-09 12:00:00');
    $planner = new Planificateur(new Moteur(c05Calendrier()));
    $refuse = false;
    try {
        $planner->planifier($a, $admin->lire()->margeJours);
    } catch (InvalidArgumentException $e) {
        $refuse = str_contains($e->getMessage(), 'MARGE_OBLIGATOIRE');
    }
    c05Check('admin_missing_margin_blocks_engine', $refuse);
    wp_set_current_user(get_user_by('login', 'c05-fiction')->ID);
    ob_start();
    $admin->afficher();
    $html = ob_get_clean();
    c05Check('admin_form_standard_nonce', str_contains($html, 'name="_wpnonce"') && str_contains($html, 'options.php'));
    c05Check('admin_margin_empty_not_seven', str_contains($html, '[marge_jours]') && !str_contains($html, 'value="7"'));
    wp_set_current_user(0);
    $denied = false;
    $refusWordPress = null;
    $traduire = static function (string $traduction, string $texte, string $domaine): string {
        return $texte === 'Gestion WooCommerce requise.' && $domaine === 'imagine-pilotage'
            ? 'TRADUIT C05 : ' . $traduction : $traduction;
    };
    $handler = static function () use (&$refusWordPress): callable {
        return static function (string $message) use (&$refusWordPress): never {
            $refusWordPress = $message;
            throw new RuntimeException('IMAGINE_C05_WP_DIE');
        };
    };
    add_filter('gettext', $traduire, PHP_INT_MAX, 3);
    add_filter('wp_die_handler', $handler, PHP_INT_MAX);
    try {
        $admin->afficher();
    } catch (RuntimeException $e) {
        $denied = $e->getMessage() === 'IMAGINE_C05_WP_DIE';
    } finally {
        remove_filter('wp_die_handler', $handler, PHP_INT_MAX);
        remove_filter('gettext', $traduire, PHP_INT_MAX);
    }
    c05Check('admin_anonymous_form_denied', $denied);
    c05Check('admin_anonymous_wp_die_translated', $refusWordPress === 'TRADUIT C05 : Gestion WooCommerce requise.');
    foreach ([1, 7, 30] as $margin) {
        foreach (['restent_dues', 'annuler_restantes'] as $rejection) {
            foreach (['fige_bloc', 'courant_impayes'] as $price) {
                $value = ['marge_jours' => (string) $margin, 'apres_rejet' => $rejection, 'tarif' => $price];
                update_option(ReglagesAdministration::OPTION, $value, false);
                $read = $admin->lire();
                c05Check('admin_option_readback_each_value', $read->margeJours === $margin && $read->apresRejet === $rejection && $read->tarif === $price);
                $plan = $planner->planifier($a, $read->margeJours);
                c05Check('admin_margin_changes_engine', $plan[1]->date == c05Date('2027-07-10')->modify('-' . $margin . ' days'));
                $due = $read->montantsRestants(1000, 1200, [1], true);
                $amount = $price === 'fige_bloc' ? 1000 : 1200;
                c05Check('admin_policy_changes_projection', $due === ($rejection === 'restent_dues' ? [2 => $amount, 3 => $amount, 4 => $amount] : []));
            }
        }
    }
    $before = get_option(ReglagesAdministration::OPTION);
    update_option(ReglagesAdministration::OPTION, ['marge_jours' => '7 jours', 'apres_rejet' => 'annuler_restantes'], false);
    c05Check('admin_invalid_preserves_previous_option', get_option(ReglagesAdministration::OPTION) === $before);
    c05Check('admin_invalid_has_settings_error', count(get_settings_errors(ReglagesAdministration::OPTION)) > 0);
    update_option(ReglagesAdministration::OPTION, ['marge_jours' => '', 'apres_rejet' => 'restent_dues', 'tarif' => 'fige_bloc'], false);
    c05Check('admin_clear_margin_keeps_unconfigured', $admin->lire()->margeJours === null);
    update_option(ReglagesAdministration::OPTION, ['marge_jours' => '7', 'apres_rejet' => 'restent_dues', 'tarif' => 'fige_bloc'], false);
    c05Check('admin_final_fixture_settings_readback', $admin->lire()->margeJours === 7);
}
