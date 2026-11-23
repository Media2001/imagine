<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Administration;

use Imagine\Pilotage\Acces\AdministrationReglages as Acces;
use Imagine\Pilotage\Echeancier\ReglagesAdministration as Paiement;
use Imagine\Pilotage\Envoi\AdministrationFormatExport as Envoi;
use Imagine\Pilotage\Envoi\ExportCsv;

/** Façade administrative seule. Les moteurs ne sont ni étendus ni recopiés. */
final class Reglages
{
    public const GROUPE = 'imagine_reglages';
    public const PAGE = 'imagine-reglages';
    public const JOURNAL = 'imagine_reglages_journal_';
    private bool $restauration = false;

    /** État éditorial explicite ; passer une clé à false quand Imagine tranche. */
    private const REGLES_OUVERTES = [
        'contenu_futur' => true, 'pdf_robot' => true, 'pdf_anterieur_abonnement' => true,
        'marge_jours' => true, 'confirmation_premier_sepa' => true, 'apres_rejet' => true,
        'tarif' => true, 'colonnes' => true,
    ];

    public function brancher(): void
    {
        add_action('admin_menu', [$this, 'menu']);
        add_action('admin_init', [$this, 'enregistrer']);
        add_filter('option_page_capability_' . self::GROUPE, static fn (): string => 'manage_options');
        add_action('updated_option', [$this, 'journaliser'], 10, 3);
        add_action('added_option', [$this, 'ajouterAuJournal'], 10, 2);
    }

    public function options(): array
    {
        return [Acces::OPTION, Paiement::OPTION, Envoi::OPTION];
    }

    public function defauts(): array
    {
        return [
            Acces::OPTION => (new \Imagine\Pilotage\Acces\Reglages())->options(),
            Paiement::OPTION => (new Paiement())->defauts(),
            Envoi::OPTION => ExportCsv::COLONNES,
        ];
    }

    public function menu(): void
    {
        add_menu_page(
            self::t('Réglages Imagine'),
            self::t('Imagine'),
            'manage_options',
            'imagine',
            [$this, 'page'],
            'dashicons-admin-settings'
        );
        add_submenu_page(
            'imagine',
            self::t('Réglages Imagine'),
            self::t('Réglages'),
            'manage_options',
            self::PAGE,
            [$this, 'page']
        );
        // Slugs distincts : WordPress conserve le sous-menu unique « Réglages ».
        remove_submenu_page('imagine', 'imagine');
    }

    public function enregistrer(): void
    {
        foreach ($this->defauts() as $option => $defaut) {
            register_setting(self::GROUPE, $option, [
                'type' => 'array', 'default' => $defaut, 'show_in_rest' => false,
                'sanitize_callback' => match ($option) {
                    Acces::OPTION => [$this, 'nettoyerAcces'],
                    Paiement::OPTION => [$this, 'nettoyerPaiement'],
                    Envoi::OPTION => [new Envoi(), 'nettoyer'],
                },
            ]);
        }
    }

    /** Refuse les tableaux incomplets/surnuméraires, sans convertir une faute en fermeture. */
    public function nettoyerAcces(mixed $value): array
    {
        $choices = [
            'contenu_futur' => ['ferme_tous', 'equipe'],
            'pdf_robot' => ['extrait', 'complet'],
            'pdf_anterieur_abonnement' => ['ferme', 'ouvert'],
        ];
        if (!$this->clesExactes($value, array_keys($choices))) {
            return $this->refuser(Acces::OPTION);
        }
        foreach ($choices as $key => $allowed) {
            if (!in_array($value[$key], $allowed, true)) {
                return $this->refuser(Acces::OPTION);
            }
        }
        return (new Acces())->nettoyer($value);
    }

    public function nettoyerPaiement(mixed $value): mixed
    {
        if (!$this->clesExactes($value, array_keys($this->defauts()[Paiement::OPTION]))) {
            return $this->refuser(Paiement::OPTION);
        }
        return (new Paiement())->sanitiser($value);
    }

