<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

/** Adaptateur WordPress optionnel ; aucun appel WordPress au chargement du moteur pur. */
final class AdministrationFormatExport
{
    public const OPTION = 'imagine_envoi_colonnes_export';

    private const PAGE = 'imagine-envoi-export';

    /** À appeler explicitement depuis le futur bootstrap WordPress. */
    public function brancher(): void
    {
        add_action('admin_menu', [$this, 'menu']);
        add_action('admin_init', [$this, 'enregistrer']);
    }

    public function menu(): void
    {
        add_options_page(
            __('Format de la liste d’envoi', 'imagine-pilotage'),
            __('Export postal Imagine', 'imagine-pilotage'),
            'manage_options',
            self::PAGE,
            [$this, 'page'],
        );
    }

    public function enregistrer(): void
    {
        register_setting(self::OPTION, self::OPTION, [
            'type' => 'array',
            'sanitize_callback' => [$this, 'nettoyer'],
            'default' => ExportCsv::COLONNES,
            'show_in_rest' => false,
        ]);
        add_settings_section(
            'imagine_envoi_format',
            __('Format CSV du routeur', 'imagine-pilotage'),
            static function (): void {
            },
            self::PAGE,
        );
        add_settings_field(
            self::OPTION,
            __('Colonnes dans l’ordre souhaité', 'imagine-pilotage'),
            [$this, 'champ'],
            self::PAGE,
            'imagine_envoi_format',
            ['label_for' => self::OPTION],
        );
    }

    public function page(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }
        echo '<div class="wrap"><h1>' . esc_html(__('Format de la liste d’envoi', 'imagine-pilotage')) . '</h1>';
        settings_errors(self::OPTION);
        // Aucun traitement POST maison : options.php assure capacité, nonce et persistance.
        echo '<form method="post" action="options.php">';
        settings_fields(self::OPTION);
        do_settings_sections(self::PAGE);
        submit_button();
        echo '</form></div>';
    }

    public function champ(): void
    {
        echo '<textarea rows="9" id="' . esc_attr(self::OPTION) . '" name="' . esc_attr(self::OPTION) . '">';
        echo esc_textarea(implode("\n", $this->lire()->colonnes));
        echo '</textarea><p>';
        echo esc_html(__('Une colonne par ligne, dans l’ordre voulu. Colonnes disponibles :', 'imagine-pilotage'));
        echo ' ' . esc_html(implode(', ', ExportCsv::COLONNES)) . '</p>';
    }

    public function exporter(ListeEnvoi $liste, bool $anomaliesRevues = false): string
    {
        return ExportCsv::liste($liste, $anomaliesRevues, $this->lire());
    }

    public function lire(): FormatExport
    {
        $valeur = get_option(self::OPTION, ExportCsv::COLONNES);
        try {
            return new FormatExport($valeur);
        } catch (\InvalidArgumentException | \TypeError) {
            return new FormatExport();
        }
    }

    /** Accepte le texte du formulaire et la liste déjà nettoyée (Settings API peut rappeler le filtre). */
    public function nettoyer(mixed $valeur): array
    {
        if (is_string($valeur)) {
            $valeur = array_map('trim', preg_split('/\r\n|\r|\n/', $valeur));
        }
        try {
            return (new FormatExport($valeur))->colonnes;
        } catch (\InvalidArgumentException | \TypeError) {
            add_settings_error(
                self::OPTION,
                'imagine_envoi_format_invalide',
                __('Format invalide : choisir des colonnes connues, sans doublon. Réglage précédent conservé.', 'imagine-pilotage'),
            );
            return $this->lire()->colonnes;
        }
    }
}
