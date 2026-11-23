<?php
/** C10 : tranche réelle d'enregistrement et rendu natifs, sur le site fictif seul. */
declare(strict_types=1);
namespace Imagine\Demo\C10Tests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive C10 requise.');
}
$checks = ['ecran_present' => class_exists('Imagine\\Pilotage\\Administration\\Reglages')];
if ($checks['ecran_present']) {
    $screen = new \Imagine\Pilotage\Administration\Reglages();
    $screen->enregistrer();
    $registered = get_registered_settings();
    $checks['trois_options_meme_groupe'] = count(array_filter($screen->options(), static fn ($name) =>
        isset($registered[$name]) && $registered[$name]['group'] === 'imagine_reglages'
        && $registered[$name]['show_in_rest'] === false)) === 3;
    wp_set_current_user(get_user_by('login', 'e-admin')->ID);
    ob_start();
    $screen->page();
    $html = ob_get_clean();
    foreach (['Accès', 'Paiement en quatre fois', 'Liste d’envoi', 'À confirmer par Imagine',
        'Défaut', 'Journal des modifications', 'options.php', '_wpnonce'] as $text) {
        $checks['rendu_' . $text] = str_contains($html, $text);
    }
    $checks['huit_champs'] = substr_count($html, 'class="imagine-reglage"') === 8;
    $checks['cap_admin'] = apply_filters('option_page_capability_imagine_reglages', 'manage_options') === 'manage_options';
    wp_set_current_user(get_user_by('login', 'e-redac')->ID);
    $checks['redacteur_sans_droit'] = !current_user_can('manage_options');
    wp_set_current_user(0);
}
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
if ($failures) { WP_CLI::halt(1); }
