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

require_once __DIR__ . '/CommandeRegles.php';
require_once __DIR__ . '/SansEmail.php';
require_once __DIR__ . '/CommandeNative.php';
require_once __DIR__ . '/CommandeAdmin.php';
SansEmail::register();
CommandeAdmin::register();

require_once __DIR__ . '/JustificatifRegles.php';
require_once __DIR__ . '/JustificatifsReglages.php';
require_once __DIR__ . '/Justificatifs.php';
JustificatifsReglages::register();
Justificatifs::register();

require_once __DIR__ . '/ExtractionsRegles.php';
require_once __DIR__ . '/ExtractionsNatives.php';
require_once __DIR__ . '/ExtractionsAdmin.php';
ExtractionsAdmin::register();

require_once __DIR__ . '/TableauBordRegles.php';
require_once __DIR__ . '/TableauBordNatives.php';
require_once __DIR__ . '/TableauBordAdmin.php';
TableauBordAdmin::register();

require_once __DIR__ . '/MonCompte.php';
MonCompte::register();

require_once __DIR__ . '/Renouvellement.php';
Renouvellement::register();

require_once __DIR__ . '/NewslettersRegles.php';
require_once __DIR__ . '/Newsletters.php';
require_once __DIR__ . '/NewslettersReglages.php';
Newsletters::register();
NewslettersReglages::register();

require_once __DIR__ . '/ConfidentialiteRegles.php';
require_once __DIR__ . '/Confidentialite.php';
Confidentialite::register();

require_once __DIR__ . '/Partenaires.php';
Partenaires::register();

require_once __DIR__ . '/CooperateursRegles.php';
require_once __DIR__ . '/Cooperateurs.php';
Cooperateurs::register();

require_once __DIR__ . '/PersonnalisationRegles.php';
require_once __DIR__ . '/Personnalisation.php';
require_once __DIR__ . '/PersonnalisationReglages.php';
require_once __DIR__ . '/PersonnalisationConfidentialite.php';
Personnalisation::register();
PersonnalisationReglages::register();
PersonnalisationConfidentialite::register();

// B07 — raccord agenda additif.
require_once __DIR__ . '/AgendaRegles.php';
require_once __DIR__ . '/Agenda.php';
require_once __DIR__ . '/AgendaConfidentialite.php';
Agenda::register();
AgendaConfidentialite::register();

// C25 — demande seule, sans effet financier ni accès.
require_once __DIR__ . '/RetractationRegles.php';
require_once __DIR__ . '/Retractation.php';
require_once __DIR__ . '/RetractationReglages.php';
require_once __DIR__ . '/RetractationConfidentialite.php';
Retractation::register();
RetractationReglages::register();
RetractationConfidentialite::register();

// B08 — pages publiques et propositions locales privées.
require_once __DIR__ . '/CooperativeRegles.php';
require_once __DIR__ . '/Cooperative.php';
require_once __DIR__ . '/Soutenir.php';
require_once __DIR__ . '/SujetRegles.php';
require_once __DIR__ . '/Sujet.php';
require_once __DIR__ . '/SujetConfidentialite.php';
Cooperative::register();
Soutenir::register();
Sujet::register();
SujetConfidentialite::register();

// B09 — pages natives et contact privé local.
require_once __DIR__ . '/Contact.php';
require_once __DIR__ . '/ContactConfidentialite.php';
require_once __DIR__ . '/AutresPages.php';
Contact::register();
ContactConfidentialite::register();
AutresPages::register();

// C27 — déclaration facultative après paiement seulement.
require_once __DIR__ . '/AcquisitionRegles.php';
require_once __DIR__ . '/Acquisition.php';
require_once __DIR__ . '/AcquisitionReglages.php';
require_once __DIR__ . '/AcquisitionConfidentialite.php';
require_once __DIR__ . '/AcquisitionAdmin.php';
Acquisition::register();
AcquisitionReglages::register();
AcquisitionConfidentialite::register();
AcquisitionAdmin::register();

// B10 — points de vente locaux, sans fournisseur de carte.
require_once __DIR__ . '/PointsVenteRegles.php';
require_once __DIR__ . '/PointsVente.php';
PointsVente::register();

// B11 — liens sans oEmbed et audio privé réutilisant C11/C06.
require_once __DIR__ . '/MediasRegles.php';
require_once __DIR__ . '/Medias.php';
require_once __DIR__ . '/AudioNumero.php';
Medias::register();
AudioNumero::register();

// B12 — aucune résolution externe du corps sans consentement.
require_once __DIR__ . '/IntegrationsCorps.php';
IntegrationsCorps::register();

// C29 — projection en lecture seule, aucun connecteur.
require_once __DIR__ . '/ContactBrevoRegles.php';
require_once __DIR__ . '/ContactBrevo.php';
ContactBrevo::register();

// C28 — instantané du pack au paiement, décision et remboursements C14 inchangés.
require_once __DIR__ . '/PacksRegles.php';
require_once __DIR__ . '/PacksThematiques.php';
PacksThematiques::register();

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