    private function clesExactes(mixed $value, array $keys): bool
    {
        return is_array($value) && count($value) === count($keys) && array_diff($keys, array_keys($value)) === [];
    }

    private function refuser(string $option): array
    {
        add_settings_error(
            $option,
            'imagine_valeur_refusee',
            self::t('Valeur invalide ou champ manquant : réglage refusé, ancienne valeur conservée.')
        );
        return get_option($option, $this->defauts()[$option]);
    }

    public function ajouterAuJournal(string $option, mixed $value): void
    {
        if (in_array($option, $this->options(), true)) {
            $this->journaliser($option, $this->defauts()[$option], $value, true);
        }
    }

    /** Après écriture effective : jamais dans un sanitizer, qui peut être appelé deux fois. */
    public function journaliser(string $option, mixed $before, mixed $after, bool $creation = false): void
    {
        if ($this->restauration || !in_array($option, $this->options(), true) || $before === $after) {
            return;
        }
        $user = wp_get_current_user();
        // Une option distincte par événement évite la perte d'un append concurrent.
        $written = add_option(self::JOURNAL . str_replace('-', '', wp_generate_uuid4()), [
            'quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID,
            'qui_login' => $user->ID ? $user->user_login : 'systeme',
            'option' => $option, 'avant' => $before, 'apres' => $after,
        ], '', false);
        if (!$written) {
            // Après persistance : annuler l'écriture métier, sans journal de restauration.
            $this->restauration = true;
            try {
                if ($creation) {
                    delete_option($option);
                } else {
                    update_option($option, $before);
                }
                if (get_option($option, $this->defauts()[$option]) !== $before) {
                    wp_die(
                        self::t('Échec du journal et de la restauration : vérifier les réglages.'),
                        '',
                        ['response' => 500]
                    );
                }
            } finally {
                $this->restauration = false;
            }
            add_settings_error(
                $option,
                'imagine_journal_indisponible',
                self::t('Modification refusée : le journal est indisponible, ancienne valeur conservée.')
            );
        }
    }

    public function journal(): array
    {
        global $wpdb;
        $like = $wpdb->esc_like(self::JOURNAL) . '%';
        $rows = $wpdb->get_col($wpdb->prepare(
            "SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id DESC LIMIT 50",
            $like
        ));
        return array_map('maybe_unserialize', $rows);
    }

    private static function t(string $text): string
    {
        return __($text, 'imagine-pilotage');
    }

