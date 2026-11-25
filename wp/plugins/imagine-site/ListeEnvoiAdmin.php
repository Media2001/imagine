<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Écran natif et contrôleur d'export : capacité indépendante du nonce. */
final class ListeEnvoiAdmin
{
    public const CAP = 'imagine_exporter_liste_envoi';
    public const PAGE = 'imagine-liste-envoi';
    public const ACTION = 'imagine_exporter_liste_envoi';
    public const JOURNAL = 'imagine_envoi_export_journal_';

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || current_user_can(self::CAP);
    }

    private static function t(string $text): string
    {
        return __($text, 'imagine-site');
    }

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_envoi', 'imagine_envoi_groupes', ['type' => 'string', 'default' => 'ferme',
                'sanitize_callback' => static fn ($value): string => $value === 'liens_memberships' ? $value : 'ferme']);
        });
        add_action('admin_menu', [self::class, 'menu'], 100);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            // Woo redirige les rôles sans edit_posts/manage_woocommerce vers Mon compte.
            // Exception limitée à notre écran, pas un accès général au back-office.
            global $pagenow;
            $page = $_GET['page'] ?? '';
            return $pagenow === 'admin.php' && is_string($page)
                && in_array($page, ['imagine', self::PAGE], true) && self::autorise() ? false : $prevent;
        });
        add_action('admin_post_' . self::ACTION, [self::class, 'exporter']);
        add_action('admin_post_nopriv_' . self::ACTION, [self::class, 'exporter']);
    }

    public static function menu(): void
    {
        if (!self::autorise()) {
            return;
        }
        $cap = current_user_can('manage_options') ? 'manage_options' : self::CAP;
        // C10 garde son écran et sa capacité. Seul le parent visible du référent
        // est remplacé : aucun manage_options/manage_woocommerce n'est accordé.
        if (!current_user_can('manage_options')) {
            add_menu_page(
                self::t('Liste d’envoi'),
                self::t('Imagine'),
                $cap,
                'imagine',
                [self::class, 'page'],
                'dashicons-admin-settings'
            );
            remove_submenu_page('imagine', 'imagine');
        }
        add_submenu_page(
            'imagine',
            self::t('Liste d’envoi'),
            self::t('Liste d’envoi'),
            $cap,
            self::PAGE,
            [self::class, 'page']
        );
    }

    private static function verifier(): void
    {
        if (!self::autorise()) {
            wp_die(self::t('Accès réservé au Référent abonnements et aux administrateurs.'), '', ['response' => 403]);
        }
    }

    private static function numero(array $request): string
    {
        $value = $request['numero'] ?? '';
        if (!is_string($value) || !preg_match('/^[A-Za-z0-9_-]{1,80}$/D', $value)) {
            throw new \InvalidArgumentException('Numéro invalide.');
        }
        return $value;
    }

    public static function page(): void
    {
        self::verifier();
        nocache_headers();
        echo '<div class="wrap"><h1>' . esc_html(self::t('Liste d’envoi')) . '</h1>';
        if (current_user_can('manage_options')) {
            echo '<form method="post" action="' . esc_url(admin_url('options.php')) . '">';
            settings_fields('imagine_envoi');
            echo '<label for="imagine-envoi-groupes">' . esc_html(self::t('Groupes — à confirmer par Imagine')) . '</label> ';
            echo '<select id="imagine-envoi-groupes" name="imagine_envoi_groupes">';
            foreach (
                ['ferme' => self::t('Fermé (défaut prudent)'),
                'liens_memberships' => self::t('Attributions Memberships natives et capacité du produit')] as $value => $label
            ) {
                echo '<option value="' . esc_attr($value) . '"' . selected(
                    get_option('imagine_envoi_groupes', 'ferme'),
                    $value,
                    false
                ) . '>' . esc_html($label) . '</option>';
            }
            echo '</select><p>' . esc_html(self::t('Aucun statut actif ne remplace un paiement. Les places libres ne reçoivent rien. Les liens requis manquants ferment l’export.')) . '</p>';
            submit_button(self::t('Enregistrer la politique postale'));
            echo '</form>';
        }
        try {
            $calendar = EnvoiNatif::calendrier();
            $code = isset($_GET['numero']) ? self::numero($_GET) : '';
            if ($code === '') {
                $code = $calendar->numeros[0]->id ?? '';
                foreach ($calendar->numeros as $number) {
                    if ($number->cloture > new \DateTimeImmutable('now')) {
                        $code = $number->id;
                        break;
                    }
                }
            }
            $view = EnvoiNatif::apercu($code);
            echo '<form method="get" action="' . esc_url(admin_url('admin.php')) . '">';
            echo '<input type="hidden" name="page" value="' . esc_attr(self::PAGE) . '">';
            echo '<label for="imagine-envoi-numero">' . esc_html(self::t('Numéro et date de clôture')) . '</label> ';
            echo '<select id="imagine-envoi-numero" name="numero">';
            foreach ($calendar->numeros as $number) {
                echo '<option value="' . esc_attr($number->id) . '"' . selected($number->id, $code, false) . '>'
                    . esc_html($number->id . ' — ' . $number->cloture->format('Y-m-d')) . '</option>';
            }
            echo '</select> ';
            submit_button(self::t('Afficher'), 'secondary', '', false);
            echo '</form><h2>' . esc_html(self::t('Aperçu')) . '</h2>';
            echo '<p>' . esc_html(sprintf(self::t('Clôture : %s (Europe/Brussels).'), $view['liste']->cloture->format('Y-m-d H:i'))) . '</p>';
            echo '<p><strong>' . esc_html(sprintf(
                self::t('%d destinataires — Belgique : %d ; étranger : %d.'),
                count($view['liste']->lignes),
                $view['belgique'],
                $view['etranger']
            )) . '</strong></p>';
            echo '<p>' . esc_html($view['provisoire']
                ? self::t('Projection provisoire avant clôture, pas une liste finale. Les dates de fin connues sont prises en compte.')
                : self::t('Liste à la clôture : seuls les relevés observés avant la clôture sont utilisés.')) . '</p>';
            echo '<div class="notice notice-warning inline"><p>' . esc_html(self::t(
                'Démonstration hors ligne : aucun email, envoi postal ni paiement. '
                . 'Les profils C09 actifs n’ont pas de paiement validé ; leur statut actif seul ne justifie pas une expédition. '
                . 'Les bénéficiaires offerts/groupés absents du natif ne sont pas inventés.'
            )) . '</p></div>';
            if ($view['historique_incomplet']) {
                echo '<div class="notice notice-error inline"><p>' . esc_html(self::t('Historique antérieur manquant : export fermé, aucune reconstitution rétroactive.')) . '</p></div>';
            }
            echo '<h2>' . esc_html(self::t('Exclus et motifs')) . '</h2><table class="widefat striped"><thead><tr>';
            foreach ([self::t('Abonnement'), self::t('Destinataire'), self::t('Motif')] as $label) {
                echo '<th scope="col">' . esc_html($label) . '</th>';
            }
            echo '</tr></thead><tbody>';
            foreach ($view['exclus'] as $row) {
                echo '<tr><td>' . esc_html($row['abonnement_id']) . '</td><td>' . esc_html($row['destinataire'])
                    . '</td><td>' . esc_html(self::motif($row['motif'])) . '</td></tr>';
            }
            echo '</tbody></table>';
            if ($view['liste']->anomalies !== []) {
                echo '<h2>' . esc_html(self::t('Anomalies — export fermé')) . '</h2><ul>';
                foreach ($view['liste']->anomalies as $anomaly) {
                    echo '<li>' . esc_html(self::motif($anomaly['motif'])) . '</li>';
                }
                echo '</ul>';
            }
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
            echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION) . '">';
            echo '<input type="hidden" name="numero" value="' . esc_attr($code) . '">';
            wp_nonce_field(self::ACTION . ':' . $code);
            submit_button(
                $view['provisoire'] ? self::t('Exporter le CSV provisoire') : self::t('Exporter le CSV'),
                'primary',
                'submit',
                true,
                $view['historique_incomplet'] || $view['liste']->anomalies !== [] ? ['disabled' => 'disabled'] : []
            );
            echo '</form>';
        } catch (\Throwable) {
            echo '<div class="notice notice-error"><p>' . esc_html(self::t('Liste indisponible : vérifier le numéro, les données natives et le journal. Aucun CSV produit.')) . '</p></div>';
        }
        echo '<h2>' . esc_html(self::t('Journal des exports — cinquante derniers, sans purge')) . '</h2>';
        echo '<table class="widefat striped"><thead><tr>';
        foreach ([self::t('Qui'), self::t('Quand (UTC)'), self::t('Numéro'), self::t('Lignes'), self::t('État')] as $label) {
            echo '<th scope="col">' . esc_html($label) . '</th>';
        }
        echo '</tr></thead><tbody>';
        foreach (self::journal() as $event) {
            echo '<tr><td>' . esc_html($event['qui_login'] . ' (#' . $event['qui_id'] . ')')
                . '</td><td>' . esc_html($event['quand_utc']) . '</td><td>' . esc_html($event['numero'])
                . '</td><td>' . esc_html((string) $event['lignes']) . '</td><td>'
                . esc_html($event['provisoire'] ? self::t('Provisoire') : self::t('Clôturé')) . '</td></tr>';
        }
        echo '</tbody></table></div>';
    }

    public static function motif(string $reason): string
    {
        return self::t(match ($reason) {
            'expire' => 'Expiré à la clôture', 'suspendu' => 'Suspendu',
            'virement_non_valide' => 'Virement non validé', 'paiement_non_valide' => 'Paiement non validé',
            'numero_non_du' => 'Numéro non dû (C01)', 'cree_apres_cloture' => 'Créé après la clôture',
            'historique_indisponible' => 'Historique avant clôture indisponible',
            'non_eligible' => 'Non éligible à l’envoi',
            'beneficiaires_non_resolus' => 'Bénéficiaires requis non résolus (export fermé)',
            'calendrier_incomplet' => 'Calendrier incomplet (export fermé)',
            'adresse_incomplete' => 'Adresse incomplète', 'pays_manquant' => 'Pays manquant',
            'doublon_destinataire_adresse' => 'Deux exemplaires à la même adresse', default => $reason,
        });
    }

    public static function journal(): array
    {
        global $wpdb;
        return array_map('maybe_unserialize', $wpdb->get_col($wpdb->prepare(
            "SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id DESC LIMIT 50",
            $wpdb->esc_like(self::JOURNAL) . '%'
        )));
    }

    public static function preparer(string $code): string
    {
        self::verifier();
        $view = EnvoiNatif::apercu($code);
        if ($view['historique_incomplet']) {
            throw new \LogicException('Historique incomplet : export fermé.');
        }
        $csv = (new \Imagine\Pilotage\Envoi\AdministrationFormatExport())->exporter($view['liste']);
        $user = wp_get_current_user();
        $event = ['qui_id' => $user->ID, 'qui_login' => $user->user_login,
            'quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'numero' => $code,
            'lignes' => count($view['liste']->lignes), 'provisoire' => $view['provisoire']];
        $key = self::JOURNAL . str_replace('-', '', wp_generate_uuid4());
        if (!add_option($key, $event, '', false) || get_option($key) !== $event) {
            throw new \RuntimeException('Journal indisponible : export refusé.');
        }
        return $csv;
    }

    public static function exporter(): void
    {
        self::verifier();
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            header('Allow: POST');
            wp_die(self::t('Export sur demande POST uniquement.'), '', ['response' => 405]);
        }
        try {
            $code = self::numero($_POST);
        } catch (\Throwable) {
            wp_die(self::t('Numéro invalide.'), '', ['response' => 400]);
        }
        check_admin_referer(self::ACTION . ':' . $code);
        try {
            $csv = self::preparer($code);
        } catch (\Throwable) {
            wp_die(self::t('Export refusé : vérifier les données, les anomalies et le journal.'), '', ['response' => 409]);
        }
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        header('Content-Type: text/csv; charset=UTF-8');
        header('X-Content-Type-Options: nosniff');
        header('Content-Disposition: attachment; filename="liste-envoi-' . $code . '.csv"');
        echo $csv;
        exit;
    }
}
