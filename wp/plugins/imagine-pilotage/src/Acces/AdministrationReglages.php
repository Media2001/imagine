<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

/** Couche WordPress optionnelle ; le moteur et Reglages restent du PHP pur. */
final class AdministrationReglages
{
    public const OPTION = 'imagine_acces_reglages';
    private const PAGE = 'imagine-acces';
    private const SECTION = 'imagine_acces_politiques';

    /** À appeler une fois depuis le bootstrap WordPress, après l'autoload. */
    public function brancher(): void
    {
        add_action('admin_menu', [$this, 'menu']);
        add_action('admin_init', [$this, 'enregistrer']);
    }

    public function menu(): void
    {
        add_options_page(
            __('Accès aux contenus Imagine', 'imagine-pilotage'),
            __('Accès Imagine', 'imagine-pilotage'),
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
            'default' => (new Reglages())->options(),
            'show_in_rest' => false,
        ]);
        add_settings_section(
            self::SECTION,
            __('Règles d’accès', 'imagine-pilotage'),
            static function (): void {
            },
            self::PAGE,
        );
        foreach ($this->champs() as $cle => $champ) {
            $id = 'imagine_acces_' . $cle;
            add_settings_field(
                $id,
                $champ['titre'],
                [$this, 'champ'],
                self::PAGE,
                self::SECTION,
                ['cle' => $cle, 'label_for' => $id],
            );
        }
    }

    /** Normalisation stricte et idempotente ; pas de conversion d'une valeur inconnue en droit. */
    public function nettoyer(mixed $valeur): array
    {
        return Reglages::depuisOptions($valeur)->options();
    }

    public function lire(): Reglages
    {
        try {
            return Reglages::depuisOptions(get_option(self::OPTION, []));
        } catch (\Throwable) {
            return new Reglages();
        }
    }

    public function page(): void
    {
        if (!current_user_can('manage_options')) {
            return;
        }
        echo '<div class="wrap"><h1>';
        echo esc_html(__('Accès aux contenus Imagine', 'imagine-pilotage'));
        echo '</h1>';
        settings_errors(self::OPTION);
        // options.php gère capacité, nonce et persistance ; pas de gestionnaire POST sur mesure.
        echo '<form method="post" action="options.php">';
        settings_fields(self::OPTION);
        do_settings_sections(self::PAGE);
        submit_button();
        echo '</form></div>';
    }

    public function champ(array $arguments): void
    {
        $champs = $this->champs();
        $cle = $arguments['cle'] ?? null;
        if (!is_string($cle) || !isset($champs[$cle])) {
            return;
        }
        $valeur = $this->lire()->options()[$cle];
        echo '<select id="' . esc_attr('imagine_acces_' . $cle) . '" name="';
        echo esc_attr(self::OPTION . '[' . $cle . ']') . '">';
        foreach ($champs[$cle]['choix'] as $option => $libelle) {
            echo '<option value="' . esc_attr($option) . '"';
            echo $option === $valeur ? ' selected="selected"' : '';
            echo '>' . esc_html($libelle) . '</option>';
        }
        echo '</select>';
    }

    private function champs(): array
    {
        return [
            'contenu_futur' => [
                'titre' => __('Contenu dont la sortie est à venir', 'imagine-pilotage'),
                'choix' => [
                    'ferme_tous' => __('Fermé pour tous, équipe et robots compris (défaut)', 'imagine-pilotage'),
                    'equipe' => __('Ouvert à l’équipe uniquement', 'imagine-pilotage'),
                ],
            ],
            'pdf_robot' => [
                'titre' => __('PDF pour un robot d’indexation vérifié', 'imagine-pilotage'),
                'choix' => [
                    'extrait' => __('Extrait, sans PDF complet (défaut)', 'imagine-pilotage'),
                    'complet' => __('Complet', 'imagine-pilotage'),
                ],
            ],
            'pdf_anterieur_abonnement' => [
                'titre' => __('PDF antérieur au début de l’abonnement en cours', 'imagine-pilotage'),
                'choix' => [
                    'ferme' => __('Fermé au titre de l’abonnement (défaut)', 'imagine-pilotage'),
                    'ouvert' => __('Ouvert au titre de l’abonnement en cours', 'imagine-pilotage'),
                ],
            ],
        ];
    }
}