    /** Métadonnées d'affichage seulement ; les validations métier restent dans les adaptateurs. */
    private function champs(): array
    {
        return [
            Acces::OPTION => [self::t('Accès'), [
                'contenu_futur' => [self::t('Contenus pas encore parus'),
                    self::t('Un abonné ne lit pas un numéro à venir. L’autre choix autorise seulement l’équipe.'),
                    self::t('Fermé pour tous, équipe comprise'),
                    ['ferme_tous' => self::t('Fermé pour tous'), 'equipe' => self::t('Ouvert à l’équipe uniquement')]],
                'pdf_robot' => [self::t('PDF pour les moteurs de recherche vérifiés'),
                    self::t('Détermine si un moteur vérifié reçoit le PDF complet ; '
                        . 'ne donne aucun droit à un visiteur ordinaire.'),
                    self::t('Extrait, sans PDF complet'),
                    ['extrait' => self::t('Extrait seulement'), 'complet' => self::t('PDF complet')]],
                'pdf_anterieur_abonnement' => [self::t('PDF parus avant l’abonnement'),
                    self::t('Un abonné en cours peut, ou non, ouvrir les PDF parus avant le début de son abonnement.'),
                    self::t('Fermé au titre de l’abonnement'),
                    ['ferme' => self::t('Fermé'), 'ouvert' => self::t('Ouvert')]],
            ]],
            Paiement::OPTION => [self::t('Paiement en quatre fois'), [
                'marge_jours' => [self::t('Marge avant clôture (jours civils)'),
                    self::t('Sans marge renseignée, le moteur refuse de planifier les échéances. '
                        . 'Aucune valeur n’est devinée.'),
                    self::t('Vide : planification refusée'), null],
                'confirmation_premier_sepa' => [self::t('Confirmation du premier paiement SEPA'),
                    self::t('Avec marge : le premier numéro n’est considéré payé qu’après la confirmation effective '
                        . 'et la marge après commande. Sans marge : seule la confirmation compte. '
                        . 'Aucune opération bancaire ici.'),
                    self::t('Avec marge'),
                    ['avec_marge' => self::t('Appliquer la marge'), 'sans_marge' => self::t('Sans marge')]],
                'apres_rejet' => [self::t('Échéances restantes après un rejet'),
                    self::t('Choisit si les autres échéances du bloc restent dues. '
                        . 'Ne rétablit pas l’accès suspendu et n’envoie aucun prélèvement.'),
                    self::t('Les échéances restent dues'),
                    ['restent_dues' => self::t('Restent dues'),
                        'annuler_restantes' => self::t('Ne sont plus dues après rejet')]],
                'tarif' => [self::t('Tarif des échéances non payées'),
                    self::t('L’abonné conserve les montants du bloc, '
                        . 'ou les échéances non payées suivent le tarif courant. '
                        . 'Les paiements déjà reçus ne changent pas.'),
                    self::t('Montants figés pour le bloc de quatre numéros'),
                    ['fige_bloc' => self::t('Figé pour le bloc'),
                        'courant_impayes' => self::t('Tarif courant pour les impayées')]],
            ]],
            Envoi::OPTION => [self::t('Liste d’envoi'), [
                'colonnes' => [self::t('Colonnes du fichier postal, dans l’ordre'),
                    self::t('Choisit les informations et leur ordre dans le CSV envoyé au routeur, '
                        . 'sans changer les destinataires ni leurs droits. Une colonne par ligne, sans doublon.'),
                    implode(', ', ExportCsv::COLONNES), 'textarea'],
            ]],
        ];
    }

