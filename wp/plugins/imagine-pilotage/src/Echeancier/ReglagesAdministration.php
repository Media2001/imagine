<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

/** Adaptation dédiée : appeler enregistrer() depuis le bootstrap parent, jamais au chargement. */
final class ReglagesAdministration
{
    public const OPTION = 'imagine_c05_reglages';

    public function enregistrer(): void
    {
        add_action('admin_init', [$this, 'declarer']);
        add_action('admin_menu', [$this, 'menu']);
        add_filter('option_page_capability_imagine_c05', static fn (): string => 'manage_woocommerce');
    }

    public function declarer(): void
    {
        register_setting('imagine_c05', self::OPTION, [
            'type' => 'array',
            'sanitize_callback' => [$this, 'sanitiser'],
            'show_in_rest' => false,
            'default' => ['marge_jours' => null, 'apres_rejet' => 'restent_dues', 'tarif' => 'fige_bloc'],
        ]);
    }

    public function lire(): Reglages
    {
        return Reglages::depuisOption(get_option(self::OPTION, []));
    }

    /** Une saisie invalide ne remplace jamais une configuration valide. */
    public function sanitiser(mixed $valeur): mixed
    {
        try {
            $r = Reglages::depuisOption($valeur);
            return ['marge_jours' => $r->margeJours, 'apres_rejet' => $r->apresRejet, 'tarif' => $r->tarif];
        } catch (\InvalidArgumentException $error) {
            add_settings_error(
                self::OPTION,
                'imagine_c05_reglages_invalides',
                __(
                    'Réglages refusés : marge civile positive entière ou vide, rejet et tarif parmi les choix proposés.',
                    'imagine-pilotage'
                )
            );
            return get_option(self::OPTION, []);
        }
    }

    public function menu(): void
    {
        add_submenu_page(
            'woocommerce',
            __('Échéancier en quatre fois', 'imagine-pilotage'),
            __('Échéancier en quatre fois', 'imagine-pilotage'),
            'manage_woocommerce',
            'imagine-c05',
            [$this, 'afficher']
        );
    }

    public function afficher(): void
    {
        if (!current_user_can('manage_woocommerce')) {
            throw new \LogicException('AUTORISATION : ' . __('Gestion WooCommerce requise.', 'imagine-pilotage'));
        }
        $r = $this->lire();
        echo '<div class="wrap"><h1>' . esc_html__('Échéancier en quatre fois', 'imagine-pilotage') . '</h1>';
        settings_errors(self::OPTION);
        echo '<p>' . esc_html__(
            'Quatre échéances par bloc de quatre numéros. Une fenêtre de date à date peut contenir cinq dates.',
            'imagine-pilotage'
        ) . '</p>';
        echo '<form method="post" action="options.php">';
        settings_fields('imagine_c05');
        echo '<p><label for="imagine-c05-marge">'
            . esc_html__('Marge avant clôture (jours civils)', 'imagine-pilotage') . '</label> ';
        echo '<input id="imagine-c05-marge" name="' . esc_attr(self::OPTION)
            . '[marge_jours]" type="number" min="1" step="1" value="'
            . esc_attr((string) $r->margeJours) . '"></p>';
        echo '<p>' . esc_html__(
            'Sans marge renseignée, toute planification est refusée. Aucun défaut ne sera appliqué.',
            'imagine-pilotage'
        ) . '</p>';
        $this->choix('apres_rejet', __('Après un rejet', 'imagine-pilotage'), $r->apresRejet, [
            'restent_dues' => __('Les échéances restantes restent dues (défaut)', 'imagine-pilotage'),
            'annuler_restantes' => __('Ne plus devoir les échéances restantes après rejet', 'imagine-pilotage'),
        ]);
        $this->choix('tarif', __('Changement de tarif', 'imagine-pilotage'), $r->tarif, [
            'fige_bloc' => __('Montants figés pour les quatre échéances du bloc (défaut)', 'imagine-pilotage'),
            'courant_impayes' => __('Tarif courant pour les seules échéances non payées', 'imagine-pilotage'),
        ]);
        echo '<p>' . esc_html__(
            'Ces réglages pilotent une projection. Les droits suivent séparément le délai de grâce ; '
                . 'aucune remise ni opération bancaire ne part de cet écran.',
            'imagine-pilotage'
        ) . '</p>';
        submit_button();
        echo '</form></div>';
    }

    /** @param array<string, string> $valeurs */
    private function choix(string $cle, string $libelle, string $courant, array $valeurs): void
    {
        $id = 'imagine-c05-' . $cle;
        echo '<p><label for="' . esc_attr($id) . '">' . esc_html($libelle) . '</label> ';
        echo '<select id="' . esc_attr($id) . '" name="' . esc_attr(self::OPTION) . '[' . esc_attr($cle) . ']">';
        foreach ($valeurs as $valeur => $texte) {
            echo '<option value="' . esc_attr($valeur) . '"' . selected($courant, $valeur, false)
                . '>' . esc_html($texte) . '</option>';
        }
        echo '</select></p>';
    }
}
