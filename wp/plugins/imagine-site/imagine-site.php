<?php
/**
 * MODÈLE PROVISOIRE B-00 : types et champs de démonstration, pas le futur modèle éditorial.
 * Plugin Name: Imagine — site
 * Description: Contenus fictifs provisoires, calendrier et chargement des bibliothèques métier.
 * Version: 0.2.0
 * Requires at least: 7.0
 * Requires PHP: 8.2
 * Text Domain: imagine-site
 */

declare(strict_types=1);

namespace Imagine\Site;

if (!defined('ABSPATH')) {
    exit;
}

// Les bibliothèques closes restent inchangées, copiées depuis le dépôt par le constructeur.
spl_autoload_register(static function (string $class): void {
    foreach (['Imagine\\Pilotage\\' => 'imagine-pilotage', 'Imagine\\Connecteur\\' => 'imagine-connecteur'] as $prefix => $directory) {
        if (str_starts_with($class, $prefix)) {
            $path = WP_PLUGIN_DIR . '/' . $directory . '/src/' . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
            if (is_file($path)) {
                require_once $path;
            }
            return;
        }
    }
});

require_once __DIR__ . '/NumeroPublication.php';
NumeroPublication::register();

require_once __DIR__ . '/Decouverte.php';
Decouverte::register();
require_once __DIR__ . '/DecouverteReglages.php';
DecouverteReglages::register();

require_once __DIR__ . '/AchatNumero.php';
require_once __DIR__ . '/AchatsNumeros.php';
AchatsNumeros::register();

require_once __DIR__ . '/Paywall.php';
Paywall::register();

require_once __DIR__ . '/PdfNumero.php';
PdfNumero::register();

require_once __DIR__ . '/EnvoiNatif.php';
require_once __DIR__ . '/ListeEnvoiAdmin.php';
EnvoiNatif::register();
ListeEnvoiAdmin::register();

require_once __DIR__ . '/EcheancesRegles.php';
require_once __DIR__ . '/EcheancesNatives.php';
require_once __DIR__ . '/EcheancesAdmin.php';
EcheancesAdmin::register();

require_once __DIR__ . '/MonCompte.php';
MonCompte::register();

add_action('init', static function (): void {
    foreach ([
        'imagine_numero' => [__('Numéros fictifs', 'imagine-site'), 'numeros'],
        'imagine_evenement' => [__('Événements fictifs', 'imagine-site'), 'evenements'],
        'imagine_partenaire' => [__('Partenaires fictifs', 'imagine-site'), 'partenaires'],
    ] as $type => [$label, $slug]) {
        register_post_type($type, [
            'label' => $label,
            'public' => true,
            'show_in_rest' => true,
            'has_archive' => true,
            'rewrite' => ['slug' => $slug],
            'supports' => ['title', 'editor', 'excerpt', 'thumbnail', 'custom-fields'],
        ]);
    }
    register_taxonomy('imagine_thematique', ['post'], [
        'label' => __('Thématiques fictives', 'imagine-site'),
        'public' => true,
        'show_in_rest' => true,
        'hierarchical' => true,
        'rewrite' => ['slug' => 'thematiques'],
    ]);
    register_post_meta('post', 'imagine_numero_id', [
        'type' => 'integer', 'single' => true, 'show_in_rest' => true,
        'sanitize_callback' => 'absint',
        'auth_callback' => static fn () => current_user_can('edit_posts'),
    ]);
    register_post_meta('post', 'imagine_reserve', [
        'type' => 'boolean', 'single' => true, 'show_in_rest' => true,
        'auth_callback' => static fn () => current_user_can('edit_posts'),
    ]);
});

// Repli natif B-00 conservé si le raccord C-08 n'est pas disponible.
add_filter('the_password_form', static function (string $form): string {
    $post = get_post();
    if (!$post || !get_post_meta($post->ID, 'imagine_reserve', true)) {
        return $form;
    }
    return '<p><strong>' . esc_html__('Article fictif réservé — protection provisoire B-00.', 'imagine-site')
        . '</strong></p><p>' . esc_html($post->post_excerpt) . '</p>' . $form;
});

add_shortcode('imagine_demo_calendrier', static function (): string {
    $html = '<table><caption>' . esc_html__('Calendrier entièrement fictif 2026–2028', 'imagine-site') . '</caption><thead><tr>';
    foreach ([__('Parution', 'imagine-site'), __('Sortie', 'imagine-site'), __('Clôture de la liste', 'imagine-site')] as $label) {
        $html .= '<th scope="col">' . esc_html($label) . '</th>';
    }
    $html .= '</tr></thead><tbody>';
    foreach (get_option('imagine_demo_calendrier', []) as $row) {
        $html .= '<tr><th scope="row">' . esc_html($row['code']) . '</th><td>' . esc_html($row['sortie']) . '</td><td>' . esc_html($row['cloture']) . '</td></tr>';
    }
    return $html . '</tbody></table>';
});