    public function page(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(self::t('Accès réservé aux administrateurs.'), '', ['response' => 403]);
        }
        $values = [Acces::OPTION => (new Acces())->lire()->options(),
            Paiement::OPTION => (new Paiement())->options((new Paiement())->lire()),
            Envoi::OPTION => (new Envoi())->lire()->colonnes];
        echo '<div class="wrap"><h1>' . esc_html(self::t('Réglages Imagine')) . '</h1>';
        settings_errors();
        echo '<p>' . esc_html(self::t('Règles provisoires à valider avec Imagine. '
            . 'Enregistrer ne lance ni paiement, ni email, ni envoi postal.')) . '</p>';
        echo '<form method="post" action="options.php">';
        settings_fields(self::GROUPE);
        foreach ($this->champs() as $option => [$title, $fields]) {
            echo '<h2>' . esc_html($title) . '</h2>';
            if ($option === Acces::OPTION) {
                echo '<p>' . esc_html(self::t(
                    'Ces trois réglages sont lus par le paywall. '
                    . 'Le choix sur les contenus futurs agit sur les articles ; '
                    . 'les deux choix PDF gouvernent la décision PDF, sans livrer ici un téléchargement protégé.'
                )) . '</p>';
            } elseif ($option === Paiement::OPTION) {
                echo '<p>' . esc_html(self::t(
                    'Ces valeurs sont conservées pour un branchement futur et ne modifient pas encore le paiement '
                    . 'du site de démonstration.'
                )) . '</p>';
            }
            echo '<table class="form-table" role="presentation">';
            foreach ($fields as $key => [$label, $help, $default, $choices]) {
                $id = 'imagine-' . $key;
                $description = $id . '-aide';
                echo '<tr class="imagine-reglage"><th scope="row"><label for="' . esc_attr($id) . '">'
                    . esc_html($label) . '</label></th><td>';
                $name = $option === Envoi::OPTION ? $option : $option . '[' . $key . ']';
                $value = $option === Envoi::OPTION ? $values[$option] : ($values[$option][$key] ?? '');
                $attrs = ' id="' . esc_attr($id) . '" name="' . esc_attr($name)
                    . '" aria-describedby="' . esc_attr($description) . '"';
                if ($choices === 'textarea') {
                    echo '<textarea class="large-text code" rows="9"' . $attrs . '>'
                        . esc_textarea(implode("\n", $value)) . '</textarea>';
                } elseif (is_array($choices)) {
                    echo '<select' . $attrs . '>';
                    foreach ($choices as $choice => $text) {
                        echo '<option value="' . esc_attr($choice) . '"' . selected($value, $choice, false)
                            . '>' . esc_html($text) . '</option>';
                    }
                    echo '</select>';
                } else {
                    echo '<input type="number" min="1" step="1" class="small-text"' . $attrs
                        . ' value="' . esc_attr((string) $value) . '">';
                }
                echo '<p class="description" id="' . esc_attr($description) . '">' . esc_html($help)
                    . '<br>' . esc_html(self::t('Défaut : ')) . esc_html($default)
                    . (self::REGLES_OUVERTES[$key]
                        ? '<br><strong>' . esc_html(self::t('À confirmer par Imagine')) . '</strong>' : '')
                    . '</p></td></tr>';
            }
            echo '</table>';
        }
        submit_button(self::t('Enregistrer les réglages'));
        echo '</form>';
        if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo') {
            echo '<h2>' . esc_html(self::t('Aperçu CSV fictif — effet du réglage Liste d’envoi')) . '</h2><p>'
                . esc_html(self::t('Le véritable exporteur C07 produit cet exemple local après chaque enregistrement. '
                    . 'Aucun fichier n’est transmis.')) . '</p><pre id="imagine-csv-apercu">'
                . esc_html($this->apercuCsv()) . '</pre>';
        }
        echo '<h2>' . esc_html(self::t('Journal des modifications')) . '</h2><p>'
            . esc_html(self::t('Les 50 derniers changements sont affichés. '
                . 'Tous les événements sont conservés. Dates en UTC.')) . '</p>';
        echo '<table class="widefat striped"><thead><tr>';
        foreach (['Quand (UTC)', 'Qui', 'Réglage', 'Avant', 'Après'] as $text) {
            echo '<th scope="col">' . esc_html(self::t($text)) . '</th>';
        }
        echo '</tr></thead><tbody>';
        foreach ($this->journal() as $row) {
            echo '<tr>';
            foreach (
                [$row['quand_utc'], $row['qui_login'] . ' (#' . $row['qui_id'] . ')',
                $row['option'], wp_json_encode($row['avant'], JSON_UNESCAPED_UNICODE),
                wp_json_encode($row['apres'], JSON_UNESCAPED_UNICODE)] as $cell
            ) {
                echo '<td>' . esc_html((string) $cell) . '</td>';
            }
            echo '</tr>';
        }
        echo '</tbody></table></div>';
    }

    /** Raccord de démonstration au véritable moteur CSV, pas une imitation du format. */
    public function apercuCsv(): string
    {
        $line = array_fill_keys(ExportCsv::COLONNES, '');
        $line = array_replace($line, ['abonnement_id' => 'C10-FICTIF', 'destinataire_id' => 'C10-DEMO',
            'destinataire' => 'Lectrice Fictive C10', 'rue' => '1 rue Imaginaire',
            'code_postal' => '0000', 'ville' => 'Ville Fictive', 'pays' => 'BE', 'origine' => 'demo']);
        return ExportCsv::lignes([$line], (new Envoi())->lire());
    }
}
